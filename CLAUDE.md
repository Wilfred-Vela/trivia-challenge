# CLAUDE.md

Terminal multiple-choice trivia game. See `problem.md` (requirements R1–R7) and
`spec.md` (behaviour and design).

## Constraints
- Python 3 standard library only. Nothing to install, no API keys, no network.
- Must run with one command: `python3 -m trivia`.
- Questions live in `trivia/questions.json` (format in `spec.md`).

## Commands
- Run the game: `python3 -m trivia`
- Run the tests: `python3 -m unittest discover tests` (must pass with nothing skipped)

## Code layout
- `trivia/game.py` — pure logic. No `input()` or `print()` here.
- `trivia/cli.py` — I/O and the game loop; takes injectable `input_fn`/`output_fn`.
- `tests/` — `unittest` tests. Every test name includes the requirement ID it
  covers, e.g. `test_R4_incorrect_answer_shows_correct_option`.
- `docs/decisions/` — architecture decision records as Y-statements.

## Working rules
- Keep logic separate from I/O so it can be tested without a terminal.
- When adding a requirement, add it to `spec.md` and add tests named with its ID.
- Commit in small steps; messages say what changed and why.
- Never undo, amend, or force-push commits.
