"""Shared helpers for driving the game loop with scripted input."""

from trivia.game import Question


def sample_questions():
    return [
        Question("What is 2 + 2?", ["3", "4", "5", "6"], 1),
        Question("Which planet is known as the Red Planet?",
                 ["Venus", "Jupiter", "Mars", "Saturn"], 2),
        Question("What colour do you get by mixing blue and yellow?",
                 ["Green", "Purple", "Orange", "Brown"], 0),
    ]


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
