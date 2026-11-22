"""Pure game logic. Nothing in this module reads input or prints output."""

import json
import os
from dataclasses import dataclass

LETTERS = ("A", "B", "C", "D")
# Fixed in the program, not declared in the question file (ADR 0003).
DIFFICULTIES = ("Easy", "Medium", "Hard")
# Points a correct answer earns at each difficulty (R5, ADR 0004).
POINTS = {"Easy": 1, "Medium": 3, "Hard": 5}
# Returned by parse_difficulty() for the menu's "Back to categories" option.
BACK = "Back"
# Returned by parse_category() for the category menu's last option (R23).
HIGH_SCORES = "High Scores"
DIFFICULTY_PROMPT = f"Difficulty (1-{len(DIFFICULTIES) + 1}): "
DIFFICULTY_ERROR = (f"Please type a number from 1 to {len(DIFFICULTIES) + 1} "
                    "or a difficulty name.")
DEFAULT_QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "questions.json")


class QuestionFileError(Exception):
    """The question file is missing, unreadable, or malformed."""


@dataclass
class Question:
    text: str
    choices: list
    answer_index: int
    category: str = ""
    difficulty: str = ""


@dataclass
class QuestionBank:
    """Declared categories (in menu order) and every question in the file."""
    categories: list
    questions: list

    def questions_in(self, category, difficulty=None):
        """A new list of the questions in ``category`` (and, if given, at
        ``difficulty``), in file order."""
        return [q for q in self.questions if q.category == category
                and (difficulty is None or q.difficulty == difficulty)]


