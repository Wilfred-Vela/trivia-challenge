# CLAUDE.md

Terminal multiple-choice trivia game. See `problem.md` (requirements R1, R2, …, grouped by round) and
`spec.md` (behaviour and design).

## Constraints
- Python 3 standard library only. Nothing to install, no API keys, no network.
- Must run with one command: `python3 -m trivia`.
- Questions live in `trivia/questions.json`: an object with a declared
  `categories` list and `questions` that each name one category (format in
  `spec.md`, rationale in ADR 0002).

## Commands
- Run the game: `python3 -m trivia`
- Run the tests: `python3 -m unittest discover tests` (must pass with nothing skipped)

## Code layout
- `trivia/game.py` — pure logic. No `input()` or `print()` here.
- `trivia/cli.py` — I/O and the game loop; takes injectable `input_fn`/`output_fn`.
- `tests/` — `unittest` tests. Every test name includes the requirement ID it
  covers, e.g. `test_R4_incorrect_answer_shows_correct_option`.
- `docs/decisions/` — architecture decision records as Y-statements, numbered
  `0001-…`, `0002-…` in order. Read them before changing a recorded decision.

## Working rules
- Keep logic separate from I/O so it can be tested without a terminal.
- When adding a requirement, add it to `spec.md` and add tests named with its ID.
- Commit in small steps; messages say what changed and why.
- If a requirement is unclear, ask the owner before writing code.
- `spec.md` fixes the exact on-screen wording, and the tests assert it
  exactly. If you change wording or behaviour, update `spec.md` and every
  affected test (including tests from earlier rounds) together.
- Handoff notes go in `handoff-round-N.md` and are written only when the owner
  asks. Don't commit them, or `CLAUDE.md` changes, until the owner has
  reviewed them.
- Never undo, amend, or force-push commits.
