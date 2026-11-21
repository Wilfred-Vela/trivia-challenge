"""Unit tests for the pure game logic in trivia.game."""

import json
import os
import tempfile
import unittest

from trivia import game
from trivia.game import Question, QuestionBank, QuestionFileError, Score
from tests.helpers import sample_bank


def q_item(category="Science", question="Q?", choices=("a", "b", "c", "d"),
           answer="A"):
    """One question as it appears in the JSON file."""
    return {"category": category, "question": question,
            "choices": list(choices), "answer": answer}


def bank_data(*items, categories=("Science",)):
    """A whole question file (decoded JSON) holding ``items``."""
    return {"categories": list(categories), "questions": list(items)}


def bundled_bank():
    return game.load_bank(game.DEFAULT_QUESTIONS_PATH)


class TestR1LocalQuestions(unittest.TestCase):
    def test_R1_bundled_question_file_loads_from_disk(self):
        bank = bundled_bank()
        self.assertIsInstance(bank, QuestionBank)
        self.assertGreaterEqual(len(bank.questions), 5)
        self.assertTrue(all(isinstance(q, Question) for q in bank.questions))

    def test_R1_load_bank_reads_given_json_file(self):
        data = bank_data(q_item(answer="d"))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "q.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            bank = game.load_bank(path)
        self.assertEqual(bank.categories, ["Science"])
        self.assertEqual(bank.questions,
                         [Question("Q?", ["a", "b", "c", "d"], 3, "Science")])

    def test_R1_missing_question_file_raises_clear_error(self):
        with self.assertRaises(QuestionFileError):
            game.load_bank("/nonexistent/questions.json")

    def test_R1_invalid_json_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "q.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{not json")
            with self.assertRaises(QuestionFileError):
                game.load_bank(path)


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
        for q in bundled_bank().questions:
            self.assertEqual(len(q.choices), 4, q.text)

    def test_R2_question_with_wrong_number_of_choices_is_rejected(self):
        with self.assertRaises(QuestionFileError):
            game.parse_bank(bank_data(q_item(choices=("a", "b", "c"))))

    def test_R2_question_with_invalid_answer_letter_is_rejected(self):
        with self.assertRaises(QuestionFileError):
            game.parse_bank(bank_data(q_item(answer="E")))

    def test_R2_empty_question_list_is_rejected(self):
        with self.assertRaises(QuestionFileError):
            game.parse_bank(bank_data())


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


class TestR8Categories(unittest.TestCase):
    def test_R8_bundled_file_has_the_four_named_categories(self):
        self.assertEqual(bundled_bank().categories,
                         ["Science", "History", "Sports", "Geography"])

    def test_R8_every_bundled_question_belongs_to_a_declared_category(self):
        bank = bundled_bank()
        for q in bank.questions:
            self.assertIn(q.category, bank.categories, q.text)

    def test_R8_every_bundled_category_has_questions(self):
        bank = bundled_bank()
        for name in bank.categories:
            self.assertGreaterEqual(len(bank.questions_in(name)), 3, name)

    def test_R8_parse_bank_keeps_category_on_each_question(self):
        bank = game.parse_bank(bank_data(
            q_item("History", "H?"), q_item("Science", "S?"),
            categories=("Science", "History")))
        self.assertEqual([(q.category, q.text) for q in bank.questions],
                         [("History", "H?"), ("Science", "S?")])

    def test_R8_question_with_undeclared_category_is_rejected(self):
        with self.assertRaisesRegex(QuestionFileError, "Art"):
            game.parse_bank(bank_data(q_item("Art")))

    def test_R8_question_without_category_is_rejected(self):
        item = q_item()
        del item["category"]
        with self.assertRaises(QuestionFileError):
            game.parse_bank(bank_data(item))

    def test_R8_category_spelling_must_match_exactly(self):
        with self.assertRaises(QuestionFileError):
            game.parse_bank(bank_data(q_item("science")))

    def test_R8_missing_or_empty_category_list_is_rejected(self):
        for categories in ([], None, "Science", [""], [3]):
            data = {"categories": categories, "questions": [q_item()]}
            with self.assertRaises(QuestionFileError, msg=repr(categories)):
                game.parse_bank(data)

    def test_R8_duplicate_categories_are_rejected(self):
        with self.assertRaises(QuestionFileError):
            game.parse_bank(bank_data(q_item(),
                                      categories=("Science", "science")))

    def test_R8_round_one_bare_array_format_is_rejected_clearly(self):
        old = [{"question": "Q?", "choices": ["a", "b", "c", "d"], "answer": "A"}]
        with self.assertRaisesRegex(QuestionFileError, "categories"):
            game.parse_bank(old)


