"""Tests for the game loop in trivia.cli, driven with scripted input."""

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest

from trivia import cli
from trivia.game import Question
from tests.helpers import (Script, history_question, medium_science_question,
                           no_shuffle, sample_bank, sample_questions)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.join(PROJECT_ROOT, "trivia")

# sample_bank() menu: 1) Science, 2) History, 3) Sports (no questions),
# 4) High Scores (R23).
SCIENCE, HISTORY, SPORTS, HIGH_SCORES = "1", "2", "3", "4"
# Difficulty menu: 1) Easy, 2) Medium, 3) Hard, 4) Back to categories.
EASY, MEDIUM, HARD, BACK = "1", "2", "3", "4"
# Answers to the Science Easy questions (sample_questions()): B, C, A
ALL_RIGHT = ("B", "C", "A")
MENU_PROMPT = "Category (1-4): "
# Typed at the name prompt after every completed game (R19).
NAME = "Ann"
NAME_PROMPT = "Enter your name for the high scores: "
DIFFICULTY_PROMPT = "Difficulty (1-4): "


def run_bundled_game(scores_path):
    """Run ``python3 -m trivia`` on the bundled questions with a temporary
    high-score file. Prompt order: category 1, Easy, then "A" for every
    answer; the first "A" left over is taken as the name (R19) and the rest
    are rejected by the play-again prompt until "n"."""
    stdin = "1\n1\n" + "A\n" * 200 + "n\n"
    return subprocess.run(
        [sys.executable, "-m", "trivia", "--scores", scores_path],
        input=stdin, capture_output=True, text=True, cwd=PROJECT_ROOT,
        timeout=30,
    )


def run_game(*lines, scores_path=None):
    """Run the whole game on sample_bank(); lines start with a category and a
    difficulty choice, and a completed game needs a name before the
    play-again reply. With no ``scores_path`` high scores stay in memory."""
    script = Script(*lines)
    code = cli.run(sample_bank(), script.input_fn, script.output_fn,
                   shuffle=no_shuffle, scores_path=scores_path)
    return script, code


