# Handoff: end of Round 2

For the session that does the next round. Standing rules for every session
are in `CLAUDE.md`; this file covers what is true **now** and what happened
in Round 2. Read `problem.md`, `spec.md` and `docs/decisions/` as well.

## Current state

- Requirements R1–R12 are implemented. R1–R7 are from Round 1, and R8–R12
  (categories) from Round 2. `spec.md` has a row for each one that describes
  the exact behaviour.
- **73 tests, all passing, none skipped** as of commit `456a152`.
- The working tree was clean at the end of the round, apart from this file and
  the uncommitted `CLAUDE.md` edits, which the owner is reviewing.
- Round 1 left no handoff file. Round 2 worked from the repo alone.

### What the program does
1. Prints `Welcome to Trivia Challenge!`.
2. Shows `Choose a category:` with a numbered menu and prompts
   `Category (1-N): `. The player can type a number or a name; names are
   case-insensitive and surrounding spaces are ignored.
3. If the chosen category has no questions, prints
   `There are no questions in <name> yet. Please choose another category.`
   and shows the menu again.
4. Prints `Category: <name>`, then asks that category's questions once each,
   in shuffled order. Headers read `Question X of N — <name>`.
5. Shows feedback and the running score after each answer, then
   `Final score: X out of N.`
6. `Play again? (y/n)`. Yes goes back to step 2; no prints `Goodbye!`.
   EOF or Ctrl-C at any prompt prints `Goodbye!` and exits 0.

### Code map
- `trivia/game.py` (pure logic, no I/O):
  - `Question(text, choices, answer_index, category)`
  - `QuestionBank(categories, questions)` with `.questions_in(name)`
  - `load_bank(path)` and `parse_bank(data)`, which raise `QuestionFileError`
  - menu helpers: `format_category_menu`, `category_prompt`,
    `category_error`, `parse_category`
  - display text: `category_banner`, `no_questions_message`
  - unchanged from Round 1: `format_question`, `parse_choice`, `is_correct`,
    `feedback`, `Score`, `final_score_message`, `parse_play_again`
- `trivia/cli.py`:
  - `ask()`: generic re-prompt loop
  - `choose_category(bank, ...)`
  - `play_round(questions, category, ...)`
  - `run(bank, input_fn, output_fn, shuffle)`
  - `main(argv)`: handles `--questions PATH`
- `trivia/questions.json`: 4 categories with 19 questions (Science 6,
  History 5, Sports 4, Geography 4).
- `tests/helpers.py`:
  - `sample_bank()`: menu is 1) Science (3 questions, answers B, C, A),
    2) History (1 question, answer B), 3) Sports (empty).
  - `Script`: a fake terminal.
  - `no_shuffle`: keeps question order fixed.
- `tests/test_game_logic.py`: logic tests.
- `tests/test_cli.py`: game-loop tests, plus one subprocess test that runs
  `python3 -m trivia`.

## How to run

```sh
python3 -m trivia                                  # play
python3 -m trivia --questions path/to/file.json    # play with a custom bank
python3 -m unittest discover tests                 # tests (expect 73, OK)
```

To see the empty-category message in the real program, use a file that
declares a category no question uses, e.g.
`{"categories":["Science","Art"],"questions":[{"category":"Science","question":"H2O is?","choices":["Water","Salt","Air","Gold"],"answer":"A"}]}`.

## Decisions made in Round 2, and why

**Confirmed by the owner before any code was written:**
1. **Categories are declared in `questions.json`**, not hard-coded and not
   derived from the questions. This is the only way an empty category can
   exist, which R12 needs. See ADR 0002.
2. **Choosing an empty category** shows a message and then the menu again.
   The program does not exit.
3. **Play again returns to the category menu**, so the player can switch
   category without restarting (R7).
4. **There is no "All categories" option.** This keeps R10 strict.

**Made by the implementer.** The owner was told about these but has not
explicitly approved them:
5. The file is `{"categories": [...], "questions": [...]}`, and each question
   has a `category` field. Nesting questions under category keys was
   rejected; ADR 0002 explains why.
6. Round 1 bare-array files are rejected with a clear error. They are not
   loaded as uncategorised questions.
7. A question's `category` must match a declared name exactly. Duplicate
   names are rejected, comparing case-insensitively. The file needs at least
   one question, so the menu can never contain only empty categories.
8. Menu input accepts a number or a name. Only ASCII digits count, so `²`
   is rejected instead of crashing `int()`.
9. All new on-screen wording, the `—` header suffix and the `Category:`
   banner. Empty categories are not marked in the menu. The final score line
   does not name the category.
10. The existing 12 questions were sorted into categories and 7 were added.
    None of the bundled categories is empty.
11. Renamed `load_questions`/`parse_questions` to `load_bank`/`parse_bank`,
    and changed the signatures of `run()` and `play_round()`. The Round 1
    tests that used them were updated.

## Unresolved

- Owner reviewed decisions 5–11 on Nov 21 and accepts all of them.
- "Romeo and Juliet" stays under History for now; owner may fix it in a later round.
- Owner confirms: no empty category in the bundled file; R12 is shown through tests and custom files.

## Warnings for the next session

- **Two commits fail the test suite on purpose.** `ae66ed2` (tests first) and
  `b03ac75` (logic before the game loop) fail. The suite passes from
  `3ad62ba` onward. Keep this in mind if you use `git bisect`, and don't try
  to "fix" these commits; history must not be rewritten.
- **The subprocess test `test_R1_python_m_trivia_runs_a_full_game`** sends
  `"1\n" + "A\n" * 200 + "n\n"`. If you add any prompt before or between
  rounds, such as a difficulty or player name, this input must change too.
  The same goes for the `run_game(SCIENCE, ...)` calls in `tests/test_cli.py`,
  which assume the category choice is the first input.
- **Tests compare exact output strings**, including the em dash `—` (U+2014)
  in question headers. Any change to the wording means updating `spec.md` and
  the tests in the same change.
- **`Question.category` defaults to `""`** so tests can build questions
  briefly. Questions loaded from a file always have a real category. A
  question without one prints a header with no category suffix.
- **`QuestionBank.questions_in()` returns a new list.** `run()` shuffles that
  copy in place, and the bank's own order is never changed. Keep it that way
  if you refactor.
- **Old question files no longer load.** Anyone with a Round 1-format custom
  file has to add `categories` and per-question `category` fields.
- `spec.md`'s "Out of scope" section lists mixed-category mode, multiple
  categories per game, difficulty, timers, high scores and network sources.
  Check that section against the new round's requirements and update it.
