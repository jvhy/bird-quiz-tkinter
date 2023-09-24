import tkinter as tk
from tkinter import messagebox

window_width = 850
window_height = 530


class QuizApp(tk.Tk):
    def __init__(self, quiz, quiz_species):
        tk.Tk.__init__(self)
        self.title("Laillinen Lintupeli")
        self.geometry(f"{window_width}x{window_height}")
        self.quiz = quiz
        self.quiz_species = quiz_species

        self.grid_columnconfigure(0, weight=29)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=99)

        self.display_title()
        self.display_quit_button()
        self._frame = None
        self.switch_frame(StartPage)

    def display_title(self):
        title = tk.Label(self, text="Bird Quiz", bg="green", fg="white", font=("ariel", 20, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="new")

    def display_quit_button(self):
        quit_button = tk.Button(
            self, command=self.destroy,
            width=5, bg="red", fg="red",
            text="Quit", font=("ariel", 16, " bold"))
        quit_button.grid(row=1, column=1, sticky="ne", pady=10, padx=10)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid(row=2, column=0, columnspan=2, sticky="nsew")


class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        welcome_text = tk.Label(self, text="Welcome to Bird Quiz!", font=("ariel", 30, "bold"))
        welcome_text.grid(row=0, column=0, sticky="nsew")

        self.selected_difficulty = tk.IntVar()
        self.selected_quiz_length = tk.IntVar()
        self.wildcard_entry = tk.StringVar()

        self.options = self.options_box()
        self.options.grid(row=1, column=0, sticky="nsew")

        play_button = tk.Button(
            self, command=self.start_quiz,
            height=3, width=10,
            fg="green",
            text="PLAY GAME", font=("ariel", 25, "bold"))
        play_button.grid(row=2, column=0, sticky="n")

    def options_box(self):
        options_box = tk.Frame(self)
        options_box.grid_columnconfigure((0, 1), weight=1)
        options_box.grid_rowconfigure((0, 1, 2), weight=1)

        diff_text = tk.Label(options_box, text="Difficulty:", font=("ariel", 15))
        diff_text.grid(row=0, column=0, sticky="nse")
        diff_option_frame = tk.Frame(options_box)
        diff_option_frame.grid_columnconfigure((0, 1, 2), weight=1)
        diff_option_frame.grid_rowconfigure(0, weight=1)
        diff_option_frame.grid(row=0, column=1, sticky="nsw")
        diff_slider = tk.Scale(options_box, variable=self.selected_difficulty, from_=1, to=5, orient=tk.HORIZONTAL)
        diff_slider.grid(row=0, column=1, sticky="nsw")

        len_text = tk.Label(options_box, text="Quiz length:", font=("ariel", 15))
        len_text.grid(row=1, column=0, sticky="nse")
        len_option_frame = tk.Frame(options_box)
        len_option_frame.grid_columnconfigure((0, 1, 2), weight=1)
        len_option_frame.grid_rowconfigure(0, weight=1)
        len_option_frame.grid(row=1, column=1, sticky="nsw")
        len_slider = tk.Scale(options_box, variable=self.selected_quiz_length, from_=10, to=30, resolution=5, orient=tk.HORIZONTAL)
        len_slider.grid(row=1, column=1, sticky="nsw")

        filter_text = tk.Label(options_box, text="Species filter:", font=("ariel", 15))
        filter_text.grid(row=2, column=0, sticky="nse")
        filter_bar = tk.Entry(options_box, textvariable=self.wildcard_entry)
        filter_bar.grid(row=2, column=1, sticky="w")

        return options_box

    def start_quiz(self):
        self.master.quiz.difficulty_level = self.selected_difficulty.get()
        self.master.quiz.quiz_length = self.selected_quiz_length.get()
        self.master.quiz.wildcard_pattern = self.wildcard_entry.get()
        print("Starting new quiz")
        print("Difficulty:", self.master.quiz.difficulty_level)
        print("Length:", self.master.quiz.quiz_length)
        print("Wildcard pattern:", self.master.quiz.wildcard_pattern)
        print()
        self.master.switch_frame(QuizPage)


class QuizPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.quiz = self.master.quiz
        self.grid_columnconfigure(0, weight=1, minsize=window_width / 4)
        self.grid_columnconfigure(1, weight=2, minsize=window_width / 2)
        self.grid_columnconfigure(2, weight=1, minsize=window_width / 4)

        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=2)

        self.quiz_species = self.master.quiz_species
        self.quiz.set_species_list(self.quiz_species)

        self.quiz.difficulty_filter()
        self.quiz.wildcard_filter()
        self.quiz.length_filter()

        self.quiz.next_species()
        self.button_frame = tk.Frame(self, background="lightgrey")
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1, minsize=window_width / 2 / 4)
        self.button_frame.grid_columnconfigure(1, weight=4, minsize=window_width / 2 / 4 * 3)
        self.button_frame.grid(row=0, column=1, sticky="nsew")

        self.sound_info = tk.Label(self.button_frame, background="lightgrey", text=self.get_recording_info_str(),
                                   justify="left", anchor="w")
        self.sound_info.grid(row=0, column=1, sticky="nsew")

        self.play_pause_button = tk.Button(self.button_frame, text="\u25BA", width=3, height=3,
                                           font=("ariel", 20, "bold"),
                                           command=self.play_pause, pady=0, padx=0, background="lightgrey")
        self.play_pause_button.grid(row=0, column=0)

        self.user_answer = tk.StringVar()
        self.bar = tk.Entry(self, textvariable=self.user_answer, highlightbackground="white")
        self.bar.grid(row=1, column=1, sticky="n")
        self.bar.bind("<Return>", lambda event: self.submit_button())
        self.bar.focus_set()

        self.next_button = tk.Button(self, text="submit", command=self.submit_button,
                                     width=8, bg="green", fg="green", font=("ariel", 16, "bold"))
        self.next_button.grid(row=1, column=1, sticky="n", pady=40)

        self.feedback = tk.Label(self, font=("ariel", 15, "bold"))
        self.feedback.grid(row=1, column=2, sticky="nw")

        self.past_answers = tk.Label(self, text="", anchor="ne", justify="left", font=("ariel", 14))
        self.past_answers.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=10)
        self.past_answer_symbols = tk.Label(self, text="", anchor="ne", justify="left", font=("ariel", 14))
        self.past_answer_symbols.grid(row=0, column=0, rowspan=2, sticky="nse", padx=50)

    def submit_button(self):
        self.quiz.current_species.stop_current_sound()
        self.play_pause_button.configure(text="\u25BA")

        normalized_answer = self.user_answer.get().lower().strip()
        if self.quiz.check_answer(normalized_answer):
            self.feedback["fg"] = "green"
            self.feedback["text"] = ('\U0001F44D Yay! \n'
                                     'Correct answer!')
        else:
            self.feedback['fg'] = 'red'
            self.feedback['text'] = ('\u274E Oops! \n'
                                     f'The right answer is:\n{self.quiz.current_species.correct_answers["comNameFI"]}')

        self.update_past_answers()
        self.clear_text()
        if self.quiz.has_more_species():
            self.quiz.next_species()
            self.update_sound_info()
        else:
            self.bar.destroy()
            self.next_button.destroy()
            self.display_results_button()

    def play_pause(self):
        if self.quiz.current_species.current_sound.is_playing():
            self.quiz.current_species.stop_current_sound()
            self.play_pause_button.configure(text="\u25BA")

        else:
            self.quiz.current_species.play_current_sound()
            self.play_pause_button.configure(text="\u25FE")

    def display_result(self):
        correct, wrong, score_percent = self.quiz.get_score()

        correct = f"Correct: {correct}"
        wrong = f"Wrong: {wrong}"
        result = f"Score: {score_percent}%"

        messagebox.showinfo("Result", f"{result}\n{correct}\n{wrong}")
        self.master.destroy()

    def display_results_button(self):
        results_button = tk.Button(self, text="Show results", command=self.display_result,
                                   width=15, bg="green", fg="green", font=("ariel", 16, "bold"))
        results_button.grid(row=1, column=1, sticky="n", pady=40)

    def clear_text(self):
        self.bar.delete(0, 'end')

    def update_past_answers(self):
        past_answers = self.quiz.answers
        user_answers = [ans["correct_answers"][0] for ans in past_answers]
        symbols = ["\u2705" if ans["answered_correctly"] else '\u274C' for ans in past_answers]
        self.past_answer_symbols.config(text="\n".join(symbols))
        self.past_answers.config(text="\n".join(user_answers))

    def update_sound_info(self):
        self.sound_info.configure(text=self.get_recording_info_str())

    def get_recording_info_str(self):
        info_str = "\n".join(
            ["xeno-canto " + self.quiz.current_species.current_sound.xc_id,
             self.quiz.current_species.current_sound.recordist,
             self.quiz.current_species.current_sound.location,
             self.quiz.current_species.current_sound.country,
             self.quiz.current_species.current_sound.license_type]
        )
        return info_str