class TestR1OneCommandNoNetwork(unittest.TestCase):
    def test_R1_package_imports_only_standard_library(self):
        allowed = set(sys.stdlib_module_names) | {"trivia"}
        for name in os.listdir(PACKAGE_DIR):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(PACKAGE_DIR, name), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    modules = [node.module]
                else:
                    continue
                for module in modules:
                    self.assertIn(module.split(".")[0], allowed,
                                  f"{name} imports non-stdlib {module}")

    def test_R1_package_does_not_use_network_modules(self):
        network = {"socket", "urllib", "http", "ssl", "ftplib", "smtplib"}
        for name in os.listdir(PACKAGE_DIR):
            if name.endswith(".py"):
                with open(os.path.join(PACKAGE_DIR, name), encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        names = ([a.name for a in node.names]
                                 if isinstance(node, ast.Import) else [node.module or ""])
                        for n in names:
                            self.assertNotIn(n.split(".")[0], network, name)

    def test_R1_python_m_trivia_runs_a_full_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_bundled_game(os.path.join(tmp, "scores.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Final score:", result.stdout)
        self.assertIn("Goodbye!", result.stdout)

    def test_R1_bad_question_file_exits_nonzero_without_traceback(self):
        script = Script()
        code = cli.main(["--questions", "/nonexistent/q.json"],
                        script.input_fn, script.output_fn)
        self.assertNotEqual(code, 0)
        self.assertIn("Could not load questions", script.text)


class TestR2DisplaysQuestions(unittest.TestCase):
    def test_R2_each_question_and_its_choices_are_shown(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        for q in sample_questions():
            self.assertIn(q.text, script.text)
            for letter, choice in zip("ABCD", q.choices):
                self.assertIn(f"{letter}) {choice}", script.text)


class TestR3TypedLetter(unittest.TestCase):
    def test_R3_lowercase_letters_are_accepted_in_game(self):
        script, _ = run_game(SCIENCE, EASY, "b", "c", "a", NAME, "n")
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)

    def test_R3_invalid_letter_reprompts_same_question(self):
        script, _ = run_game(SCIENCE, EASY, "E", "", "B", "C", "A", NAME, "n")
        self.assertEqual(script.text.count("Please type A, B, C, or D."), 2)
        self.assertEqual(script.text.count("What is 2 + 2?"), 1)
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)


class TestR4Feedback(unittest.TestCase):
    def test_R4_game_reports_correct_and_incorrect(self):
        script, _ = run_game(SCIENCE, EASY, "B", "A", "A", NAME, "n")
        self.assertEqual(script.text.count("Correct!"), 2)
        self.assertIn("Incorrect. The correct answer was C) Mars.", script.text)


class TestR5Score(unittest.TestCase):
    def test_R5_running_score_shown_after_each_answer(self):
        script, _ = run_game(SCIENCE, EASY, "B", "A", "A", NAME, "n")
        running = [line for line in script.output if line.startswith("Score:")]
        self.assertEqual(running, ["Score: 1 point (1 of 1 correct)",
                                   "Score: 1 point (1 of 2 correct)",
                                   "Score: 2 points (2 of 3 correct)"])

    def test_R5_wrong_first_answer_shows_zero_points(self):
        script, _ = run_game(SCIENCE, EASY, "A", "C", "A", NAME, "n")
        self.assertIn("Score: 0 points (0 of 1 correct)", script.output)

    def test_R5_easy_correct_answer_earns_1_point(self):
        script, _ = run_game(HISTORY, EASY, "B", NAME, "n")
        self.assertIn("Score: 1 point (1 of 1 correct)", script.output)

    def test_R5_medium_correct_answer_earns_3_points(self):
        script, _ = run_game(SCIENCE, MEDIUM, "D", NAME, "n")
        self.assertIn("Score: 3 points (1 of 1 correct)", script.output)

    def test_R5_hard_correct_answers_earn_5_points_each(self):
        hard = [Question("Hard one?", ["W", "X", "Y", "Z"], 0, "Science", "Hard"),
                Question("Hard two?", ["W", "X", "Y", "Z"], 1, "Science", "Hard")]
        script = Script("A", "B")
        cli.play_round(hard, "Science", "Hard", script.input_fn, script.output_fn)
        self.assertIn("Score: 5 points (1 of 1 correct)", script.output)
        self.assertIn("Score: 10 points (2 of 2 correct)", script.output)

    def test_R5_incorrect_answer_earns_no_points(self):
        script, _ = run_game(SCIENCE, MEDIUM, "A", NAME, "n")
        self.assertIn("Score: 0 points (0 of 1 correct)", script.output)

    def test_R5_play_round_returns_score(self):
        script = Script("A", "C", "D")
        score = cli.play_round(sample_questions(), "Science", "Easy",
                               script.input_fn, script.output_fn)
        self.assertEqual((score.points, score.correct, score.answered), (1, 1, 3))

    def test_R5_play_again_resets_points(self):
        script, _ = run_game(SCIENCE, MEDIUM, "D", NAME, "y", SCIENCE, MEDIUM, "D", NAME, "n")
        self.assertEqual(
            script.output.count("Final score: 3 points (1 of 1 correct)."), 2)
        self.assertNotIn("6 points", script.text)


class TestR6FinalScoreShown(unittest.TestCase):
    def test_R6_final_score_shown_after_last_question(self):
        script, _ = run_game(SCIENCE, EASY, "A", "A", "A", NAME, "n")
        final = [i for i, line in enumerate(script.output)
                 if line == "Final score: 1 point (1 of 3 correct)."]
        last_feedback = max(i for i, line in enumerate(script.output)
                            if line.startswith(("Correct!", "Incorrect.")))
        self.assertEqual(len(final), 1)
        self.assertGreater(final[0], last_feedback)

    def test_R6_final_score_shows_points_and_correct_count(self):
        script, _ = run_game(SCIENCE, MEDIUM, "D", NAME, "n")
        self.assertIn("Final score: 3 points (1 of 1 correct).", script.output)

    def test_R6_final_score_with_no_correct_answers(self):
        script, _ = run_game(SCIENCE, EASY, "A", "A", "B", NAME, "n")
        self.assertIn("Final score: 0 points (0 of 3 correct).", script.output)

    def test_R6_bundled_game_final_score_uses_points_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_bundled_game(os.path.join(tmp, "scores.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout,
                         r"Final score: (1 point|\d+ points) \(\d+ of \d+ correct\)\.")


class TestR7PlayAgain(unittest.TestCase):
    def test_R7_yes_starts_new_round_with_reset_score(self):
        script, code = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "y",
                                SCIENCE, EASY, "A", "A", "A", NAME, "n")
        self.assertEqual(code, 0)
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)
        self.assertIn("Final score: 1 point (1 of 3 correct).", script.text)
        self.assertEqual(script.text.count("What is 2 + 2?"), 2)

    def test_R7_no_exits(self):
        script, code = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        self.assertEqual(code, 0)
        self.assertEqual(script.text.count("What is 2 + 2?"), 1)
        self.assertTrue(script.output[-1].startswith("Goodbye!"))

    def test_R7_unrecognised_reply_asks_again(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "maybe", "n")
        self.assertIn("Please type y or n.", script.text)
        self.assertEqual(sum("Play again?" in p for p in script.prompts), 2)

    def test_R7_each_round_shuffles_questions(self):
        calls = []
        script = Script(SCIENCE, EASY, *ALL_RIGHT, NAME, "y",
                        SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=lambda items: calls.append(list(items)))
        self.assertEqual(len(calls), 2)

    def test_R7_end_of_input_exits_cleanly(self):
        script, code = run_game(SCIENCE, EASY, "B")
        self.assertEqual(code, 0)
        self.assertIn("Goodbye!", script.text)


    def test_R7_play_again_returns_to_category_menu(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "y", HISTORY, EASY, "B", NAME, "n")
        self.assertEqual(script.prompts.count(MENU_PROMPT), 2)
        self.assertEqual(script.text.count("Choose a category:"), 2)
        self.assertIn("Category: History", script.text)
        self.assertIn("Final score: 1 point (1 of 1 correct).", script.text)