class TestR9CategorySelection(unittest.TestCase):
    CATEGORIES = ["Science", "History", "Sports", "Geography"]

    def test_R9_menu_lists_categories_numbered_in_order(self):
        menu = game.format_category_menu(self.CATEGORIES)
        lines = menu.splitlines()
        self.assertEqual(lines[0], "Choose a category:")
        self.assertEqual(lines[1:], ["  1) Science", "  2) History",
                                     "  3) Sports", "  4) Geography"])

    def test_R9_prompt_and_error_mention_the_number_range(self):
        self.assertEqual(game.category_prompt(self.CATEGORIES),
                         "Category (1-4): ")
        self.assertEqual(game.category_error(self.CATEGORIES),
                         "Please type a number from 1 to 4 or a category name.")

    def test_R9_number_selects_category(self):
        for n, name in enumerate(self.CATEGORIES, start=1):
            self.assertEqual(game.parse_category(str(n), self.CATEGORIES), name)
        self.assertEqual(game.parse_category(" 2 ", self.CATEGORIES), "History")

    def test_R9_name_selects_category_case_insensitively(self):
        self.assertEqual(game.parse_category("sports", self.CATEGORIES), "Sports")
        self.assertEqual(game.parse_category("  GEOGRAPHY ", self.CATEGORIES),
                         "Geography")

    def test_R9_invalid_selection_returns_none(self):
        for text in ("", " ", "0", "5", "-1", "1.5", "Art", "Sci", "1 2"):
            self.assertIsNone(game.parse_category(text, self.CATEGORIES),
                              repr(text))


class TestR10OnlySelectedCategory(unittest.TestCase):
    def test_R10_questions_in_returns_only_that_category(self):
        bank = sample_bank()
        science = bank.questions_in("Science")
        self.assertEqual(len(science), 3)
        self.assertTrue(all(q.category == "Science" for q in science))
        self.assertEqual([q.category for q in bank.questions_in("History")],
                         ["History"])

    def test_R10_questions_in_keeps_file_order_and_returns_a_copy(self):
        bank = sample_bank()
        science = bank.questions_in("Science")
        self.assertEqual(science, bank.questions[:3])
        science.clear()
        self.assertEqual(len(bank.questions_in("Science")), 3)


class TestR11CategoryShown(unittest.TestCase):
    def test_R11_question_header_includes_category(self):
        q = Question("Q?", ["a", "b", "c", "d"], 0, "History")
        header = game.format_question(q, 2, 5).splitlines()[0]
        self.assertEqual(header, "Question 2 of 5 \u2014 History")

    def test_R11_round_banner_names_category(self):
        self.assertEqual(game.category_banner("Sports"), "Category: Sports")


class TestR12EmptyCategory(unittest.TestCase):
    def test_R12_declared_category_may_have_no_questions(self):
        bank = game.parse_bank(bank_data(q_item(),
                                         categories=("Science", "Sports")))
        self.assertEqual(bank.categories, ["Science", "Sports"])
        self.assertEqual(bank.questions_in("Sports"), [])

    def test_R12_message_names_category_and_suggests_another(self):
        self.assertEqual(
            game.no_questions_message("Sports"),
            "There are no questions in Sports yet. "
            "Please choose another category.")


if __name__ == "__main__":
    unittest.main()
