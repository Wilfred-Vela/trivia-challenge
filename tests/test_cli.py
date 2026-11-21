"""Tests for the game loop in trivia.cli, driven with scripted input."""

import ast
import os
import subprocess
import sys
import unittest

from trivia import cli
from tests.helpers import (Script, history_question, no_shuffle,
                           sample_bank, sample_questions)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.join(PROJECT_ROOT, "trivia")

# sample_bank() menu: 1) Science, 2) History, 3) Sports (no questions).
SCIENCE, HISTORY, SPORTS = "1", "2", "3"
# Answers to the Science questions (sample_questions()): B, C, A
ALL_RIGHT = ("B", "C", "A")
MENU_PROMPT = "Category (1-3): "


def run_game(*lines):
    """Run the whole game on sample_bank(); lines start with a category choice."""
    script = Script(*lines)
    code = cli.run(sample_bank(), script.input_fn, script.output_fn,
                   shuffle=no_shuffle)
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
        # Pick the first category, answer every question with "A"
        # (extra "A"s are rejected by the play-again prompt), then decline.
        stdin = "1\n" + "A\n" * 200 + "n\n"
        result = subprocess.run(
            [sys.executable, "-m", "trivia"], input=stdin, capture_output=True,
            text=True, cwd=PROJECT_ROOT, timeout=30,
        )
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
        script, _ = run_game(SCIENCE, *ALL_RIGHT, "n")
        for q in sample_questions():
            self.assertIn(q.text, script.text)
            for letter, choice in zip("ABCD", q.choices):
                self.assertIn(f"{letter}) {choice}", script.text)


class TestR3TypedLetter(unittest.TestCase):
    def test_R3_lowercase_letters_are_accepted_in_game(self):
        script, _ = run_game(SCIENCE, "b", "c", "a", "n")
        self.assertIn("Final score: 3 out of 3.", script.text)

    def test_R3_invalid_letter_reprompts_same_question(self):
        script, _ = run_game(SCIENCE, "E", "", "B", "C", "A", "n")
        self.assertEqual(script.text.count("Please type A, B, C, or D."), 2)
        self.assertEqual(script.text.count("What is 2 + 2?"), 1)
        self.assertIn("Final score: 3 out of 3.", script.text)


class TestR4Feedback(unittest.TestCase):
    def test_R4_game_reports_correct_and_incorrect(self):
        script, _ = run_game(SCIENCE, "B", "A", "A", "n")
        self.assertEqual(script.text.count("Correct!"), 2)
        self.assertIn("Incorrect. The correct answer was C) Mars.", script.text)


class TestR5Score(unittest.TestCase):
    def test_R5_running_score_shown_after_each_answer(self):
        script, _ = run_game(SCIENCE, "B", "A", "A", "n")
        for expected in ("Score: 1/1", "Score: 1/2", "Score: 2/3"):
            self.assertIn(expected, script.text)

    def test_R5_play_round_returns_score(self):
        script = Script("A", "C", "D")
        score = cli.play_round(sample_questions(), "Science",
                               script.input_fn, script.output_fn)
        self.assertEqual((score.correct, score.answered), (1, 3))


class TestR6FinalScoreShown(unittest.TestCase):
    def test_R6_final_score_shown_after_last_question(self):
        script, _ = run_game(SCIENCE, "A", "A", "A", "n")
        final = [i for i, line in enumerate(script.output)
                 if line == "Final score: 1 out of 3."]
        last_feedback = max(i for i, line in enumerate(script.output)
                            if line.startswith(("Correct!", "Incorrect.")))
        self.assertEqual(len(final), 1)
        self.assertGreater(final[0], last_feedback)


