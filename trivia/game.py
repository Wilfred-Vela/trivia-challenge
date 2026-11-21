"""Pure game logic. Nothing in this module reads input or prints output."""

import json
import os
from dataclasses import dataclass

LETTERS = ("A", "B", "C", "D")
DEFAULT_QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "questions.json")


class QuestionFileError(Exception):
    """The question file is missing, unreadable, or malformed."""


@dataclass
class Question:
    text: str
    choices: list
    answer_index: int


def load_questions(path):
    """Read and validate the JSON question file at ``path``."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise QuestionFileError(f"cannot read {path}: {e.strerror or e}") from e
    except json.JSONDecodeError as e:
        raise QuestionFileError(f"{path} is not valid JSON: {e}") from e
    return parse_questions(data)


def parse_questions(data):
    """Turn decoded JSON into a list of Question, validating every field."""
    if not isinstance(data, list) or not data:
        raise QuestionFileError("question file must be a non-empty JSON array")
    questions = []
    for n, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise QuestionFileError(f"question {n}: must be a JSON object")
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
        questions.append(Question(text, list(choices),
                                  LETTERS.index(answer.strip().upper())))
    return questions


def format_question(question, number, total):
    """Return the question header, text and lettered choices as one string."""
    lines = [f"Question {number} of {total}", question.text]
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


class Score:
    """Running tally for one round."""

    def __init__(self):
        self.correct = 0
        self.answered = 0

    def record(self, was_correct):
        self.answered += 1
        if was_correct:
            self.correct += 1

    def running_text(self):
        return f"Score: {self.correct}/{self.answered}"


def final_score_message(score):
    return f"Final score: {score.correct} out of {score.answered}."


def parse_play_again(text):
    """True for yes, False for no, None if the reply isn't recognised."""
    reply = text.strip().lower()
    if reply in ("y", "yes"):
        return True
    if reply in ("n", "no"):
        return False
    return None
