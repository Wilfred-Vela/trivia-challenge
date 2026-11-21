"""Unit tests for the pure game logic in trivia.game."""

import json
import os
import tempfile
import unittest

from trivia import game
from trivia.game import Question, QuestionFileError, Score


class TestR1LocalQuestions(unittest.TestCase):
    def test_R1_bundled_question_file_loads_from_disk(self):
        questions = game.load_questions(game.DEFAULT_QUESTIONS_PATH)
        self.assertGreaterEqual(len(questions), 5)
        self.assertTrue(all(isinstance(q, Question) for q in questions))

    def test_R1_load_questions_reads_given_json_file(self):
        data = [{"question": "Q?", "choices": ["a", "b", "c", "d"], "answer": "d"}]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "q.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            questions = game.load_questions(path)
        self.assertEqual(questions, [Question("Q?", ["a", "b", "c", "d"], 3)])

    def test_R1_missing_question_file_raises_clear_error(self):
        with self.assertRaises(QuestionFileError):
            game.load_questions("/nonexistent/questions.json")

    def test_R1_invalid_json_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "q.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{not json")
            with self.assertRaises(QuestionFileError):
                game.load_questions(path)


class TestR2MultipleChoiceDisplay(unittest.TestCase):
    def setUp(self):
        self.q = Question("What is 2 + 2?", ["3", "4", "5", "6"], 1)

    def test_R2_format_question_shows_text_and_four_lettered_choices(self):
        text = game.format_question(self.q, 1, 10)
        self.assertIn("What is 2 + 2?", text)
        for line in ("A) 3", "B) 4", "C) 5", "D) 6"):
            self.assertIn(line, text)

    def test_R2_format_question_shows_question_number(self):
        self.assertIn("Question 3 of 10", game.format_question(self.q, 3, 10))

    def test_R2_every_bundled_question_has_four_choices(self):
        for q in game.load_questions(game.DEFAULT_QUESTIONS_PATH):
            self.assertEqual(len(q.choices), 4, q.text)

    def test_R2_question_with_wrong_number_of_choices_is_rejected(self):
        bad = [{"question": "Q?", "choices": ["a", "b", "c"], "answer": "A"}]
        with self.assertRaises(QuestionFileError):
            game.parse_questions(bad)

    def test_R2_question_with_invalid_answer_letter_is_rejected(self):
        bad = [{"question": "Q?", "choices": ["a", "b", "c", "d"], "answer": "E"}]
        with self.assertRaises(QuestionFileError):
            game.parse_questions(bad)

    def test_R2_empty_question_list_is_rejected(self):
        with self.assertRaises(QuestionFileError):
            game.parse_questions([])


class TestR3LetterSelection(unittest.TestCase):
    def test_R3_uppercase_letters_map_to_choice_index(self):
        for i, letter in enumerate("ABCD"):
            self.assertEqual(game.parse_choice(letter), i)

    def test_R3_lowercase_and_whitespace_are_accepted(self):
        self.assertEqual(game.parse_choice("b"), 1)
        self.assertEqual(game.parse_choice("  d \n"), 3)

    def test_R3_invalid_input_returns_none(self):
        for text in ("", " ", "E", "AB", "1", "answer", "?"):
            self.assertIsNone(game.parse_choice(text), repr(text))


class TestR4CorrectnessFeedback(unittest.TestCase):
    def setUp(self):
        self.q = Question("Red Planet?", ["Venus", "Jupiter", "Mars", "Saturn"], 2)

    def test_R4_is_correct_true_only_for_answer_index(self):
        self.assertTrue(game.is_correct(self.q, 2))
        for i in (0, 1, 3):
            self.assertFalse(game.is_correct(self.q, i))

    def test_R4_correct_answer_feedback_says_correct(self):
        self.assertEqual(game.feedback(self.q, 2), "Correct!")

    def test_R4_incorrect_answer_feedback_names_correct_option(self):
        self.assertEqual(game.feedback(self.q, 0),
                         "Incorrect. The correct answer was C) Mars.")


class TestR5ScoreTracking(unittest.TestCase):
    def test_R5_new_score_starts_at_zero(self):
        s = Score()
        self.assertEqual((s.correct, s.answered), (0, 0))

    def test_R5_correct_answers_increase_score_incorrect_do_not(self):
        s = Score()
        for result in (True, False, True, True, False):
            s.record(result)
        self.assertEqual((s.correct, s.answered), (3, 5))

    def test_R5_running_score_text(self):
        s = Score()
        s.record(True)
        s.record(False)
        self.assertEqual(s.running_text(), "Score: 1/2")


class TestR6FinalScore(unittest.TestCase):
    def test_R6_final_score_message(self):
        s = Score()
        for result in (True, False, True):
            s.record(result)
        self.assertEqual(game.final_score_message(s), "Final score: 2 out of 3.")


class TestR7PlayAgainParsing(unittest.TestCase):
    def test_R7_yes_answers(self):
        for text in ("y", "Y", "yes", " YES "):
            self.assertIs(game.parse_play_again(text), True, repr(text))

    def test_R7_no_answers(self):
        for text in ("n", "N", "no", " No "):
            self.assertIs(game.parse_play_again(text), False, repr(text))

    def test_R7_unrecognised_answers_return_none(self):
        for text in ("", "maybe", "yep", "1"):
            self.assertIsNone(game.parse_play_again(text), repr(text))


if __name__ == "__main__":
    unittest.main()
