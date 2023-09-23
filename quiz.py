import requests
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
from simpleaudio import stop_all
import random
import re
import requests


class BirdSound:
    def __init__(self,
                 xc_id: int,
                 url: str,
                 download_url: str,
                 recordist: str,
                 country: str,
                 location: str,
                 sound_type: str,
                 license_type: str):
        self.xc_id = f"XC{xc_id}"
        self.url = url
        self.download_url = download_url
        self.recordist = recordist
        self.country = country
        self.location = location
        self.sound_type = sound_type
        self.license_type = license_type
        self.sound = None
        self.playback = None

    def download_sound_file(self):
        sound_data = requests.get(self.download_url).content
        sound_file = AudioSegment.from_file(BytesIO(sound_data))[:15000]  # first 15 seconds of the file
        self.sound = sound_file

    def play_sound(self):
        self.playback = _play_with_simpleaudio(self.sound)

    def stop_sound(self):
        if self.playback:
            stop_all()

    def is_playing(self):
        if self.playback:
            return self.playback.is_playing()
        else:
            return False


class MysterySpecies:
    def __init__(self, common_name_FI: str, common_name_EN: str, scientific_name: str, sounds: [], square_count: int):
        self.correct_answers = {
            "comNameFI": common_name_FI.lower().strip(),
            "comNameEN": common_name_EN.lower().strip(),
            "sciName": scientific_name.lower().strip()
        }
        self.square_count = square_count
        self.sounds = sounds
        self.current_sound = None

    def set_current_sound(self):
        successful_download = False
        while not successful_download:
            random_sound_idx = random.choice(range(len(self.sounds)))
            random_sound = self.sounds[random_sound_idx]
            try:
                random_sound.download_sound_file()
            except requests.exceptions.MissingSchema:
                print("Download failed...")
                self.sounds.pop(random_sound_idx)
                continue
            self.current_sound = random_sound
            successful_download = True

    def play_current_sound(self):
        if self.current_sound:
            try:
                self.current_sound.play_sound()
            except ValueError:
                print("Error playing sound")
                self.set_current_sound()
                self.play_current_sound()

    def stop_current_sound(self):
        if self.current_sound:
            self.current_sound.stop_sound()


class SpeciesList(object):
    def __init__(self, full_species_list: []):
        self.full_species_list = full_species_list
        self.current_species_list = full_species_list
        self._data_len = len(self.current_species_list)

    def __iter__(self):
        for elem in self.current_species_list:
            yield elem

    def __getitem__(self, item):
        return self.current_species_list[item]

    def __len__(self):
        return self._data_len


class Quiz:
    def __init__(self):
        self.mystery_species_list = None
        self.current_species = None
        self.species_no = 0
        self.score = 0
        self.answers = []
        self.difficulty_level = 1
        self.quiz_length = 10
        self.wildcard_pattern = None

    def set_species_list(self, species_list):
        self.mystery_species_list = species_list

    def set_difficulty_level(self, level: int):
        self.difficulty_level = level

    def set_quiz_length(self, length: int):
        self.quiz_length = length

    def set_wildcard_filter(self, pattern: str):
        self.wildcard_pattern = pattern

    def wildcard_filter(self):
        if self.wildcard_pattern:
            regex_pattern = re.compile(rf'^{self.wildcard_pattern.replace("*", ".*")}$')
            matched_species_list = [sp for sp in self.mystery_species_list
                                    if regex_pattern.match(sp.correct_answers["comNameFI"])]
            if len(matched_species_list) > 0:
                self.mystery_species_list = matched_species_list

    def length_filter(self):
        random_species = random.sample(self.mystery_species_list, min(len(self.mystery_species_list), self.quiz_length))
        self.mystery_species_list = random_species

    def difficulty_filter(self):
        """
        Difficulty level limits the species in the quiz to the n most common species by Atlas square count:
            Level 1 -> 50 most common
            Level 2 -> 150 most common
            Level 3 -> All species
        """

        min_square_count_ranks = {1: 50, 2: 150, 3: len(self.mystery_species_list)}
        no_of_species = min_square_count_ranks[self.difficulty_level]
        self.mystery_species_list = sorted(self.mystery_species_list, key=lambda x: x.square_count, reverse=True)[:no_of_species]
        random.shuffle(self.mystery_species_list)

    def has_more_species(self):
        return self.species_no < len(self.mystery_species_list)

    def next_species(self):
        self.current_species = self.mystery_species_list[self.species_no]
        self.species_no += 1
        self.current_species.set_current_sound()
        species_sound = self.current_species.current_sound
        print(species_sound.xc_id)

        return species_sound

    def check_answer(self, user_answer):
        correct_answers = list(self.current_species.correct_answers.values())
        if user_answer in correct_answers:
            self.score += 1
            correct = True
        else:
            correct = False
        self.answers.append(
            {"user_answer": user_answer,
             "correct_answers": correct_answers,
             "answered_correctly": correct
             }
        )
        return correct

    def get_score(self):
        wrong = self.species_no - self.score
        score_percent = int(self.score / self.species_no * 100)
        return self.score, wrong, score_percent
