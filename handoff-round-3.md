# Handoff: end of Round 3

This is for the session that does the next round. Standing rules for every
session are in `CLAUDE.md`. This file covers what is true **now** and what
happened in Round 3. Also read `problem.md`, `spec.md` and `docs/decisions/`
(ADRs 0001–0003).

## Current state

- Requirements R1–R18 are implemented:
  - R1–R7 (Round 1): the basic game.
  - R8–R12 (Round 2): categories.
  - R13–R18 (Round 3): difficulty levels.
- `spec.md` has a row for every requirement giving the exact behaviour and
  wording.
- **107 tests, all passing, none skipped**, as of commit `c93bf96`.
- The working tree was clean at the end of the round, except for this file and
  the uncommitted `CLAUDE.md` edits, which the owner is reviewing.

### What the program does
1. Prints `Welcome to Trivia Challenge!`.
2. **Category menu.** Shows `Choose a category:` with a numbered menu and the
   prompt `Category (1-N): `. The player types a number or a name (any case,
   surrounding spaces ignored). If the category has no questions at all, the
   game prints the R12 message and shows the category menu again.
3. **Difficulty menu.** Shows `Choose a difficulty for <category>:` with
   `1) Easy`, `2) Medium`, `3) Hard`, `4) Back to categories` and the prompt
   `Difficulty (1-4): `. The player types a number or a name (`easy`,
   `medium`, `hard`, `back`), in any case.
   - `4`/`back` returns to step 2.
   - If the category has no questions at that level, the game prints
     `There are no <level> questions in <category> yet.` and
     `Please choose another difficulty or go back.`, then shows the
     difficulty menu again (R18).
4. **The round.** Prints `Category: <name>` and then `Difficulty: <level>`.
   It asks each question of that category and level once, in shuffled order.
   Headers read `Question X of N — <category> (<level>)`.
5. Shows feedback and the running score after each answer, then
   `Final score: X out of N.` This line is unchanged and does not name the
   category or the level.
6. Asks `Play again? (y/n)`. Yes goes back to step 2, so both menus are shown
   again and nothing is remembered from the last round. No prints `Goodbye!`.
   EOF or Ctrl-C at any prompt prints `Goodbye!` and exits 0.

### Code map
- `trivia/game.py` (pure logic, no I/O):
  - Constants: `DIFFICULTIES = ("Easy", "Medium", "Hard")`, `BACK = "Back"`
    (the sentinel for the menu's 4th option), `DIFFICULTY_PROMPT`,
    `DIFFICULTY_ERROR`.
  - `Question(text, choices, answer_index, category="", difficulty="")`.
  - `QuestionBank(categories, questions)`, with
    `.questions_in(category, difficulty=None)`. Leaving out `difficulty`
    gives every question in the category.
  - `load_bank` / `parse_bank`. These now also validate `difficulty`.
  - New in Round 3: `format_difficulty_menu(category)`,
    `parse_difficulty(text)` (returns a level, `BACK` or `None`),
    `difficulty_banner`, `no_questions_at_difficulty_message`.
  - `format_question` appends ` (<level>)` when the question has a
    difficulty.
  - Unchanged from earlier rounds: the category menu helpers, the scoring
    functions and the play-again parsing.
- `trivia/cli.py`:
  - `ask()`.
  - `choose_category(bank, ...)`.
  - New: `choose_difficulty(bank, category, ...)`. Returns `None` for Back.
  - `play_round(questions, category, difficulty, ...)`. The `difficulty`
    argument is new.
  - `run()` and `main(argv)`, with `--questions PATH`.
- `trivia/questions.json`: 4 categories and 26 questions. Every
  category × level has at least 2; History Hard and Geography Easy have 3.
  Questions are grouped by category, then by level.
- `tests/helpers.py`, `sample_bank()`:
  - 1) Science: 3 Easy (answers B, C, A) and 1 Medium
    (`medium_science_question()`, answer D). There is no Science Hard.
  - 2) History: 1 Easy (answer B). There is no Medium or Hard.
  - 3) Sports: no questions at all.
  - The Medium question comes **after** the History question in
    `bank.questions`.
- `tests/test_cli.py`:
  - Constants: `SCIENCE`, `HISTORY`, `SPORTS` = `"1"`, `"2"`, `"3"`, and
    `EASY`, `MEDIUM`, `HARD`, `BACK` = `"1"` to `"4"`.
  - `run_game(...)` takes the category choice, then the difficulty choice,
    then the answers.

## How to run

