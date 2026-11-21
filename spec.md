# Trivia Challenge — Specification

## Overview
A multiple-choice trivia game that runs in a terminal. Questions are read from
a local JSON file. Built with the Python 3 standard library only.

Run: `python3 -m trivia`

## Requirements
Requirement IDs come from `problem.md`. Each has at least one test in `tests/`
whose name contains the ID (e.g. `test_R3_...`).

| ID | Requirement | Behaviour in this build |
|----|-------------|-------------------------|
| R1 | Runs in the terminal with one command; no internet, API key, account or paid service. | `python3 -m trivia` starts the game. Only standard-library modules are imported. Questions come from `trivia/questions.json`, read from disk. |
| R2 | Displays trivia questions with multiple-choice answers. | Each question is shown with its number, its text, and four options labelled `A)`–`D)`. |
| R3 | Player selects an answer by typing its letter (A–D). | Input is trimmed and case-insensitive (`b`, ` B ` are accepted). Anything else (empty, `E`, `AB`, `1`) is rejected with a message and the same question is asked again. |
| R4 | Tells the player whether the answer is correct or incorrect. | After each answer: `Correct!` or `Incorrect. The correct answer was C) <text>.` |
| R5 | Keeps track of the player's score. | One point per correct answer; the running score is shown after each answer (`Score: 2/3`). |
| R6 | Displays the final score when all questions are answered. | After the last question: `Final score: X out of N.` |
| R7 | Player can play again without restarting the program. | After the final score the game asks `Play again? (y/n)`. `y`/`yes` starts a new round with the score reset to 0; `n`/`no` exits. Other input is rejected and the question repeated. |

## Question file format
`trivia/questions.json` is a JSON array. Each element:

```json
{
  "question": "What is the capital of France?",
  "choices": ["Berlin", "Madrid", "Paris", "Rome"],
  "answer": "C"
}
```

- `question`: non-empty string.
- `choices`: exactly four non-empty strings, shown as A, B, C, D in order.
- `answer`: one of `"A"`, `"B"`, `"C"`, `"D"`.

A malformed file causes a clear error message and a non-zero exit, not a traceback.

## Additional behaviour
- Question order is shuffled at the start of each round so replays differ.
- If input ends (EOF / Ctrl-D) or the player presses Ctrl-C, the game prints
  `Goodbye!` and exits cleanly.

## Design
- `trivia/game.py` — pure logic, no `input()`/`print()`: loading and validating
  questions, formatting a question, parsing a letter, checking an answer,
  score tracking, parsing the play-again reply.
- `trivia/cli.py` — the game loop. Takes `input_fn` and `output_fn` parameters
  (defaulting to `input` and `print`) so tests can drive it with scripted input.
- `trivia/__main__.py` — entry point for `python3 -m trivia`.

## Out of scope (this build)
Categories, difficulty levels, timers, high-score persistence, network question
sources.
