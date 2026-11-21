"""Tests for the game loop in trivia.cli, driven with scripted input."""

import ast
import os
import subprocess
import sys
import unittest

from trivia import cli
from tests.helpers import Script, no_shuffle, sample_questions

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.join(PROJECT_ROOT, "trivia")

# Answers to sample_questions(): B, C, A
ALL_RIGHT = ("B", "C", "A")


def run_game(*lines):
    script = Script(*lines)
    code = cli.run(sample_questions(), script.input_fn, script.output_fn,
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
        # Answer every question with "A", then decline to play again.
        stdin = "A\n" * 200 + "n\n"
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
        script, _ = run_game(*ALL_RIGHT, "n")
        for q in sample_questions():
            self.assertIn(q.text, script.text)
            for letter, choice in zip("ABCD", q.choices):
                self.assertIn(f"{letter}) {choice}", script.text)


class TestR3TypedLetter(unittest.TestCase):
    def test_R3_lowercase_letters_are_accepted_in_game(self):
        script, _ = run_game("b", "c", "a", "n")
        self.assertIn("Final score: 3 out of 3.", script.text)

    def test_R3_invalid_letter_reprompts_same_question(self):
        script, _ = run_game("E", "", "B", "C", "A", "n")
        self.assertEqual(script.text.count("Please type A, B, C, or D."), 2)
        self.assertEqual(script.text.count("What is 2 + 2?"), 1)
        self.assertIn("Final score: 3 out of 3.", script.text)


class TestR4Feedback(unittest.TestCase):
    def test_R4_game_reports_correct_and_incorrect(self):
        script, _ = run_game("B", "A", "A", "n")
        self.assertEqual(script.text.count("Correct!"), 2)
        self.assertIn("Incorrect. The correct answer was C) Mars.", script.text)


class TestR5Score(unittest.TestCase):
    def test_R5_running_score_shown_after_each_answer(self):
        script, _ = run_game("B", "A", "A", "n")
        for expected in ("Score: 1/1", "Score: 1/2", "Score: 2/3"):
            self.assertIn(expected, script.text)

    def test_R5_play_round_returns_score(self):
        script = Script("A", "C", "D")
        score = cli.play_round(sample_questions(), script.input_fn, script.output_fn)
        self.assertEqual((score.correct, score.answered), (1, 3))


class TestR6FinalScoreShown(unittest.TestCase):
    def test_R6_final_score_shown_after_last_question(self):
        script, _ = run_game("A", "A", "A", "n")
        final = [i for i, line in enumerate(script.output)
                 if line == "Final score: 1 out of 3."]
        last_feedback = max(i for i, line in enumerate(script.output)
                            if line.startswith(("Correct!", "Incorrect.")))
        self.assertEqual(len(final), 1)
        self.assertGreater(final[0], last_feedback)


class TestR7PlayAgain(unittest.TestCase):
    def test_R7_yes_starts_new_round_with_reset_score(self):
        script, code = run_game(*ALL_RIGHT, "y", "A", "A", "A", "n")
        self.assertEqual(code, 0)
        self.assertIn("Final score: 3 out of 3.", script.text)
        self.assertIn("Final score: 1 out of 3.", script.text)
        self.assertEqual(script.text.count("What is 2 + 2?"), 2)

    def test_R7_no_exits(self):
        script, code = run_game(*ALL_RIGHT, "n")
        self.assertEqual(code, 0)
        self.assertEqual(script.text.count("What is 2 + 2?"), 1)
        self.assertTrue(script.output[-1].startswith("Goodbye!"))

    def test_R7_unrecognised_reply_asks_again(self):
        script, _ = run_game(*ALL_RIGHT, "maybe", "n")
        self.assertIn("Please type y or n.", script.text)
        self.assertEqual(sum("Play again?" in p for p in script.prompts), 2)

    def test_R7_each_round_shuffles_questions(self):
        calls = []
        script = Script(*ALL_RIGHT, "y", *ALL_RIGHT, "n")
        cli.run(sample_questions(), script.input_fn, script.output_fn,
                shuffle=lambda items: calls.append(list(items)))
        self.assertEqual(len(calls), 2)

    def test_R7_end_of_input_exits_cleanly(self):
        script, code = run_game("B")
        self.assertEqual(code, 0)
        self.assertIn("Goodbye!", script.text)


if __name__ == "__main__":
    unittest.main()
