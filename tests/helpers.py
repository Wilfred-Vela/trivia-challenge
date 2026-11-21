"""Shared helpers for driving the game loop with scripted input."""

from trivia.game import Question, QuestionBank


def sample_questions():
    """The Science Easy questions in sample_bank(). Answers: B, C, A."""
    return [
        Question("What is 2 + 2?", ["3", "4", "5", "6"], 1, "Science", "Easy"),
        Question("Which planet is known as the Red Planet?",
                 ["Venus", "Jupiter", "Mars", "Saturn"], 2, "Science", "Easy"),
        Question("What colour do you get by mixing blue and yellow?",
                 ["Green", "Purple", "Orange", "Brown"], 0, "Science", "Easy"),
    ]


def medium_science_question():
    """The only Science Medium question in sample_bank(). Answer: D."""
    return Question("What is the chemical symbol for sodium?",
                    ["S", "So", "Sd", "Na"], 3, "Science", "Medium")


def history_question():
    return Question("In which year did humans first land on the Moon?",
                    ["1965", "1969", "1972", "1959"], 1, "History", "Easy")


def sample_bank():
    """Menu: 1) Science (3 Easy, 1 Medium, no Hard), 2) History (1 Easy),
    3) Sports (empty)."""
    return QuestionBank(["Science", "History", "Sports"],
                        sample_questions() + [history_question(),
                                              medium_science_question()])


def no_shuffle(items):
    """Keep question order fixed so tests are deterministic."""


class Script:
    """Fake terminal: feeds scripted lines to input_fn, collects output_fn text."""

    def __init__(self, *lines):
        self._lines = list(lines)
        self.output = []
        self.prompts = []

    def input_fn(self, prompt=""):
        self.prompts.append(prompt)
        if not self._lines:
            raise EOFError
        return self._lines.pop(0)

    def output_fn(self, text=""):
        self.output.append(str(text))

    @property
    def text(self):
        return "\n".join(self.output)
