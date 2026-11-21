# 0001. Inject terminal I/O into the game loop for testing

- Status: accepted
- Date: 2026-11-21

## Decision (Y-statement)

In the context of **testing a terminal trivia game whose requirements (R2–R7)
are mostly about what the player sees and types**,
facing **the need to verify prompts, re-prompts, feedback, scoring and
play-again with `unittest` alone, with no extra packages and no real terminal**,
we decided for **splitting pure logic (`trivia/game.py`) from a game loop
(`trivia/cli.py`) whose `run()`/`play_round()` take `input_fn`, `output_fn`
and `shuffle` as parameters defaulting to `input`, `print` and
`random.shuffle`**,
and neglected **(a) patching `builtins.input`/`sys.stdout` with
`unittest.mock` in every test, and (b) testing only end-to-end by running
`python3 -m trivia` as a subprocess with piped stdin**,
to achieve **fast, deterministic tests that read like a scripted play session
and can fix question order, plus logic functions that can be tested with no
I/O at all**,
accepting that **the loop's function signatures carry three extra parameters
that production code never changes, and that one subprocess test is still
needed to prove the real one-command entry point (R1) works**.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **Injected I/O functions (chosen)** | No patching; tests pass a tiny `Script` fake; order made deterministic by passing a no-op shuffle; logic module is I/O-free | Slightly wider function signatures |
| `unittest.mock.patch` on `input`/`stdout` | Production signatures stay minimal | Every test needs patch boilerplate; patches global state; random order still needs patching too |
| Subprocess end-to-end only | Tests the real program exactly as a user runs it | Slower; can't fix shuffle order without a test-only flag; failures are harder to localise; logic edge cases tested indirectly |

## Consequences

- New interactive features should accept `input_fn`/`output_fn` rather than
  calling `input()`/`print()` directly (recorded in `CLAUDE.md`).
- `tests/test_cli.py` keeps a single subprocess test for R1 alongside the
  injected-I/O tests.