class TestR9ChooseCategory(unittest.TestCase):
    def test_R9_menu_is_shown_before_the_first_question(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        menu = script.output.index("Choose a category:\n  1) Science\n"
                                   "  2) History\n  3) Sports\n"
                                   "  4) High Scores")
        first_question = next(i for i, line in enumerate(script.output)
                              if line.startswith("Question 1 of"))
        self.assertLess(menu, first_question)
        self.assertEqual(script.prompts[0], MENU_PROMPT)

    def test_R9_category_can_be_chosen_by_name(self):
        script, _ = run_game("history", "easy", "B", NAME, "n")
        self.assertIn("Category: History", script.text)
        self.assertIn("Final score: 1 point (1 of 1 correct).", script.text)

    def test_R9_invalid_choice_reprompts_menu(self):
        script = Script("9", "Art", "", SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=no_shuffle)
        self.assertEqual(
            script.text.count("Please type a number from 1 to 4 or a category name."),
            3)
        self.assertEqual(script.prompts[:4], [MENU_PROMPT] * 4)
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)

    def test_R9_choose_category_returns_selected_name(self):
        script = Script("x", "2")
        chosen = cli.choose_category(sample_bank(), script.input_fn,
                                     script.output_fn)
        self.assertEqual(chosen, "History")


