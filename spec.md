# Trivia Challenge — Specification

## Overview
A multiple-choice trivia game that runs in a terminal. Questions are read from
a local JSON file, grouped into categories, and each has a difficulty level
(Easy, Medium or Hard) that sets how many points a correct answer earns;
the player picks a category and then a difficulty at
the start of every game. The difficulty menu shows what each level is worth,
and each correct answer shows the points it earned. After each game the player's name and points are
saved to a local top-10 high-score list, which can also be viewed from the
category menu. Built with the Python 3 standard library only.

Run: `python3 -m trivia`

## Requirements
Requirement IDs come from `problem.md`. Each has at least one test in `tests/`
whose name contains the ID (e.g. `test_R3_...`).

| ID | Requirement | Behaviour in this build |
|----|-------------|-------------------------|
| R1 | Runs in the terminal with one command; no internet, API key, account or paid service. | `python3 -m trivia` starts the game. Only standard-library modules are imported. Questions come from `trivia/questions.json`, read from disk. |
| R2 | Displays trivia questions with multiple-choice answers. | Each question is shown with its number, its category and difficulty (see R11, R17), its text, and four options labelled `A)`–`D)`. |
| R3 | Player selects an answer by typing its letter (A–D). | Input is trimmed and case-insensitive (`b`, ` B ` are accepted). Anything else (empty, `E`, `AB`, `1`) is rejected with a message and the same question is asked again. |
| R4 | Tells the player whether the answer is correct or incorrect. | After each answer: `Correct! +<P> point(s)` (R26) or `Incorrect. The correct answer was C) <text>.` (Changed in Round 6: the correct line used to be just `Correct!`.) |
| R5 | A correct answer earns points by the question's difficulty: Easy 1, Medium 3, Hard 5 (changed in Round 4; was 1 point each). | Each correct answer adds the points for that question's difficulty (Easy 1, Medium 3, Hard 5; fixed in the program, see ADR 0004); an incorrect answer adds 0. The score also counts correct answers and questions answered. After each answer the running score is shown as `Score: <P> points (<C> of <A> correct)`, e.g. `Score: 6 points (2 of 3 correct)` after three Medium answers with two right. `points` is `point` when P is exactly 1 (`Score: 1 point (1 of 2 correct)`); 0 is `0 points`. |
| R6 | When all questions are answered, displays the total points and the number answered correctly (changed in Round 4; was correct out of total). | After the last question: `Final score: <P> points (<C> of <N> correct).`, e.g. `Final score: 12 points (4 of 5 correct).` N is the number of questions in the round. The same singular rule as R5 applies: `Final score: 1 point (1 of 3 correct).` |
| R7 | Player can play again without restarting the program. | After the final score, the name prompt (R19) and the high-score list (R22), the game asks `Play again? (y/n)` (changed in Round 5: it used to follow the final score directly). `y`/`yes` returns to the category menu (R9), then the difficulty menu (R14), and starts a new round with the score reset to 0; `n`/`no` exits. Other input is rejected and the question repeated. |
| R8 | Questions are organised into categories (e.g. Science, History, Sports, Geography). | The question file declares an ordered list of categories, and every question names exactly one of them (see *Question file format*). The bundled file has Science, History, Sports, Geography and Literature (changed in Round 6: Literature was added, see R28). |
| R9 | Player selects a category before starting a game. | Before each round the game prints `Choose a category:` and the declared categories numbered `1)`, `2)`, … in file order, followed by one more line, `N+1) High Scores` (R23), then prompts `Category (1-M): `, where M = N+1. The player may type the number or the category name (trimmed, case-insensitive). Anything else is rejected with `Please type a number from 1 to M or a category name.` and the menu prompt is repeated. (Changed in Round 5: the `High Scores` line was added, so M used to be N.) |
| R10 | Only questions in the selected category are displayed. | A round asks only questions of the selected category (narrowed further by difficulty, see R16). |
| R11 | The selected category is displayed during gameplay. | The round starts with `Category: <name>`, and every question header reads `Question X of N — <name> (<difficulty>)` (the difficulty part is R17). |
| R12 | Categories with no available questions get a helpful message. | Empty categories still appear in the menu. Choosing one prints `There are no questions in <name> yet. Please choose another category.` and the menu is shown again; no round starts and the score is not affected. This check happens before the difficulty menu, so a category with no questions at all never reaches it. |
| R13 | Three difficulty levels: Easy, Medium, Hard. | The levels are fixed in the program (not declared in the question file) as `Easy`, `Medium`, `Hard`, in that order (see ADR 0003). |
| R14 | Player selects a difficulty after the category and before the game starts. | After a category with questions is chosen, the game prints `Choose a difficulty for <category>:` followed by `1) Easy (1 point)`, `2) Medium (3 points)`, `3) Hard (5 points)` (R27), `4) Back to categories`, then prompts `Difficulty (1-4): `. The player may type the number or the name (`easy`, `medium`, `hard`, `back`; trimmed, case-insensitive). Anything else is rejected with `Please type a number from 1 to 4 or a difficulty name.` and the prompt is repeated. `4`/`back` shows the category menu again. (Changed in Round 6: the levels used to be listed without their points.) |
| R15 | Every question has an assigned difficulty. | Every question in the file must have a `difficulty` field that is exactly `Easy`, `Medium` or `Hard`; a missing or different value makes the file malformed. |
| R16 | Only questions matching both the selected category and difficulty are displayed. | A round asks every question with the selected category *and* difficulty once, in shuffled order, and no others. `Question X of N` counts only those questions. |
| R17 | The selected difficulty is displayed during gameplay. | The `Category: <name>` banner is followed by `Difficulty: <level>`, and every question header ends with ` (<level>)`, e.g. `Question 2 of 5 — Science (Hard)`. |
| R18 | No questions at the chosen difficulty: helpful message, choose again without crashing. | The game prints `There are no <level> questions in <category> yet.` and `Please choose another difficulty or go back.` (two lines), then shows the difficulty menu for the same category again. The player can pick another level or `4`/`back` to return to the category menu. No round starts and the score is not affected. |
| R19 | After each completed game, ask the player's name and save an entry (name, total points, category, difficulty) to a file. | After the final score (R6) the game prompts `Enter your name for the high scores: `. The reply is trimmed and cut to its first 20 characters (then trimmed again, so a cut name never ends in a space); an empty reply prints `Please type your name.` and the prompt is repeated. The entry (name, points, category, difficulty) is added to the list and the whole list is written to the high-score file (see *High-score file*), default `trivia/highscores.json`, or the path given with `--scores PATH`. The prompt is asked after every completed game, whatever the score. If the file can't be written, the game prints `Could not save high scores: <reason>.` and carries on; the entry still appears in the list for the rest of the session. A game left early (end of input, Ctrl-C) saves nothing. |
| R20 | The list keeps only the top 10 scores. | After an entry is added, only the 10 highest-scoring entries are kept, in memory and in the file. With equal points the older entry ranks higher, so a new score must beat the 10th entry to get in, and an entry that misses the top 10 is dropped. |
| R21 | The list is displayed from highest to lowest score. | `High Scores` followed by one line per entry, highest points first (ties: older first): `{rank:>4}. {name:<20} {points:>3} {unit:<6}  {category} ({difficulty})`, where unit is `point` for exactly 1 and `points` otherwise, e.g. `   1. Ana                   12 points  Science (Hard)` and `   3. Cy                     1 point   Sports (Easy)`. An empty list shows `High Scores` then `No high scores yet.` |
| R22 | The list is shown automatically after each completed game. | Straight after the entry is saved (R19), the list (R21), including the new entry if it made the top 10, is shown, then `Play again? (y/n)` (R7). |
| R23 | The player can view the list from a High Scores option in the menu. | The category menu's last option is `High Scores` (R9). Choosing it by number or by typing `high scores` (trimmed, case-insensitive) shows the list (R21) and then the category menu again; no round starts. A question file may not declare a category named `High Scores` (any case); it is reported as malformed. |
| R24 | If the high-score file doesn't exist, start with an empty list and create the file at the first save. | A missing file is not an error and prints nothing: the list starts empty (`No high scores yet.`). The file is created when the first entry is saved. Its folder is not created; if it is missing, the save fails as in R19. |
| R25 | If the high-score file is corrupted or can't be read, start with an empty list without crashing. | At start-up, after the welcome line, the game prints `High scores could not be read, so the list starts empty.` and the list starts empty. *Corrupted* means anything other than the format under *High-score file*. The bad file is left alone until the first save, which first renames it to `<file>.bak` (replacing any older `.bak`), then writes a fresh file. |
| R26 | After a correct answer, the feedback shows the points earned (Round 6). | A correct answer prints `Correct! +<P> points`, where P is that question's points (R5): `Correct! +3 points` (Medium), `Correct! +5 points` (Hard), and `Correct! +1 point` (Easy; singular for exactly 1, like R5). An incorrect answer is unchanged (R4) and shows no points. The running score line (R5) still follows. |
| R27 | The difficulty menu shows how many points each level is worth (Round 6). | Each level line ends with its points in brackets, from the same table that scores answers (R5, ADR 0007): `  1) Easy (1 point)`, `  2) Medium (3 points)`, `  3) Hard (5 points)`. `  4) Back to categories` has none. The prompt, the error message and typing a level by name (`easy`, not `easy (1 point)`) are unchanged. |
| R28 | The bundled questions include a Literature category; literature questions are in Literature, not History (Round 6). | `trivia/questions.json` declares `Literature` last, after Geography, so the bundled menu is `1) Science` … `4) Geography`, `5) Literature`, `6) High Scores`, prompt `Category (1-6): `. "Who wrote 'Romeo and Juliet'?" moved from History (Easy) to Literature (Easy). Literature has two questions at each level; History gained one Easy question so it still has two at each level. No bundled question outside Literature is about literature. |

