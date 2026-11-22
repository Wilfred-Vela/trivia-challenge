# 0007. Show points in feedback and the difficulty menu from the scoring table

- Status: accepted
- Date: 2026-11-22

## Decision (Y-statement)

In the context of **showing the points a correct answer earned
(`Correct! +3 points`, R26) and what each level is worth
(`1) Easy (1 point)`, R27), where ADR 0004 already keeps the values in
`game.POINTS` and scores answers with `points_for(question)`**,
facing **the risk that the numbers the player is told drift away from the
numbers actually added to the score, and the choice of who works out the
number shown after an answer**,
we decided for **building both texts in `trivia/game.py` from the same
table: `feedback(question, choice)` calls `points_for(question)` itself, and
`format_difficulty_menu()` reads `POINTS[level]` for each level, both through
the existing singular/plural helper (`1 point`, `3 points`)**,
and neglected **(a) writing the point values into the menu and feedback
strings by hand, (b) having the game loop pass the points it just recorded
into `feedback(question, choice, points)`, and (c) working out the points
shown from the change in `Score.points` before and after the answer**,
to achieve **a single source for every point value the player sees or
earns, so a change to `POINTS` updates the score, the feedback and the menu
together, while `feedback()` keeps its two-argument signature and stays
testable with no game loop**,
accepting that **`feedback()` now needs a question with a difficulty for a
correct answer (a hand-built `Question` without one raises `KeyError`, as
`points_for()` already did), and that the feedback and the score each look
the value up separately rather than sharing one computed number**.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **Both texts read `POINTS` / `points_for()` (chosen)** | One source of values; menu and feedback can't disagree with scoring; `feedback()` signature unchanged | Correct-answer feedback needs a difficulty on the question |
| Hard-coded strings (`"Easy (1 point)"`, …) | Simplest; the text is visible right in the code | A change to `POINTS` silently leaves the menu and feedback wrong; the values are written in three places |
| Loop passes recorded points into `feedback()` | The feedback shows exactly the number added this time | Every caller and test of `feedback()` changes; a caller could pass a wrong number; the logic for "how many points" leaks into `cli.py` |
| Change in `Score.points` | Shows exactly what was added | Ties the feedback text to the `Score` object and to call order in the loop; harder to test on its own |

The owner chose the wording before implementation: `+1 point` for exactly 1,
no points on an incorrect answer, and `(N points)` after each level name.
Where the numbers come from was an implementation decision.

## Consequences

- `game.POINTS` now feeds three things: scoring (R5), the feedback line
  (R26) and the difficulty menu (R27). The tests
  `test_R26_feedback_points_match_the_points_table` and
  `test_R27_menu_points_match_the_points_table` check the texts against the
  table rather than against fixed numbers alone.
- An incorrect answer never calls `points_for()`, so its feedback works for
  a question with no difficulty, as before.
- If a later round gives single questions their own point values, both
  `points_for()` and this ADR would need revisiting.