class TestR10OnlySelectedCategoryAsked(unittest.TestCase):
    def test_R10_history_round_asks_only_history_questions(self):
        script = Script(HISTORY, EASY, "B", NAME, "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=no_shuffle)
        self.assertIn(history_question().text, script.text)
        for q in sample_questions():
            self.assertNotIn(q.text, script.text)
        self.assertIn("Question 1 of 1", script.text)
        self.assertIn("Final score: 1 point (1 of 1 correct).", script.text)

    def test_R10_science_round_does_not_ask_history_question(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        self.assertNotIn(history_question().text, script.text)
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)

    def test_R10_only_selected_questions_are_shuffled(self):
        shuffled = []
        script = Script(HISTORY, EASY, "B", NAME, "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=lambda items: shuffled.append(list(items)))
        self.assertEqual(shuffled, [[history_question()]])


class TestR11CategoryDisplayed(unittest.TestCase):
    def test_R11_round_starts_with_category_banner(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        banner = script.output.index("Category: Science")
        first_question = next(i for i, line in enumerate(script.output)
                              if line.startswith("Question 1 of"))
        self.assertLess(banner, first_question)

    def test_R11_every_question_header_shows_category(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        headers = [line.splitlines()[0] for line in script.output
                   if line.startswith("Question ")]
        self.assertEqual(headers, [f"Question {n} of 3 \u2014 Science (Easy)"
                                   for n in (1, 2, 3)])


class TestR12EmptyCategoryMessage(unittest.TestCase):
    MESSAGE = ("There are no questions in Sports yet. "
               "Please choose another category.")

    def test_R12_empty_category_shows_message_and_menu_again(self):
        script = Script(SPORTS, SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        code = cli.run(sample_bank(), script.input_fn, script.output_fn,
                       shuffle=no_shuffle)
        self.assertEqual(code, 0)
        self.assertEqual(script.text.count(self.MESSAGE), 1)
        self.assertEqual(script.text.count("Choose a category:"), 2)
        self.assertNotIn("Category: Sports", script.text)
        self.assertNotIn("Choose a difficulty for Sports:", script.text)
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)

    def test_R12_no_round_starts_for_empty_category(self):
        script = Script("sports")
        code = cli.run(sample_bank(), script.input_fn, script.output_fn,
                       shuffle=no_shuffle)
        self.assertEqual(code, 0)
        self.assertIn(self.MESSAGE, script.text)
        self.assertNotIn("Question 1 of", script.text)
        self.assertNotIn("Final score", script.text)
        self.assertIn("Goodbye!", script.text)

    def test_R12_empty_category_listed_in_menu(self):
        script = Script()
        cli.run(sample_bank(), script.input_fn, script.output_fn)
        self.assertIn("  3) Sports", script.text)


DIFFICULTY_MENU = ("Choose a difficulty for Science:\n  1) Easy\n  2) Medium\n"
                   "  3) Hard\n  4) Back to categories")
NO_HARD_SCIENCE = ("There are no Hard questions in Science yet.\n"
                   "Please choose another difficulty or go back.")


class TestR13ThreeDifficultyLevels(unittest.TestCase):
    def test_R13_difficulty_menu_offers_easy_medium_hard(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        self.assertIn(DIFFICULTY_MENU, script.output)


class TestR14ChooseDifficulty(unittest.TestCase):
    def test_R14_difficulty_asked_after_category_before_first_question(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        self.assertEqual(script.prompts[:2], [MENU_PROMPT, DIFFICULTY_PROMPT])
        menu = script.output.index(DIFFICULTY_MENU)
        category_menu = next(i for i, line in enumerate(script.output)
                             if line.startswith("Choose a category:"))
        first_question = next(i for i, line in enumerate(script.output)
                              if line.startswith("Question 1 of"))
        self.assertLess(category_menu, menu)
        self.assertLess(menu, first_question)

    def test_R14_difficulty_can_be_chosen_by_name(self):
        script, _ = run_game(SCIENCE, " MEDIUM ", "D", NAME, "n")
        self.assertIn("Difficulty: Medium", script.text)
        self.assertIn("Final score: 3 points (1 of 1 correct).", script.text)

    def test_R14_invalid_difficulty_reprompts(self):
        script, _ = run_game(SCIENCE, "0", "5", "expert", "", EASY,
                             *ALL_RIGHT, NAME, "n")
        self.assertEqual(script.text.count(
            "Please type a number from 1 to 4 or a difficulty name."), 4)
        self.assertEqual(script.prompts[1:6], [DIFFICULTY_PROMPT] * 5)
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)

    def test_R14_back_returns_to_category_menu(self):
        script, _ = run_game(SCIENCE, BACK, HISTORY, EASY, "B", NAME, "n")
        self.assertEqual(script.prompts[:4], [MENU_PROMPT, DIFFICULTY_PROMPT,
                                              MENU_PROMPT, DIFFICULTY_PROMPT])
        self.assertNotIn("Category: Science", script.text)
        self.assertIn("Category: History", script.text)

    def test_R14_back_can_be_typed_by_name(self):
        script, _ = run_game(SCIENCE, "Back", HISTORY, EASY, "B", NAME, "n")
        self.assertEqual(script.text.count("Choose a category:"), 2)
        self.assertIn("Final score: 1 point (1 of 1 correct).", script.text)

    def test_R14_play_again_asks_category_then_difficulty(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "y",
                             SCIENCE, MEDIUM, "D", NAME, "n")
        self.assertEqual(script.prompts.count(DIFFICULTY_PROMPT), 2)
        self.assertIn("Difficulty: Medium", script.text)

    def test_R14_choose_difficulty_returns_level_or_none_for_back(self):
        script = Script("x", "back")
        self.assertEqual(cli.choose_difficulty(sample_bank(), "Science",
                                               script.input_fn,
                                               script.output_fn), None)
        script = Script("x", "2")
        self.assertEqual(cli.choose_difficulty(sample_bank(), "Science",
                                               script.input_fn,
                                               script.output_fn), "Medium")


class TestR16CategoryAndDifficulty(unittest.TestCase):
    def test_R16_medium_round_asks_only_medium_questions_of_category(self):
        script, _ = run_game(SCIENCE, MEDIUM, "D", NAME, "n")
        self.assertIn(medium_science_question().text, script.text)
        for q in sample_questions() + [history_question()]:
            self.assertNotIn(q.text, script.text)
        self.assertIn("Question 1 of 1", script.text)

    def test_R16_easy_round_does_not_ask_medium_question(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        self.assertNotIn(medium_science_question().text, script.text)
        self.assertIn("Question 3 of 3", script.text)

    def test_R16_only_matching_questions_are_shuffled(self):
        shuffled = []
        script = Script(SCIENCE, MEDIUM, "D", NAME, "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=lambda items: shuffled.append(list(items)))
        self.assertEqual(shuffled, [[medium_science_question()]])


class TestR17DifficultyDisplayed(unittest.TestCase):
    def test_R17_difficulty_banner_follows_category_banner(self):
        script, _ = run_game(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        banner = script.output.index("Category: Science")
        self.assertEqual(script.output[banner + 1], "Difficulty: Easy")

    def test_R17_every_question_header_shows_difficulty(self):
        script, _ = run_game(SCIENCE, MEDIUM, "D", NAME, "n")
        headers = [line.splitlines()[0] for line in script.output
                   if line.startswith("Question ")]
        self.assertEqual(headers, ["Question 1 of 1 \u2014 Science (Medium)"])


class TestR18NoQuestionsAtDifficulty(unittest.TestCase):
    def test_R18_message_then_difficulty_menu_again(self):
        script, code = run_game(SCIENCE, HARD, EASY, *ALL_RIGHT, NAME, "n")
        self.assertEqual(code, 0)
        self.assertEqual(script.text.count(NO_HARD_SCIENCE), 1)
        self.assertEqual(script.output.count(DIFFICULTY_MENU), 2)
        after = script.output.index(NO_HARD_SCIENCE)
        self.assertEqual(script.output[after + 2], DIFFICULTY_MENU)
        self.assertNotIn("Difficulty: Hard", script.text)
        self.assertIn("Final score: 3 points (3 of 3 correct).", script.text)

    def test_R18_player_can_go_back_and_pick_another_category(self):
        script, code = run_game(SCIENCE, HARD, BACK, HISTORY, EASY, "B", NAME, "n")
        self.assertEqual(code, 0)
        self.assertIn(NO_HARD_SCIENCE, script.text)
        self.assertEqual(script.text.count("Choose a category:"), 2)
        self.assertIn("Category: History", script.text)
        self.assertIn("Final score: 1 point (1 of 1 correct).", script.text)

    def test_R18_no_round_starts_and_input_end_exits_cleanly(self):
        script, code = run_game(SCIENCE, "hard")
        self.assertEqual(code, 0)
        self.assertIn(NO_HARD_SCIENCE, script.text)
        self.assertNotIn("Question 1 of", script.text)
        self.assertNotIn("Final score", script.text)
        self.assertEqual(script.output[-1], "Goodbye!")

    def test_R18_repeated_empty_choices_do_not_crash(self):
        script, code = run_game(HISTORY, MEDIUM, HARD, "medium", EASY, "B", NAME, "n")
        self.assertEqual(code, 0)
        self.assertEqual(script.text.count(
            "There are no Medium questions in History yet."), 2)
        self.assertEqual(script.text.count(
            "There are no Hard questions in History yet."), 1)
        self.assertIn("Final score: 1 point (1 of 1 correct).", script.text)



PLAY_AGAIN_PROMPT = "Play again? (y/n): "
EMPTY_LIST = "High Scores\nNo high scores yet."
UNREADABLE = "High scores could not be read, so the list starts empty."


def score_data(name, points, category="Science", difficulty="Easy"):
    return {"name": name, "points": points, "category": category,
            "difficulty": difficulty}


class ScoresFileTestCase(unittest.TestCase):
    """Gives each test a temporary high-score path (not created yet)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "highscores.json")

    def write_scores(self, *items):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"scores": list(items)}, f)

    def write_raw(self, content):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)

    def saved(self):
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)["scores"]

    def play(self, *lines):
        return run_game(*lines, scores_path=self.path)


def high_score_tables(script):
    return [line for line in script.output if line.startswith("High Scores")]


class TestR19NameAndSave(ScoresFileTestCase):
    def test_R19_name_is_asked_after_final_score_before_play_again(self):
        script, _ = self.play(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        self.assertEqual(script.prompts[-2:], [NAME_PROMPT, PLAY_AGAIN_PROMPT])
        final = script.transcript.index(
            ("output", "Final score: 3 points (3 of 3 correct)."))
        self.assertLess(final, script.transcript.index(("prompt", NAME_PROMPT)))

    def test_R19_entry_is_saved_with_name_points_category_difficulty(self):
        self.play(SCIENCE, MEDIUM, "D", "Ann", "n")
        self.assertEqual(self.saved(), [score_data("Ann", 3, "Science", "Medium")])

    def test_R19_every_completed_game_is_saved(self):
        self.play(HISTORY, EASY, "B", "Ann", "y", SCIENCE, MEDIUM, "D", "Bo", "n")
        self.assertEqual(self.saved(), [score_data("Bo", 3, "Science", "Medium"),
                                        score_data("Ann", 1, "History", "Easy")])

    def test_R19_zero_score_still_asks_and_saves(self):
        script, _ = self.play(SCIENCE, EASY, "A", "A", "B", "Ann", "n")
        self.assertIn(NAME_PROMPT, script.prompts)
        self.assertEqual(self.saved(), [score_data("Ann", 0)])

    def test_R19_blank_name_asks_again(self):
        script, _ = self.play(HISTORY, EASY, "B", "", "   ", "Ann", "n")
        self.assertEqual(script.text.count("Please type your name."), 2)
        self.assertEqual(script.prompts.count(NAME_PROMPT), 3)
        self.assertEqual(self.saved()[0]["name"], "Ann")

    def test_R19_name_is_trimmed_and_cut_to_20_characters(self):
        self.play(HISTORY, EASY, "B", "  Bartholomew Alexander Smith  ", "n")
        self.assertEqual(self.saved()[0]["name"], "Bartholomew Alexande")

    def test_R19_input_ending_at_name_prompt_saves_nothing(self):
        script, code = self.play(HISTORY, EASY, "B")
        self.assertEqual(code, 0)
        self.assertEqual(script.prompts[-1], NAME_PROMPT)
        self.assertFalse(os.path.exists(self.path))
        self.assertEqual(script.output[-1], "Goodbye!")

    def test_R19_game_left_mid_round_saves_nothing(self):
        script, _ = self.play(SCIENCE, EASY, "B")
        self.assertNotIn(NAME_PROMPT, script.prompts)
        self.assertFalse(os.path.exists(self.path))

    def test_R19_save_failure_is_reported_and_game_continues(self):
        path = os.path.join(self._tmp.name, "missing-folder", "scores.json")
        script, code = run_game(HISTORY, EASY, "B", "Ann", "y",
                                HIGH_SCORES, SCIENCE, MEDIUM, "D", "Bo", "n",
                                scores_path=path)
        self.assertEqual(code, 0)
        failures = [line for line in script.output
                    if line.startswith("Could not save high scores: ")]
        self.assertEqual(len(failures), 2)
        self.assertTrue(failures[0].endswith("."))
        # The entries still appear for the rest of the session.
        self.assertIn("   1. Ann                    1 point   History (Easy)",
                      high_score_tables(script)[1])
        self.assertIn("   1. Bo                     3 points  Science (Medium)",
                      high_score_tables(script)[2])
        self.assertEqual(script.output[-1], "Goodbye!")

    def test_R19_without_scores_path_nothing_is_written(self):
        script, _ = run_game(HISTORY, EASY, "B", NAME, "n")
        self.assertIn("   1. Ann                    1 point   History (Easy)",
                      high_score_tables(script)[0])
        self.assertEqual(os.listdir(self._tmp.name), [])

    def test_R19_python_m_trivia_saves_to_the_scores_path(self):
        result = run_bundled_game(self.path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(NAME_PROMPT, result.stdout)
        saved = self.saved()
        self.assertEqual(len(saved), 1)
        self.assertEqual((saved[0]["name"], saved[0]["category"],
                          saved[0]["difficulty"]), ("A", "Science", "Easy"))

    def test_R19_scores_option_defaults_to_package_file(self):
        self.assertEqual(cli.parse_args([]).scores,
                         os.path.join(PACKAGE_DIR, "highscores.json"))
        self.assertEqual(cli.parse_args(["--scores", "x.json"]).scores, "x.json")


class TestR20TopTenKept(ScoresFileTestCase):
    def test_R20_low_score_misses_a_full_list(self):
        full = [score_data(f"P{n}", 10 + n) for n in range(10, 0, -1)]
        self.write_scores(*full)
        script, _ = self.play(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")
        self.assertEqual(self.saved(), full)
        self.assertNotIn(NAME, high_score_tables(script)[0])

    def test_R20_high_score_pushes_the_lowest_out(self):
        full = [score_data(f"P{n}", n) for n in range(10, 0, -1)]
        self.write_scores(*full)
        self.play(SCIENCE, EASY, *ALL_RIGHT, NAME, "n")  # 3 points
        saved = self.saved()
        self.assertEqual(len(saved), 10)
        self.assertEqual([e["points"] for e in saved],
                         [10, 9, 8, 7, 6, 5, 4, 3, 3, 2])
        self.assertEqual(saved[8]["name"], NAME)

    def test_R20_eleven_games_keep_ten(self):
        lines = []
        for n in range(11):
            lines += [HISTORY, EASY, "B", f"P{n}", "y"]
        self.play(*lines[:-1], "n")
        saved = self.saved()
        self.assertEqual([e["name"] for e in saved], [f"P{n}" for n in range(10)])


class TestR21HighestFirstShown(ScoresFileTestCase):
    def test_R21_list_is_shown_highest_first(self):
        script, _ = self.play(HISTORY, EASY, "B", "Low", "y",
                              SCIENCE, MEDIUM, "D", "High", "n")
        self.assertEqual(high_score_tables(script)[-1], "\n".join([
            "High Scores",
            "   1. High                   3 points  Science (Medium)",
            "   2. Low                    1 point   History (Easy)",
        ]))

    def test_R21_ties_show_older_entry_first(self):
        self.write_scores(score_data("Old", 1, "History", "Easy"))
        script, _ = self.play(HISTORY, EASY, "B", "New", "n")
        lines = high_score_tables(script)[0].splitlines()
        self.assertTrue(lines[1].startswith("   1. Old "))
        self.assertTrue(lines[2].startswith("   2. New "))


class TestR22ShownAfterEachGame(ScoresFileTestCase):
    def test_R22_list_follows_name_and_precedes_play_again(self):
        script, _ = self.play(HISTORY, EASY, "B", NAME, "n")
        table = "High Scores\n   1. Ann                    1 point   History (Easy)"
        at = script.transcript.index(("output", table))
        self.assertEqual(script.transcript[at - 1], ("output", ""))
        self.assertLess(script.transcript.index(("prompt", NAME_PROMPT)), at)
        self.assertEqual(script.transcript[at + 1], ("prompt", PLAY_AGAIN_PROMPT))

    def test_R22_list_is_shown_after_every_game(self):
        script, _ = self.play(HISTORY, EASY, "B", NAME, "y",
                              HISTORY, EASY, "B", NAME, "n")
        self.assertEqual(len(high_score_tables(script)), 2)

    def test_R22_list_is_not_shown_when_no_game_is_completed(self):
        script, _ = self.play(SCIENCE, EASY, "B")
        self.assertEqual(high_score_tables(script), [])


class TestR23HighScoresFromMenu(ScoresFileTestCase):
    def test_R23_menu_option_shows_list_then_menu_again(self):
        script, code = self.play(HIGH_SCORES)
        self.assertEqual(code, 0)
        self.assertEqual(script.prompts, [MENU_PROMPT, MENU_PROMPT])
        at = script.output.index(EMPTY_LIST)
        self.assertTrue(script.output[at + 2].startswith("Choose a category:"))
        self.assertNotIn("Choose a difficulty", script.text)

    def test_R23_high_scores_can_be_typed_by_name(self):
        script, _ = self.play(" high SCORES ", "High Scores")
        self.assertEqual(script.output.count(EMPTY_LIST), 2)

    def test_R23_menu_shows_saved_scores(self):
        self.write_scores(score_data("Ana", 12, "Science", "Hard"),
                          score_data("Ben", 3, "History", "Medium"))
        script, _ = self.play(HIGH_SCORES)
        self.assertEqual(high_score_tables(script), ["\n".join([
            "High Scores",
            "   1. Ana                   12 points  Science (Hard)",
            "   2. Ben                    3 points  History (Medium)",
        ])])

    def test_R23_menu_shows_scores_from_this_session(self):
        script, _ = self.play(HISTORY, EASY, "B", NAME, "y", HIGH_SCORES)
        self.assertEqual(len(high_score_tables(script)), 2)
        self.assertIn(" Ann ", high_score_tables(script)[1])

    def test_R23_viewing_scores_then_playing_works(self):
        script, _ = self.play(HIGH_SCORES, HISTORY, EASY, "B", NAME, "n")
        self.assertIn("Final score: 1 point (1 of 1 correct).", script.text)
        self.assertEqual(self.saved(), [score_data("Ann", 1, "History", "Easy")])


class TestR24MissingScoresFile(ScoresFileTestCase):
    def test_R24_missing_file_starts_with_empty_list_and_no_message(self):
        script, code = self.play(HIGH_SCORES)
        self.assertEqual(code, 0)
        self.assertIn(EMPTY_LIST, script.output)
        self.assertNotIn(UNREADABLE, script.output)
        self.assertFalse(os.path.exists(self.path))

    def test_R24_file_is_created_by_first_save(self):
        self.play(HISTORY, EASY, "B", NAME, "n")
        self.assertTrue(os.path.isfile(self.path))
        self.assertFalse(os.path.exists(self.path + ".bak"))

    def test_R24_python_m_trivia_creates_missing_file(self):
        self.assertFalse(os.path.exists(self.path))
        result = run_bundled_game(self.path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(UNREADABLE, result.stdout)
        self.assertTrue(os.path.isfile(self.path))


class TestR25CorruptedScoresFile(ScoresFileTestCase):
    def test_R25_corrupted_file_shows_message_after_welcome(self):
        self.write_raw("{not json")
        script, code = self.play(HIGH_SCORES)
        self.assertEqual(code, 0)
        self.assertEqual(script.output[:2],
                         ["Welcome to Trivia Challenge!", UNREADABLE])
        self.assertEqual(script.output.count(UNREADABLE), 1)
        self.assertIn(EMPTY_LIST, script.output)

    def test_R25_wrong_shape_counts_as_corrupted(self):
        self.write_scores(score_data("Ana", -3))
        script, _ = self.play(HIGH_SCORES)
        self.assertIn(UNREADABLE, script.output)
        self.assertIn(EMPTY_LIST, script.output)

    def test_R25_bad_file_is_untouched_until_first_save(self):
        self.write_raw("{not json")
        self.play(HIGH_SCORES)
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "{not json")
        self.assertFalse(os.path.exists(self.path + ".bak"))

    def test_R25_first_save_backs_up_bad_file_then_writes_fresh_list(self):
        self.write_raw("{not json")
        script, _ = self.play(HISTORY, EASY, "B", NAME, "y",
                              HISTORY, EASY, "B", "Bo", "n")
        with open(self.path + ".bak", encoding="utf-8") as f:
            self.assertEqual(f.read(), "{not json")
        self.assertEqual(self.saved(), [score_data("Ann", 1, "History", "Easy"),
                                        score_data("Bo", 1, "History", "Easy")])
        self.assertEqual(script.output.count(UNREADABLE), 1)

    def test_R25_unreadable_path_does_not_crash(self):
        os.mkdir(self.path)  # a folder where the file should be
        script, code = self.play(HISTORY, EASY, "B", NAME, "n")
        self.assertEqual(code, 0)
        self.assertIn(UNREADABLE, script.output)
        self.assertTrue(any(line.startswith("Could not save high scores: ")
                            for line in script.output))
        self.assertIn(" Ann ", high_score_tables(script)[0])
        self.assertEqual(script.output[-1], "Goodbye!")

    def test_R25_python_m_trivia_survives_a_corrupted_file(self):
        self.write_raw("\x00garbage")
        result = run_bundled_game(self.path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn(UNREADABLE, result.stdout)
        self.assertEqual(len(self.saved()), 1)


if __name__ == "__main__":
    unittest.main()
