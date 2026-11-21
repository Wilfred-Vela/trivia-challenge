# Trivia Challenge — Specification

## Overview
A multiple-choice trivia game that runs in a terminal. Questions are read from
a local JSON file, grouped into categories, and each has a difficulty level
(Easy, Medium or Hard); the player picks a category and then a difficulty at
the start of every game. Built with the Python 3 standard library only.

Run: `python3 -m trivia`

## Requirements
Requirement IDs come from `problem.md`. Each has at least one test in `tests/`
whose name contains the ID (e.g. `test_R3_...`).

| ID | Requirement | Behaviour in this build |
|----|-------------|-------------------------|
| R1 | Runs in the terminal with one command; no internet, API key, account or paid service. | `python3 -m trivia` starts the game. Only standard-library modules are imported. Questions come from `trivia/questions.json`, read from disk. |
| R2 | Displays trivia questions with multiple-choice answers. | Each question is shown with its number, its category and difficulty (see R11, R17), its text, and four options labelled `A)`–`D)`. |
| R3 | Player selects an answer by typing its letter (A–D). | Input is trimmed and case-insensitive (`b`, ` B ` are accepted). Anything else (empty, `E`, `AB`, `1`) is rejected with a message and the same question is asked again. |
| R4 | Tells the player whether the answer is correct or incorrect. | After each answer: `Correct!` or `Incorrect. The correct answer was C) <text>.` |
| R5 | Keeps track of the player's score. | One point per correct answer; the running score is shown after each answer (`Score: 2/3`). |
| R6 | Displays the final score when all questions are answered. | After the last question: `Final score: X out of N.` |
| R7 | Player can play again without restarting the program. | After the final score the game asks `Play again? (y/n)`. `y`/`yes` returns to the category menu (R9), then the difficulty menu (R14), and starts a new round with the score reset to 0; `n`/`no` exits. Other input is rejected and the question repeated. |
| R8 | Questions are organised into categories (e.g. Science, History, Sports, Geography). | The question file declares an ordered list of categories, and every question names exactly one of them (see *Question file format*). The bundled file has Science, History, Sports and Geography. |
| R9 | Player selects a category before starting a game. | Before each round the game prints `Choose a category:` and the declared categories numbered `1)`, `2)`, … in file order, then prompts `Category (1-N): `. The player may type the number or the category name (trimmed, case-insensitive). Anything else is rejected with `Please type a number from 1 to N or a category name.` and the menu prompt is repeated. |
| R10 | Only questions in the selected category are displayed. | A round asks only questions of the selected category (narrowed further by difficulty, see R16). |
| R11 | The selected category is displayed during gameplay. | The round starts with `Category: <name>`, and every question header reads `Question X of N — <name> (<difficulty>)` (the difficulty part is R17). |
| R12 | Categories with no available questions get a helpful message. | Empty categories still appear in the menu. Choosing one prints `There are no questions in <name> yet. Please choose another category.` and the menu is shown again; no round starts and the score is not affected. This check happens before the difficulty menu, so a category with no questions at all never reaches it. |
| R13 | Three difficulty levels: Easy, Medium, Hard. | The levels are fixed in the program (not declared in the question file) as `Easy`, `Medium`, `Hard`, in that order (see ADR 0003). |
| R14 | Player selects a difficulty after the category and before the game starts. | After a category with questions is chosen, the game prints `Choose a difficulty for <category>:` followed by `1) Easy`, `2) Medium`, `3) Hard`, `4) Back to categories`, then prompts `Difficulty (1-4): `. The player may type the number or the name (`easy`, `medium`, `hard`, `back`; trimmed, case-insensitive). Anything else is rejected with `Please type a number from 1 to 4 or a difficulty name.` and the prompt is repeated. `4`/`back` shows the category menu again. |
| R15 | Every question has an assigned difficulty. | Every question in the file must have a `difficulty` field that is exactly `Easy`, `Medium` or `Hard`; a missing or different value makes the file malformed. |
| R16 | Only questions matching both the selected category and difficulty are displayed. | A round asks every question with the selected category *and* difficulty once, in shuffled order, and no others. `Question X of N` counts only those questions. |
| R17 | The selected difficulty is displayed during gameplay. | The `Category: <name>` banner is followed by `Difficulty: <level>`, and every question header ends with ` (<level>)`, e.g. `Question 2 of 5 — Science (Hard)`. |
| R18 | No questions at the chosen difficulty: helpful message, choose again without crashing. | The game prints `There are no <level> questions in <category> yet.` and `Please choose another difficulty or go back.` (two lines), then shows the difficulty menu for the same category again. The player can pick another level or `4`/`back` to return to the category menu. No round starts and the score is not affected. |

## Question file format
`trivia/questions.json` is a JSON object with two keys:

```json
{
  "categories": ["Science", "History", "Sports", "Geography"],
  "questions": [
    {
      "category": "Geography",
      "difficulty": "Easy",
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
  - `difficulty`: exactly one of `"Easy"`, `"Medium"`, `"Hard"` (exact
    spelling, like `category`).
  - `question`: non-empty string.
  - `choices`: exactly four non-empty strings, shown as A, B, C, D in order.
  - `answer`: one of `"A"`, `"B"`, `"C"`, `"D"` (case-insensitive).

The Round 1 format (a bare JSON array of questions) is no longer accepted; it
is reported as a malformed file. Round 2 files (no `difficulty` fields) are
also rejected, with an error naming the question and the `difficulty` field.

The bundled file has at least two questions for every category at every
difficulty, so the R18 message is shown through tests and custom files.

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
  category and difficulty menus, parsing a category or difficulty choice,
  selecting a category's questions (optionally at one difficulty),
  formatting a question, parsing a letter, checking an answer, score
  tracking, parsing the play-again reply.
- `trivia/cli.py` — the game loop: category menu, then difficulty menu
  (which can go back to categories), then a round, then play again. Takes `input_fn` and `output_fn` parameters (defaulting to `input`
  and `print`) so tests can drive it with scripted input.
- `trivia/__main__.py` — entry point for `python3 -m trivia`.

## Out of scope (this build)
An "all categories" mixed mode, choosing more than one category per game,
an "any difficulty" mixed mode, levels other than Easy/Medium/Hard, scoring
that depends on difficulty, timers, high-score persistence, network question sources.
