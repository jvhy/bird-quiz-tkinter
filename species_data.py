import requests
import yaml
import pandas as pd
from quiz import BirdSound, MysterySpecies, SpeciesList
import re


def get_species() -> pd.DataFrame:
    """
    Fetches the list of bird species observed in Finland from eBird API, and then fetches
    the scientific and common Finnish names of each species from the eBird API.
    Finally, the list of species are filtered to only include birds that nest in Finland
    using the nesting species information from Lintuatlas 3.

    :return species_df: dataframe containing bird species that nest in Finland
    """

    with open("utils/config.yaml", "r") as f:
        api_key = yaml.load(f, Loader=yaml.Loader).get("api_key")
    headers = {"X-eBirdApiToken": api_key}
    species_endpoint = "https://api.ebird.org/v2/product/spplist/FI"
    species_response = requests.get(species_endpoint, headers=headers)
    species_list = species_response.json()

    species_list = [species for species in species_list if not species.startswith("x")]  # remove hybrid species

    taxonomy_endpoint = "https://api.ebird.org/v2/ref/taxonomy/ebird"
    taxonomy_params = \
        {
            "fmt": "json",
            "locale": "fi",
            "species": ",".join(species_list)
         }
    taxonomy_response = requests.get(taxonomy_endpoint, headers=headers, params=taxonomy_params)
    base_species_list = taxonomy_response.json()
    base_species_list = [sp for sp in base_species_list if " " not in sp["comName"]]  # gets rid of non-Finnish names
    base_species_names = [(sp["sciName"], sp["comName"]) for sp in base_species_list]
    base_species_df = pd.DataFrame(base_species_names, columns=["sciName", "comName"])

    atlas_df = pd.read_csv("data/atlasdata.csv")
    species_df = atlas_df.merge(base_species_df, how="left", on="comName")  # results in a df with nesting species only
    species_df.loc[species_df["comName"] == "kesykyyhky", "sciName"] = "Columba livia"  # fix an exception in names

    return species_df


def get_recordings(species_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetches all bird sound recordings from the Xeno-Canto API from 5 countries
    and filters them to only include the species that nest in Finland.

    :param species_df: dataframe containing bird species that nest in Finland
    :return recording_df: dataframe of bird sound recordings
    """

    all_recordings = []

    endpoint = "https://xeno-canto.org/api/2/recordings"

    for country in ["finland", "sweden", "norway", "denmark", "estonia"]:
        current_page = 1
        more_pages = True
        params = {"query": f'grp:birds cnt:{country} q:A', "page": current_page}

        while more_pages:
            r = requests.get(url=endpoint, params=params).json()
            data = r.get("recordings")
            all_recordings.extend(data)

            total_pages = r.get("numPages")
            if total_pages == current_page:
                more_pages = False
            else:
                current_page += 1
                params["page"] = current_page

    recording_df = pd.DataFrame(all_recordings)
    recording_df["sciName"] = recording_df["gen"] + " " + recording_df["sp"]
    recording_df = recording_df.loc[recording_df["sciName"].isin(species_df["sciName"].unique())]
    recording_df = recording_df.dropna(subset=["id", "url", "file", "rec", "lic"])
    recording_df = recording_df.merge(species_df, how="left", on="sciName")

    return recording_df


def extract_license_type(license_url: str) -> str:
    """
    Reformats the Creative Commons license URL of a sound recording to the name of the license for display purposes.

    :param license_url: URL to the CC license type page
    :return license_type: name of the CC license type
    """

    m = re.match(r"//creativecommons.org/licenses/([a-z-]+)/(\d\.\d)/", license_url)
    if m:
        license_type = f"CC {m.group(1).upper()} {m.group(2)}"
    else:
        license_type = None
    return license_type


def reformat_recordings(recording_df: pd.DataFrame) -> SpeciesList:
    """
    Reformats the dataframe of bird sound recordings to a SpeciesList that contains MysterySpecies objects.

    :param recording_df: dataframe of bird sound recordings
    :return species_list: SpeciesList object containing all nesting species in Finland.
    """

    recording_df["lic"] = recording_df["lic"].map(extract_license_type)
    species_list = []
    for species in recording_df["sciName"].unique():
        subdf = recording_df.loc[recording_df["sciName"] == species]
        species_sounds = [BirdSound(*values) for values in subdf[["id", "url", "file", "rec", "cnt", "loc", "type", "lic"]].values]
        mystery_species = MysterySpecies(common_name_FI=subdf["comName"].values[0],
                                         common_name_EN=subdf["en"].values[0],
                                         scientific_name=species,
                                         sounds=species_sounds,
                                         square_count=subdf["atlasSquareCount"].values[0])
        species_list.append(mystery_species)

    species_list = SpeciesList(species_list)

    return species_list