class TestR7PlayAgain(unittest.TestCase):
    def test_R7_yes_starts_new_round_with_reset_score(self):
        script, code = run_game(SCIENCE, *ALL_RIGHT, "y", SCIENCE, "A", "A", "A", "n")
        self.assertEqual(code, 0)
        self.assertIn("Final score: 3 out of 3.", script.text)
        self.assertIn("Final score: 1 out of 3.", script.text)
        self.assertEqual(script.text.count("What is 2 + 2?"), 2)

    def test_R7_no_exits(self):
        script, code = run_game(SCIENCE, *ALL_RIGHT, "n")
        self.assertEqual(code, 0)
        self.assertEqual(script.text.count("What is 2 + 2?"), 1)
        self.assertTrue(script.output[-1].startswith("Goodbye!"))

    def test_R7_unrecognised_reply_asks_again(self):
        script, _ = run_game(SCIENCE, *ALL_RIGHT, "maybe", "n")
        self.assertIn("Please type y or n.", script.text)
        self.assertEqual(sum("Play again?" in p for p in script.prompts), 2)

    def test_R7_each_round_shuffles_questions(self):
        calls = []
        script = Script(SCIENCE, *ALL_RIGHT, "y", SCIENCE, *ALL_RIGHT, "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=lambda items: calls.append(list(items)))
        self.assertEqual(len(calls), 2)

    def test_R7_end_of_input_exits_cleanly(self):
        script, code = run_game(SCIENCE, "B")
        self.assertEqual(code, 0)
        self.assertIn("Goodbye!", script.text)


    def test_R7_play_again_returns_to_category_menu(self):
        script, _ = run_game(SCIENCE, *ALL_RIGHT, "y", HISTORY, "B", "n")
        self.assertEqual(script.prompts.count(MENU_PROMPT), 2)
        self.assertEqual(script.text.count("Choose a category:"), 2)
        self.assertIn("Category: History", script.text)
        self.assertIn("Final score: 1 out of 1.", script.text)


class TestR9ChooseCategory(unittest.TestCase):
    def test_R9_menu_is_shown_before_the_first_question(self):
        script, _ = run_game(SCIENCE, *ALL_RIGHT, "n")
        menu = script.output.index("Choose a category:\n  1) Science\n"
                                   "  2) History\n  3) Sports")
        first_question = next(i for i, line in enumerate(script.output)
                              if line.startswith("Question 1 of"))
        self.assertLess(menu, first_question)
        self.assertEqual(script.prompts[0], MENU_PROMPT)

    def test_R9_category_can_be_chosen_by_name(self):
        script, _ = run_game("history", "B", "n")
        self.assertIn("Category: History", script.text)
        self.assertIn("Final score: 1 out of 1.", script.text)

    def test_R9_invalid_choice_reprompts_menu(self):
        script = Script("9", "Art", "", SCIENCE, *ALL_RIGHT, "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=no_shuffle)
        self.assertEqual(
            script.text.count("Please type a number from 1 to 3 or a category name."),
            3)
        self.assertEqual(script.prompts[:4], [MENU_PROMPT] * 4)
        self.assertIn("Final score: 3 out of 3.", script.text)

    def test_R9_choose_category_returns_selected_name(self):
        script = Script("x", "2")
        chosen = cli.choose_category(sample_bank(), script.input_fn,
                                     script.output_fn)
        self.assertEqual(chosen, "History")


class TestR10OnlySelectedCategoryAsked(unittest.TestCase):
    def test_R10_history_round_asks_only_history_questions(self):
        script = Script(HISTORY, "B", "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=no_shuffle)
        self.assertIn(history_question().text, script.text)
        for q in sample_questions():
            self.assertNotIn(q.text, script.text)
        self.assertIn("Question 1 of 1", script.text)
        self.assertIn("Final score: 1 out of 1.", script.text)

    def test_R10_science_round_does_not_ask_history_question(self):
        script, _ = run_game(SCIENCE, *ALL_RIGHT, "n")
        self.assertNotIn(history_question().text, script.text)
        self.assertIn("Final score: 3 out of 3.", script.text)

    def test_R10_only_selected_questions_are_shuffled(self):
        shuffled = []
        script = Script(HISTORY, "B", "n")
        cli.run(sample_bank(), script.input_fn, script.output_fn,
                shuffle=lambda items: shuffled.append(list(items)))
        self.assertEqual(shuffled, [[history_question()]])


class TestR11CategoryDisplayed(unittest.TestCase):
    def test_R11_round_starts_with_category_banner(self):
        script, _ = run_game(SCIENCE, *ALL_RIGHT, "n")
        banner = script.output.index("Category: Science")
        first_question = next(i for i, line in enumerate(script.output)
                              if line.startswith("Question 1 of"))
        self.assertLess(banner, first_question)

    def test_R11_every_question_header_shows_category(self):
        script, _ = run_game(SCIENCE, *ALL_RIGHT, "n")
        headers = [line.splitlines()[0] for line in script.output
                   if line.startswith("Question ")]
        self.assertEqual(headers, [f"Question {n} of 3 \u2014 Science"
                                   for n in (1, 2, 3)])


class TestR12EmptyCategoryMessage(unittest.TestCase):
    MESSAGE = ("There are no questions in Sports yet. "
               "Please choose another category.")

    def test_R12_empty_category_shows_message_and_menu_again(self):
        script = Script(SPORTS, SCIENCE, *ALL_RIGHT, "n")
        code = cli.run(sample_bank(), script.input_fn, script.output_fn,
                       shuffle=no_shuffle)
        self.assertEqual(code, 0)
        self.assertEqual(script.text.count(self.MESSAGE), 1)
        self.assertEqual(script.text.count("Choose a category:"), 2)
        self.assertNotIn("Category: Sports", script.text)
        self.assertIn("Final score: 3 out of 3.", script.text)

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


if __name__ == "__main__":
    unittest.main()