```sh
python3 -m trivia                                  # play
python3 -m trivia --questions path/to/file.json    # play with a custom bank
python3 -m unittest discover tests                 # tests (expect 107, OK)
```

The bundled file has no empty category and no empty level. To see the R12 and
R18 messages in the real program, use a custom file such as:

```json
{"categories":["Science","Art"],"questions":[{"category":"Science","difficulty":"Easy","question":"H2O is?","choices":["Water","Salt","Air","Gold"],"answer":"A"}]}
```

With this file, Science → Hard shows R18 and Art shows R12.

## Decisions made in Round 3, and why

**Confirmed by the owner before any code was written:**
1. **R18 navigation is a `4) Back to categories` option** that is always in
   the difficulty menu. After the R18 message the difficulty menu is shown
   again, so one menu covers both "another difficulty" and "another
   category". The rejected alternatives were a separate follow-up question
   ((d)ifficulty or (c)ategory?) and always jumping back to categories.
2. **`difficulty` is required on every question.** A missing value is a
   malformed file. It does not default to Medium. This matches how
   `category` was handled in Round 2.
3. **The bundled file was filled out** so every category has at least 2
   questions at every level. R18 is shown through tests and custom files, as
   R12 is.

**Made by the implementer.** The owner was given this list at the end of the
round but has not explicitly approved it:

4. **The levels are fixed in code** and are not declared in the file the way
   categories are. Without this, R13 could break or R18 could never happen.
   See ADR 0003.
5. **The `difficulty` value must be spelt exactly** (`Easy`, not `easy`),
   matching the rule for `category`. Round 2 files no longer load, and the
   error names the question and the field.
6. **All new on-screen wording** (listed in `spec.md` R14, R17, R18). The R18
   text is the two lines from the preview the owner chose.
7. **The menu accepts a number or a name**, including `back`. Only ASCII
   digits count, the same as the category menu.
8. **How the difficulty is shown:**
   - A separate `Difficulty:` line follows the `Category:` banner. This keeps
     the Round 2 banner line unchanged.
   - Headers gain the ` (<level>)` suffix. This changed the R11 header test.
9. **The R12 check runs before the difficulty menu.** Every category shows all
   three levels, and empty levels are not marked.
10. **Play again goes back to the category menu.** It does not reuse the last
    category or level.
11. **The final score line is unchanged.**
12. **Levels assigned to the 19 existing questions** are the implementer's
    judgement. 7 questions were added: History Hard ×2, Sports Hard ×2,
    Geography Medium ×1, Geography Hard ×2.
13. **The sample bank gained a Science Medium question.** Two Round 2 R10
    logic tests now expect 4 Science questions instead of 3.

## Unresolved

- Owner reviewed decisions 4–13 on Nov 21 and accepts all of them.
- Difficulty assignments for questions are accepted as they are for now.
- "Romeo and Juliet" stays under History for now.

## Warnings for the next session

- **Four commits fail the test suite on purpose:**
  - Round 2: `ae66ed2` and `b03ac75`.
  - Round 3: `e8b1ebf` (tests first) and `7091c12` (logic before the game
    loop).

  The suite passes from `92112f7` onward. Don't try to "fix" these commits,
  and keep them in mind if you use `git bisect`.
- **Every scripted game now needs two menu inputs** (category, then
  difficulty) before the answers:
  - The subprocess test sends `"1\n1\n" + "A\n" * 200 + "n\n"`.
  - `run_game(...)` and `Script(...)` calls in `tests/test_cli.py` follow
    the same order.

  If you add another prompt, update all of these. `CLAUDE.md` now says so.
- **`"4"` / `"back"` in the difficulty menu returns `None`** from
  `choose_difficulty()`, and `run()` loops back to the category menu with
  `continue`. Any new step between the two menus has to respect that.
- **`Question.difficulty` defaults to `""`**, like `category`, so tests can
  build short questions. A question without a difficulty prints a header
  with no ` (...)` suffix. Questions loaded from a file always have one.
- **`questions_in()` still returns a new list.** `run()` shuffles that copy
  in place.
- **Tests compare exact output strings**, including the em dash `—`, the
  parentheses around the level, and the `\n` inside the R18 message. The R18
  message is one `output_fn` call that contains a newline.
- **Old question files no longer load.** A Round 2 file needs a `difficulty`
  on every question.
- `spec.md` "Out of scope" now lists a mixed-category mode, a mixed-difficulty
  mode, levels other than the three, difficulty-weighted scoring, timers,
  high scores and network sources. Check it against the next round's
  requirements.