## Question file format
`trivia/questions.json` is a JSON object with two keys:

```json
{
  "categories": ["Science", "History", "Sports", "Geography", "Literature"],
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

A category named `High Scores` (compared case-insensitively) is rejected,
since that name is the menu's High Scores option (R23).

## High-score file
`trivia/highscores.json` (or the `--scores` path) is written by the game, not
by hand, and is ignored by git. It is a JSON object (UTF-8):

```json
{
  "scores": [
    {"name": "Ana", "points": 12, "category": "Science", "difficulty": "Hard"}
  ]
}
```

- `scores`: array of entries in rank order (highest points first; ties
  oldest first). It holds at most 10 entries.
- Each entry: `name` is a non-empty string, `points` is a whole number of 0 or
  more (not `true`/`false`), `category` is a non-empty string (it need not be a
  category in the current question file), and `difficulty` is exactly
  `Easy`, `Medium` or `Hard`. Other keys are ignored.
- On loading, the entries are sorted by points (keeping file order for ties)
  and cut to 10.
- A file that is not valid UTF-8 JSON, is not an object with a `scores` array,
  or has any invalid entry counts as corrupted (R25). The whole list is then
  discarded, not just the bad entries. A file that exists but can't be opened
  (e.g. no permission) is treated the same way.
- Saving writes a temporary `<file>.tmp` next to the file and then renames it
  over the file, so an interrupted save never leaves a half-written list.

## Additional behaviour
- Question order is shuffled at the start of each round so replays differ.
- At least one question is required in the whole file, so the category menu
  always has a playable choice.
- If input ends (EOF / Ctrl-D) or the player presses Ctrl-C, the game prints
  `Goodbye!` and exits cleanly.
- `python3 -m trivia --scores PATH` uses a different high-score file. The
  tests always use a temporary file, so they never touch the real list.
- The order of prompts in a game is: category, difficulty, one answer per
  question, name, play again.

## Design
- `trivia/game.py` — pure logic, no `input()`/`print()`: loading and validating
  the question bank (`QuestionBank` = categories + questions), formatting the
  category and difficulty menus, parsing a category or difficulty choice,
  selecting a category's questions (optionally at one difficulty),
  formatting a question, parsing a letter, checking an answer and the
  feedback line, the points each difficulty is worth (`POINTS`, which the
  feedback (R26) and the difficulty menu (R27) also read), score tracking (points, correct,
  answered), parsing the play-again reply. The category menu's `High Scores`
  option is part of the category menu and parser (`game.HIGH_SCORES`).
- `trivia/highscores.py` — high-score logic, also with no `input()`/`print()`:
  the `Entry` record, adding an entry and keeping the top 10, parsing a name,
  formatting the list, and reading/writing the high-score file
  (`load()` reports a missing file as empty, a corrupted one as empty plus a
  flag; `save()` backs up a corrupted file first).
- `trivia/cli.py` — the game loop: load high scores, then category menu
  (which can show the high scores), then difficulty menu (which can go back
  to categories), then a round, then the name prompt, save and high-score
  list, then play again. `run()` takes `scores_path`; with `None` (the
  default, used by tests that don't care about scores) the list is kept in
  memory only and nothing is written. `main()` passes `--scores`, default
  `trivia/highscores.json`. Takes `input_fn` and `output_fn` parameters (defaulting to `input`
  and `print`) so tests can drive it with scripted input.
- `trivia/__main__.py` — entry point for `python3 -m trivia`.

## Out of scope (this build)
An "all categories" mixed mode, choosing more than one category per game,
an "any difficulty" mixed mode, levels other than Easy/Medium/Hard, point values set
in the question file or per question, bonus points (e.g. streaks or speed), timers, network question sources,
separate high-score lists per category or difficulty, deleting or resetting
high scores from inside the game, dates or times on high-score entries.
