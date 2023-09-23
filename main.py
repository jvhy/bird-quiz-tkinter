from species_data import get_species, get_recordings, reformat_recordings
from quiz import Quiz
from ui import QuizApp
import pandas as pd


species_df = get_species()
recordings = get_recordings(species_df)
quiz_species = reformat_recordings(recordings)

quiz_brain = Quiz()
quiz_app = QuizApp(quiz=quiz_brain, quiz_species=quiz_species)
quiz_app.mainloop()
