# 0004. Score points per answer from a difficulty table in code

- Status: accepted
- Date: 2026-11-22

## Decision (Y-statement)

In the context of **changing R5 so a correct answer earns points by the
question's difficulty (Easy 1, Medium 3, Hard 5) and R6 so the final score
shows the total points and the number of correct answers**,
facing **the choice of where the point values live and when they are added
up, given that ADR 0003 already fixes the three levels in `trivia/game.py`
and that every round today uses one level only**,
we decided for **a `POINTS = {"Easy": 1, "Medium": 3, "Hard": 5}` table in
`trivia/game.py` beside `DIFFICULTIES`, a `points_for(question)` lookup, and a
`Score` that adds each correct answer's own points as it is recorded
(`record(was_correct, points)`), alongside the existing correct and answered
counts**,
and neglected **(a) point values declared in `questions.json`, either per
level or as a `points` field on each question, and (b) storing only the
correct count and multiplying by the round's level at the end**,
to achieve **point values that always match R5 for every question file,
a single place to change them next to the levels they belong to, and a total
that stays right if a later round mixes levels (an "any difficulty" mode is
listed as out of scope today, but is a likely next requirement)**,
accepting that **a question file can't give one question extra points, that
`Score.record()` now needs a second argument (every caller and test changed),
and that `POINTS` and `DIFFICULTIES` must be kept in step, which a test
checks**.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **Table in code, added per answer (chosen)** | R5 met for every file by construction; same home as the levels (ADR 0003); correct for mixed-level rounds | Values not customisable per file; `record()` signature changed |
| Per-level `points` in `questions.json` | Authors could rebalance without code | A file could set Hard to 2, which breaks R5; validation would have to insist on 1/3/5 anyway, the same argument that kept the levels out of the file in ADR 0003 |
| `points` field on each question | Most flexible | R5 ties points to difficulty, not to the question; every question gains a field that has to agree with its level |
| Correct count × the round's level, at the end | No change to `Score.record()`; tiny diff | Depends on a round having exactly one level; a mixed-level round would give a wrong total with no error; the running score would need the level passed in separately |

The owner chose the wording before implementation: the running score has the
same shape as the final line (`Score: 4 points (2 of 3 correct)`), and a total
of exactly 1 says `1 point`. Where the values live and how they are added up
were implementation decisions.

## Consequences

- `game.POINTS` and `game.points_for()` are the only source of point values.
  `points_for()` raises `KeyError` for a question with no difficulty.
  Questions loaded from a file always have one (R15), but a hand-built
  `Question` in a test needs one before it goes through `play_round()`.
- `Score` has `points`, `correct` and `answered`. `running_text()` and
  `final_score_message()` show all three. Both use the singular "point"
  when the total is 1.
- Adding or renaming a level now means editing both `DIFFICULTIES` and
  `POINTS`. `test_R5_every_difficulty_has_a_point_value` fails if they
  drift apart.
