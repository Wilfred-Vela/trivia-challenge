# Handoff: end of Round 6

This is for the session that does the next round. Standing rules for every
session are in `CLAUDE.md`. This file covers what is true **now** and what
happened in Round 6. Also read `problem.md`, `spec.md` and `docs/decisions/`
(ADRs 0001–0007). `handoff-round-5.md` still describes the high scores and
`handoff-round-3.md`/`handoff-round-4.md` the menus and scoring; they still
hold, apart from the Round 6 changes listed below.

## Current state

- Requirements R1–R28 are implemented:
  - R1–R7 (Round 1): the basic game. R5 and R6 changed in Round 4, R7 in
    Round 5, **R4 in Round 6** (correct-answer line now shows points).
  - R8–R12 (Round 2): categories. R9 changed in Round 5, **R8 in Round 6**
    (bundled file now has five categories).
  - R13–R18 (Round 3): difficulty levels. **R14 changed in Round 6** (menu
    lines show points).
  - R19–R25 (Round 5): saved top-10 high scores.
  - R26–R28 (Round 6): points in feedback, points in the difficulty menu,
    Literature category.
- `spec.md` marks R4, R8 and R14 "changed in Round 6". `problem.md` does
  **not** note those changes yet (last round the owner added such notes
  themselves).
- **224 tests, all passing, none skipped**, as of commit `5968417`
  (99 in `tests/test_cli.py`, 88 in `tests/test_game_logic.py`, 37 in
  `tests/test_highscores.py`).
- The working tree was clean at the end of the round, except for this file
  and the uncommitted `CLAUDE.md` edits, which the owner is reviewing.

### What changed for the player
1. **Category menu (bundled file):** `1) Science`, `2) History`,
   `3) Sports`, `4) Geography`, `5) Literature`, `6) High Scores`, prompt
   `Category (1-6): `. Typing `literature` also works.
2. **Difficulty menu:**
   ```
   Choose a difficulty for Science:
     1) Easy (1 point)
     2) Medium (3 points)
     3) Hard (5 points)
     4) Back to categories
   Difficulty (1-4): 
   ```
   Prompt, error message and typed names (`easy`, `medium`, `hard`, `back`)
   are unchanged.
3. **Feedback:** a correct answer prints `Correct! +1 point` (Easy),
   `Correct! +3 points` (Medium) or `Correct! +5 points` (Hard). An incorrect
   answer is unchanged: `Incorrect. The correct answer was C) <text>.` The
   running `Score: …` line still follows.
4. **Questions:** "Who wrote 'Romeo and Juliet'?" moved from History Easy to
   Literature Easy. Literature has two questions at each level. History
   gained "In which country are the ancient Pyramids of Giza?" (Easy) so it
   still has two per level.

### Code map (Round 6 changes only)
- `trivia/game.py`:
  - `feedback(question, choice_index)` returns
    `f"Correct! +{_points_text(points_for(question))}"` for a correct answer.
  - `format_difficulty_menu(category)` builds each level line as
    `f"{level} ({_points_text(POINTS[level])})"`.
  - No new names; `POINTS`, `points_for()` and `_points_text()` already
    existed (Round 4).
- `trivia/cli.py`: unchanged.
- `trivia/highscores.py`: unchanged.
- `trivia/questions.json`: `Literature` appended to `categories`; the Romeo
  question replaced in place by the Pyramids question (History Easy); six
  Literature questions appended at the end (Romeo first).
- `tests/test_game_logic.py`: new `TestR26PointsInFeedback`,
  `TestR27PointsInDifficultyMenu`, `TestR28LiteratureCategory`; R4, R8 and
  R13 tests updated to the new wording.
- `tests/test_cli.py`: new `TestR26PointsInFeedbackInGame`,
  `TestR27PointsInDifficultyMenuInGame`, `TestR28LiteratureInGame`; new
  helper `run_bundled_in_memory(*lines)` (bundled questions, file order,
  in-memory scores); `DIFFICULTY_MENU` constant updated; now imports
  `trivia.game`.
- `docs/decisions/0007-show-points-from-the-scoring-table.md` (new).
- `README.md`: Literature, the points display, R1–R28.

## How to run

```sh
python3 -m trivia                                  # play (scores in trivia/highscores.json)
python3 -m trivia --scores /tmp/hs.json            # play with a throwaway score file
python3 -m trivia --questions path/to/file.json    # play with a custom bank
python3 -m unittest discover tests                 # tests (expect 224, OK)
```

To see Round 6 by hand: start the game, choose `5` (Literature), then `2`
(Medium) and answer correctly to see `Correct! +3 points`.

## Decisions made in Round 6, and why

