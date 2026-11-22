# Handoff: end of Round 4

This is for the session that does the next round. Standing rules for every
session are in `CLAUDE.md`. This file covers what is true **now** and what
happened in Round 4. Also read `problem.md`, `spec.md` and `docs/decisions/`
(ADRs 0001–0004). `handoff-round-3.md` still describes the menus and the
round flow; nothing there changed except scoring.

## Current state

- Requirements R1–R18 are implemented, with R5 and R6 as changed in Round 4:
  - R1–R7 (Round 1): the basic game. R5 and R6 are now points-based.
  - R8–R12 (Round 2): categories.
  - R13–R18 (Round 3): difficulty levels.
- Round 4 added no new requirement IDs. It changed R5 and R6 in place.
  `problem.md` and `spec.md` both mark them "changed in Round 4".
- **124 tests, all passing, none skipped**, as of commit `607d759`
  (69 in `tests/test_game_logic.py`, 55 in `tests/test_cli.py`).
- The working tree was clean at the end of the round, except for this file and
  the uncommitted `CLAUDE.md` edits, which the owner is reviewing.

### What changed for the player
The flow is unchanged (welcome → category menu → difficulty menu → round →
play again). Only the scoring and the two score lines differ:

- A correct answer earns **Easy 1, Medium 3, Hard 5** points. A wrong answer
  earns 0.
- After each answer: `Score: <P> points (<C> of <A> correct)`. There is no
  full stop.
- After the last question: `Final score: <P> points (<C> of <N> correct).`
  This one has a full stop.
- When P is exactly 1 the word is `point` (`1 point`). Every other value,
  including 0, uses `points`.
- Feedback (`Correct!` / `Incorrect. …`) and both menus are unchanged. They
  don't mention points.

### Code map (Round 4 changes only)
- `trivia/game.py`:
  - `POINTS = {"Easy": 1, "Medium": 3, "Hard": 5}`, right below `DIFFICULTIES`.
  - `points_for(question)` returns `POINTS[question.difficulty]`.
  - `_points_text(n)` is a private helper that gives `"1 point"` or
    `"N points"`.
  - `Score` now has `points`, `correct` and `answered`.
    `record(was_correct, points)` takes a **required** second argument.
  - `Score.running_text()` and `final_score_message(score)` use the new
    wording.
- `trivia/cli.py`: `play_round()` calls
  `score.record(game.is_correct(...), game.points_for(question))`. Nothing
  else changed.
- `trivia/questions.json`, `tests/helpers.py`: unchanged.
- `README.md`: a paragraph about points was added.

## How to run

```sh
python3 -m trivia                                  # play
python3 -m trivia --questions path/to/file.json    # play with a custom bank
python3 -m unittest discover tests                 # tests (expect 124, OK)
```

The sample bank in `tests/helpers.py` has no Hard question. The Hard scoring
test builds two Hard questions inline and calls `cli.play_round()` directly.
To see Hard points in the real program, pick Science → Hard. Its two answers
are A and D, but the order is shuffled.

## Decisions made in Round 4, and why

**Confirmed by the owner before any code was written:**
1. **The running score has the same shape as the final line**
   (`Score: 4 points (2 of 3 correct)`). This keeps the points and the
   correct count visible all the time. The rejected options were points only
   (`Score: 4 points`) and keeping `Score: 2/3`.
2. **`1 point` is singular. Every other total, including 0, is plural.**
3. **No extras.** Points are not shown in the answer feedback
   (`Correct! +3 points`) or in the difficulty menu (`1) Easy (1 point)`).
   Either would change R4 or R14 wording.

**Made by the implementer.** The owner was given this list at the end of the
round but has not yet explicitly approved it:

4. **The point values are fixed in code** next to the levels. They are not in
   `questions.json`. This follows the ADR 0003 reasoning: a file could
   otherwise break R5. See ADR 0004.
5. **Points are added per answer from each question's own difficulty.** They
   are not computed as the correct count × the round's level. This stays
   correct if a future round mixes levels. See ADR 0004.
6. **`Score.record()` requires the points argument.** It has no default of 1,
   so no caller can quietly keep the old scoring.
7. **`points_for()` raises `KeyError` for a question with no difficulty.**
   File-loaded questions always have one (R15).
8. **Exact wording details beyond the owner's example:**
   - The running line has no full stop.
   - N in the final line is the number of questions in the round.
   - A wrong first answer shows `Score: 0 points (0 of 1 correct)`.
9. **Earlier-round tests were updated** to the new final-score text (R3, R7,
   R9–R12, R14, R16–R18). Each one still checks the same behaviour as before.
10. **New tests:**
    - A second subprocess test (`test_R6_bundled_game_final_score_uses_points_format`).
    - A test that `POINTS` and `DIFFICULTIES` have the same keys.
    - A logic test that reproduces the problem's own example,
      `Final score: 12 points (4 of 5 correct).`
11. **The README was updated.**
12. **New "Out of scope" entries in `spec.md`:**
    - point values set in the question file or per question
    - bonus points (e.g. streaks, speed)

    "Scoring that depends on difficulty" was removed from the list, since it
    is now in scope.

## Unresolved

- Owner reviewed decisions 4–12 on Nov 22 and accepts all of them.
- Bundled question difficulty levels and "Romeo and Juliet" under History remain accepted as they are.

  Their levels now affect points, so they matter a little more than before.

## Warnings for the next session

- **Five commits fail the test suite on purpose:**
  - Round 2: `ae66ed2` and `b03ac75`.
  - Round 3: `e8b1ebf` and `7091c12`.
  - Round 4: `d47788f` (tests first).

  The suite passes from `6a9fef6` onward. Don't try to "fix" these commits,
  and keep them in mind if you use `git bisect`.
- **`Score.record()` takes two arguments now.** Any new code or test that
  records an answer must pass the points, normally
  `game.points_for(question)`.
- **A hand-built `Question` needs a difficulty before it can be scored.**
  `Question.difficulty` still defaults to `""`, so formatting such a question
  works, but `points_for()` raises `KeyError`. Anything that goes through
  `play_round()` needs `"Easy"`, `"Medium"` or `"Hard"`.
- **Changing or adding a level now means editing two things:**
  `DIFFICULTIES` and `POINTS`. A test fails if their keys differ.
- **Tests compare exact strings.** That includes the parentheses in the
  score lines, the full stop on the final line only, and `point` vs `points`.
  Many CLI tests assert the final-score line as a check that a round ran, so
  changing that wording touches about 24 lines of
  `tests/test_cli.py`.
- **The "1 of 1 correct" assertions differ by level.** History Easy games
  expect `1 point (1 of 1 correct).`, while Science Medium games
  (`test_R14_difficulty_can_be_chosen_by_name` and the R5/R6 Medium tests)
  expect `3 points`.
- **Points don't carry between rounds.** Play again starts a new `Score`.
  `test_R5_play_again_resets_points` checks this. A cumulative or high-score
  feature would be a new requirement; high-score persistence is listed as out
  of scope.
- **Mixed-level rounds** (an "any difficulty" mode) are still out of scope.
  The scoring already supports them, since each answer adds its own
  question's points. The menus, the banner and the header would still need
  work.
