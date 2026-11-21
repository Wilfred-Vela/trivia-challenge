# Trivia Challenge — Specification

## Overview
A multiple-choice trivia game that runs in a terminal. Questions are read from
a local JSON file and grouped into categories; the player picks a category at
the start of every game. Built with the Python 3 standard library only.

Run: `python3 -m trivia`

## Requirements
Requirement IDs come from `problem.md`. Each has at least one test in `tests/`
whose name contains the ID (e.g. `test_R3_...`).

| ID | Requirement | Behaviour in this build |
|----|-------------|-------------------------|
| R1 | Runs in the terminal with one command; no internet, API key, account or paid service. | `python3 -m trivia` starts the game. Only standard-library modules are imported. Questions come from `trivia/questions.json`, read from disk. |
| R2 | Displays trivia questions with multiple-choice answers. | Each question is shown with its number, its category (see R11), its text, and four options labelled `A)`–`D)`. |
| R3 | Player selects an answer by typing its letter (A–D). | Input is trimmed and case-insensitive (`b`, ` B ` are accepted). Anything else (empty, `E`, `AB`, `1`) is rejected with a message and the same question is asked again. |
| R4 | Tells the player whether the answer is correct or incorrect. | After each answer: `Correct!` or `Incorrect. The correct answer was C) <text>.` |
| R5 | Keeps track of the player's score. | One point per correct answer; the running score is shown after each answer (`Score: 2/3`). |
| R6 | Displays the final score when all questions are answered. | After the last question: `Final score: X out of N.` |
| R7 | Player can play again without restarting the program. | After the final score the game asks `Play again? (y/n)`. `y`/`yes` returns to the category menu (R9) and starts a new round with the score reset to 0; `n`/`no` exits. Other input is rejected and the question repeated. |
| R8 | Questions are organised into categories (e.g. Science, History, Sports, Geography). | The question file declares an ordered list of categories, and every question names exactly one of them (see *Question file format*). The bundled file has Science, History, Sports and Geography. |
| R9 | Player selects a category before starting a game. | Before each round the game prints `Choose a category:` and the declared categories numbered `1)`, `2)`, … in file order, then prompts `Category (1-N): `. The player may type the number or the category name (trimmed, case-insensitive). Anything else is rejected with `Please type a number from 1 to N or a category name.` and the menu prompt is repeated. |
| R10 | Only questions in the selected category are displayed. | A round asks every question of the selected category once, in shuffled order, and no others. `Question X of N` counts only that category's questions. |
| R11 | The selected category is displayed during gameplay. | The round starts with `Category: <name>`, and every question header reads `Question X of N — <name>`. |
| R12 | Categories with no available questions get a helpful message. | Empty categories still appear in the menu. Choosing one prints `There are no questions in <name> yet. Please choose another category.` and the menu is shown again; no round starts and the score is not affected. |

## Question file format
`trivia/questions.json` is a JSON object with two keys:

```json
{
  "categories": ["Science", "History", "Sports", "Geography"],
  "questions": [
    {
      "category": "Geography",
      "question": "What is the capital of France?",
      "choices": ["Berlin", "Madrid", "Paris", "Rome"],
      "answer": "C"
    }
  ]
}
```

- `categories`: non-empty array of non-empty strings, no duplicates (compared
  case-insensitively). Order is the menu order. A category may have no
  questions (R12).
- `questions`: array with at least one question. Each element:
  - `category`: exactly one of the names in `categories` (exact spelling).
  - `question`: non-empty string.
  - `choices`: exactly four non-empty strings, shown as A, B, C, D in order.
  - `answer`: one of `"A"`, `"B"`, `"C"`, `"D"` (case-insensitive).

The Round 1 format (a bare JSON array of questions) is no longer accepted; it
is reported as a malformed file.

A malformed file causes a clear error message and a non-zero exit, not a traceback.

## Additional behaviour
- Question order is shuffled at the start of each round so replays differ.
- At least one question is required in the whole file, so the category menu
  always has a playable choice.
- If input ends (EOF / Ctrl-D) or the player presses Ctrl-C, the game prints
  `Goodbye!` and exits cleanly.

## Design
- `trivia/game.py` — pure logic, no `input()`/`print()`: loading and validating
  the question bank (`QuestionBank` = categories + questions), formatting the
  category menu, parsing a category choice, selecting a category's questions,
  formatting a question, parsing a letter, checking an answer, score
  tracking, parsing the play-again reply.
- `trivia/cli.py` — the game loop: category menu, then a round, then play
  again. Takes `input_fn` and `output_fn` parameters (defaulting to `input`
  and `print`) so tests can drive it with scripted input.
- `trivia/__main__.py` — entry point for `python3 -m trivia`.

## Out of scope (this build)
An "all categories" mixed mode, choosing more than one category per game,
difficulty levels, timers, high-score persistence, network question sources.