**Confirmed by the owner before any code was written:**
1. **`+1 point` is singular**, matching the existing score lines; an
   incorrect answer shows no points.
2. **Difficulty menu format** `1) Easy (1 point)`, with nothing after
   `Back to categories`.
3. **Literature goes last** in the category menu, so existing numbers stay
   the same; only High Scores moves (5 → 6).
4. **Question content:** move Romeo and Juliet, add five Literature
   questions (two per level) and one History Easy question (the texts were
   shown to and approved by the owner).

**Made by the implementer.** The owner was given this list at the end of the
round but has not yet explicitly approved it:

5. **Shown points come from the scoring table (ADR 0007).** `feedback()` calls
   `points_for()` and the menu reads `POINTS`, instead of hard-coded text or
   points passed in by the game loop, so the texts can't drift from scoring.
6. **`feedback()` now needs a difficulty for a correct answer.** A
   hand-built `Question` with no difficulty raises `KeyError` on a correct
   answer. The R4 test's question was given `"Science", "Easy"`.
7. **Earlier tests updated to the new wording:** R4 correct line, R8
   bundled categories (renamed `test_R8_bundled_file_has_the_named_categories`),
   R13 menu lines, and the shared `DIFFICULTY_MENU` constant in
   `tests/test_cli.py`.
8. **R4, R8 and R14 marked "changed in Round 6" in `spec.md`; `problem.md`
   left alone** for the owner.
9. **Typing a level by name is unchanged**: `easy` works, `easy (1 point)`
   doesn't.
10. **Question details:** the wrong options and correct letter for each new
    question; the Pyramids question takes Romeo's place in the file, the
    Literature questions go at the end.
11. **A heuristic test:** every bundled question starting "Who wrote" must be
    in Literature (`test_R28_who_wrote_questions_are_all_in_literature`).
12. **`run_bundled_in_memory()` helper** in `tests/test_cli.py`, so R28 game
    tests use the real bundled file without a subprocess and without
    touching the real high-score file.
13. **Spec extras:** overview sentence about points, Literature in the
    question-file example, Design section notes that feedback and menu read
    `POINTS`.
14. **README updated.**

## Unresolved

- Owner reviewed decisions 5–14 on Nov 22 and accepts all of them.
- R4, R8 and R14 changes are now noted in problem.md (done by owner at end of Round 6).
- The "Who wrote" check for Literature is accepted as a known weak test.

## Warnings for the next session

- **Seven commits fail the test suite on purpose:**
  - Round 2: `ae66ed2` and `b03ac75`.
  - Round 3: `e8b1ebf` and `7091c12`.
  - Round 4: `d47788f` (tests first).
  - Round 5: `b45f0f8` (tests first).
  - Round 6: `c51eff3` (tests first) and `7bf8bab` (R26/R27 done, R28
    question file not yet).

  The suite passes from `a1a2e12` onward. Don't try to "fix" these commits,
  and keep them in mind if you use `git bisect`.
- **Feedback text now depends on difficulty.** Any new test that drives
  `play_round()` or `feedback()` with a hand-built `Question` and a correct
  answer must give it a difficulty, or it raises `KeyError`.
- **Tests that look for the feedback line** should match
  `line.startswith("Correct!")` or the exact `Correct! +N point(s)`;
  `== "Correct!"` no longer matches anything.
- **Two menus, two sources of numbers.** The bundled menu is now 1–6, but
  the tests' `sample_bank()` menu is still `1) Science`, `2) History`,
  `3) Sports`, `4) High Scores` (`MENU_PROMPT = "Category (1-4): "`). Don't
  mix them up. Tests using `run_bundled_in_memory()` use the bundled numbers
  (`"5"` = Literature).
- **`run_bundled_in_memory()` keeps file order** (no shuffle), so its tests
  depend on the order of questions in `trivia/questions.json`, e.g. that
  Literature Easy has exactly two questions (`Question 1 of 2`). Adding a
  bundled question to a category/level those tests use will need them
  updated.
- **The subprocess stdin is still `"1\n1\n" + "A\n"*200 + "n\n"`** (Science,
  Easy). If a category is ever inserted before Science, or Science Easy
  changes size a lot, check where the padding lands (see Round 5 handoff).
- **Changing `POINTS`** now changes the score, the feedback and the menu
  together; the R26/R27 "match the points table" tests follow it, but the
  tests with literal text (`"Correct! +3 points"`, `DIFFICULTY_MENU`, the R13
  menu lines) and `spec.md` do not.
- **Never let a test touch `trivia/highscores.json`** (same as Round 5:
  `cli.run()` defaults to memory, `cli.main()` and subprocess runs must pass
  `--scores`).