def load_bank(path):
    """Read and validate the JSON question file at ``path``."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise QuestionFileError(f"cannot read {path}: {e.strerror or e}") from e
    except json.JSONDecodeError as e:
        raise QuestionFileError(f"{path} is not valid JSON: {e}") from e
    return parse_bank(data)


def parse_bank(data):
    """Turn decoded JSON into a QuestionBank, validating every field."""
    if not isinstance(data, dict):
        raise QuestionFileError(
            "question file must be a JSON object with 'categories' and "
            "'questions' keys (see spec.md)")
    categories = _parse_categories(data.get("categories"))
    items = data.get("questions")
    if not isinstance(items, list) or not items:
        raise QuestionFileError("'questions' must be a non-empty JSON array")
    questions = [_parse_question(n, item, categories)
                 for n, item in enumerate(items, start=1)]
    return QuestionBank(categories, questions)


def _parse_categories(categories):
    if (not isinstance(categories, list) or not categories
            or not all(isinstance(c, str) and c.strip() for c in categories)):
        raise QuestionFileError(
            "'categories' must be a non-empty array of non-empty strings")
    seen = set()
    for name in categories:
        if name.lower() == HIGH_SCORES.lower():
            raise QuestionFileError(
                f"category '{name}' is reserved for the High Scores menu option")
        if name.lower() in seen:
            raise QuestionFileError(f"category '{name}' is listed more than once")
        seen.add(name.lower())
    return list(categories)


def _parse_question(n, item, categories):
    if not isinstance(item, dict):
        raise QuestionFileError(f"question {n}: must be a JSON object")
    category = item.get("category")
    if category not in categories:
        raise QuestionFileError(
            f"question {n}: 'category' must be one of {', '.join(categories)}"
            f" (got {category!r})")
    difficulty = item.get("difficulty")
    if difficulty not in DIFFICULTIES:
        raise QuestionFileError(
            f"question {n}: 'difficulty' must be one of {', '.join(DIFFICULTIES)}"
            f" (got {difficulty!r})")
    text = item.get("question")
    choices = item.get("choices")
    answer = item.get("answer")
    if not isinstance(text, str) or not text.strip():
        raise QuestionFileError(f"question {n}: 'question' must be a non-empty string")
    if (not isinstance(choices, list) or len(choices) != len(LETTERS)
            or not all(isinstance(c, str) and c.strip() for c in choices)):
        raise QuestionFileError(f"question {n}: 'choices' must be 4 non-empty strings")
    if not isinstance(answer, str) or answer.strip().upper() not in LETTERS:
        raise QuestionFileError(f"question {n}: 'answer' must be one of A, B, C, D")
    return Question(text, list(choices), LETTERS.index(answer.strip().upper()),
                    category, difficulty)


def format_category_menu(categories):
    """The numbered list of categories shown before each round (R9), with
    High Scores as the last option (R23)."""
    options = list(categories) + [HIGH_SCORES]
    lines = ["Choose a category:"]
    lines += [f"  {n}) {name}" for n, name in enumerate(options, start=1)]
    return "\n".join(lines)


def category_prompt(categories):
    return f"Category (1-{len(categories) + 1}): "


def category_error(categories):
    return (f"Please type a number from 1 to {len(categories) + 1} "
            "or a category name.")


def parse_category(text, categories):
    """Map a typed menu number or name (case-insensitive) to a category name,
    HIGH_SCORES for the last option, or None if it matches nothing."""
    options = list(categories) + [HIGH_SCORES]
    reply = text.strip()
    if reply.isascii() and reply.isdigit() and 1 <= int(reply) <= len(options):
        return options[int(reply) - 1]
    for name in options:
        if reply.lower() == name.lower():
            return name
    return None


def category_banner(category):
    return f"Category: {category}"


def no_questions_message(category):
    return (f"There are no questions in {category} yet. "
            "Please choose another category.")


def format_difficulty_menu(category):
    """The numbered difficulty list, plus a way back, shown after a category
    is chosen (R13, R14)."""
    options = list(DIFFICULTIES) + ["Back to categories"]
    lines = [f"Choose a difficulty for {category}:"]
    lines += [f"  {n}) {name}" for n, name in enumerate(options, start=1)]
    return "\n".join(lines)


def parse_difficulty(text):
    """Map a typed menu number or name (case-insensitive) to a difficulty,
    BACK for the last option, or None if it matches nothing."""
    options = DIFFICULTIES + (BACK,)
    reply = text.strip()
    if reply.isascii() and reply.isdigit() and 1 <= int(reply) <= len(options):
        return options[int(reply) - 1]
    for name in options:
        if reply.lower() == name.lower():
            return name
    return None


def difficulty_banner(difficulty):
    return f"Difficulty: {difficulty}"


def no_questions_at_difficulty_message(category, difficulty):
    return (f"There are no {difficulty} questions in {category} yet.\n"
            "Please choose another difficulty or go back.")


def format_question(question, number, total):
    """Return the question header, text and lettered choices as one string.
    The header names the question's category (R11) and difficulty (R17)
    when it has them."""
    header = f"Question {number} of {total}"
    if question.category:
        header += f" — {question.category}"
    if question.difficulty:
        header += f" ({question.difficulty})"
    lines = [header, question.text]
    lines += [f"  {letter}) {choice}" for letter, choice in zip(LETTERS, question.choices)]
    return "\n".join(lines)


def parse_choice(text):
    """Map a typed letter (case-insensitive) to a choice index, or None if invalid."""
    letter = text.strip().upper()
    return LETTERS.index(letter) if letter in LETTERS else None


def is_correct(question, choice_index):
    return choice_index == question.answer_index


def feedback(question, choice_index):
    if is_correct(question, choice_index):
        return "Correct!"
    i = question.answer_index
    return f"Incorrect. The correct answer was {LETTERS[i]}) {question.choices[i]}."


def points_for(question):
    """The points a correct answer to ``question`` earns (R5)."""
    return POINTS[question.difficulty]


def _points_text(points):
    return f"{points} point" if points == 1 else f"{points} points"


class Score:
    """Running tally for one round: points earned, correct answers, and
    questions answered."""

    def __init__(self):
        self.points = 0
        self.correct = 0
        self.answered = 0

    def record(self, was_correct, points):
        """Count one answer; a correct one adds ``points``."""
        self.answered += 1
        if was_correct:
            self.correct += 1
            self.points += points

    def running_text(self):
        return (f"Score: {_points_text(self.points)} "
                f"({self.correct} of {self.answered} correct)")


def final_score_message(score):
    return (f"Final score: {_points_text(score.points)} "
            f"({score.correct} of {score.answered} correct).")


def parse_play_again(text):
    """True for yes, False for no, None if the reply isn't recognised."""
    reply = text.strip().lower()
    if reply in ("y", "yes"):
        return True
    if reply in ("n", "no"):
        return False
    return None
