# Handoff: end of Round 5

This is for the session that does the next round. Standing rules for every
session are in `CLAUDE.md`. This file covers what is true **now** and what
happened in Round 5. Also read `problem.md`, `spec.md` and `docs/decisions/`
(ADRs 0001–0006). `handoff-round-3.md` still describes the menus and
`handoff-round-4.md` the scoring; both still hold, apart from the changes to
R7 and R9 listed below.

## Current state

- Requirements R1–R25 are implemented:
  - R1–R7 (Round 1): the basic game. R5 and R6 changed in Round 4 (points);
    R7 changed in Round 5 (play again now follows the high-score list).
  - R8–R12 (Round 2): categories. R9 changed in Round 5 (menu gained
    `High Scores`).
  - R13–R18 (Round 3): difficulty levels.
  - R19–R25 (Round 5): saved top-10 high scores.
- `spec.md` marks R7 and R9 "changed in Round 5". `problem.md` doesn't mention
  those changes: they follow from R22/R23, not from a rewritten requirement.
- **200 tests, all passing, none skipped**, as of commit `2d7e4aa`
  (89 in `tests/test_cli.py`, 74 in `tests/test_game_logic.py`, 37 in the new
  `tests/test_highscores.py`).
- The working tree was clean at the end of the round, except for this file and
  the uncommitted `CLAUDE.md` edits, which the owner is reviewing.

### What changed for the player
1. **Start-up:** if the high-score file is corrupted or unreadable, the line
   `High scores could not be read, so the list starts empty.` appears right
   after `Welcome to Trivia Challenge!`. A missing file prints nothing.
2. **Category menu:** it ends with one extra option, `High Scores`
   (`5) High Scores` with the bundled file, prompt `Category (1-5): `). This
   shows the list and then the menu again. Typing `high scores` (any case)
   also works.
3. **After the final score:** a blank line, then
   `Enter your name for the high scores: `. A blank reply gets
   `Please type your name.` and is asked again. The name is trimmed, cut to 20
   characters, then trimmed again.
4. **Saving:** the entry is saved. If saving fails, the game prints
   `Could not save high scores: <reason>.` and carries on.
5. **The list:** a blank line, then the list:
   ```
   High Scores
      1. Ana                   12 points  Science (Hard)
      2. Ben                    3 points  History (Medium)
      3. Cy                     1 point   Sports (Easy)
   ```
   An empty list shows `High Scores` / `No high scores yet.`
6. **Play again:** `Play again? (y/n): ` follows the list, with no blank line
   between them.

### Code map (Round 5 changes only)
- `trivia/highscores.py` (new, no `input()`/`print()`):
  - Constants: `MAX_ENTRIES = 10`, `NAME_MAX_LENGTH = 20`,
    `DEFAULT_SCORES_PATH`, `NAME_PROMPT`, `NAME_ERROR`, `UNREADABLE_MESSAGE`.
  - `Entry(name, points, category, difficulty)` is a frozen dataclass.
  - `parse_name(text)` returns the name, or `None` if it's blank.
  - `ranked(entries)` and `add_entry(entries, entry)` both return new lists:
    stable sort by points (highest first), cut to 10. The newest entry goes
    last among equal points.
  - `format_high_scores(entries)` and `save_error_message(error)` build the
    text the game shows.
  - `entries_from_data()` / `entries_to_data()` convert to and from JSON.
    `HighScoreFileError` is raised for bad contents.
  - `load(path)` returns `(entries, corrupted)` and never raises for bad
    contents.
  - `save(path, entries, backup=False)` writes `.tmp` and then calls
    `os.replace`. With `backup`, it first renames an existing *file* to
    `.bak`. It raises `OSError` on failure.
- `trivia/game.py`:
  - `HIGH_SCORES = "High Scores"` is the menu option.
  - `format_category_menu`, `category_prompt`, `category_error` and
    `parse_category` count the extra option. `parse_category` can return
    `HIGH_SCORES`.
  - `_parse_categories` rejects a category named `High Scores` in any case.
- `trivia/cli.py`:
  - `HighScoreList(path=None)` holds the session's entries. It loads them in
    `__init__` and records whether a backup is still owed. `add(entry)`
    saves and returns an error message or `None`.
  - `show_high_scores()` prints the list. `record_high_score()` asks the name,
    saves, and shows the list.
  - `choose_category()` can return `game.HIGH_SCORES`.
  - `run(..., scores_path=None)`: with `None`, scores stay in memory and
    nothing is written.
  - New `parse_args()`. `main()` passes `--scores`, which defaults to
    `trivia/highscores.json`.
- `tests/helpers.py`: `Script` now also keeps a `transcript` of
  `("prompt", text)` / `("output", text)` pairs, in order.
- `.gitignore`: `trivia/highscores.json`, plus its `.bak` and `.tmp` files.
- `README.md`: a high-scores paragraph and the `--scores` option.
- `trivia/questions.json`: unchanged.

## How to run

```sh
python3 -m trivia                                  # play (scores in trivia/highscores.json)
python3 -m trivia --scores /tmp/hs.json            # play with a throwaway score file
python3 -m trivia --questions path/to/file.json    # play with a custom bank
python3 -m unittest discover tests                 # tests (expect 200, OK)
```

To see R25 by hand, put something that isn't JSON in a score file
(`echo '{bad' > /tmp/hs.json`), start the game with `--scores /tmp/hs.json`,
play one game, and look for `/tmp/hs.json.bak`.

## Decisions made in Round 5, and why

**Confirmed by the owner before any code was written:**
1. **High Scores is the last option of the category menu.** The rejected
   options were a new main menu and the play-again prompt. This adds no new
   prompt, and the option can be reached before the first game (ADR 0006).
2. **The file is `trivia/highscores.json`, next to the questions.** It's
   ignored by git, and `--scores PATH` overrides it.
3. **One list for all categories and levels.** Each entry shows its category
   and level.
4. **A blank name is asked again, and names are capped at 20 characters.
   With equal points the older entry ranks higher**, so a new score must beat
   the 10th to get in.
5. **The aligned table layout** shown above, with `No high scores yet.` for
   an empty list.
6. **A corrupted file gets a notice, and is kept as `.bak`** when a new file
   is written.
7. **The name is always asked**, even if the score can't reach the top 10
   (R19's wording).

**Made by the implementer.** The owner was given this list at the end of the
round but has not yet explicitly approved it:

8. **Exact wording:**
   - the name prompt and the blank-name error
   - the corrupted-file notice, shown once, after the welcome line
   - `Could not save high scores: <reason>.`
9. **A missing file prints nothing (R24).** Its folder is never created. If
   the folder is missing, the save fails and the message is shown.
10. **Name handling:** the name is trimmed, cut to 20 characters, then trimmed
    again. A name already in the file isn't cut when it's displayed.
11. **`high scores` typed by name is accepted.** A question file can't
    declare a category called `High Scores`. After viewing the list, the
    category menu comes back.
12. **The file format** is `{"scores": [ ... ]}`, with these rules:
    - points must be a whole number of 0 or more (not a bool)
    - difficulty must be exactly Easy, Medium or Hard
    - category can be any non-empty string
    - extra keys are ignored
    - entries are re-sorted and cut to 10 on load

    See `spec.md` → *High-score file* and ADR 0005.
13. **One bad entry makes the whole file count as corrupted** (ADR 0005).
    Valid entries are not kept; the `.bak` holds them.
14. **The backup happens at the first save, not at start-up.** It replaces
    any older `.bak`. A folder in the file's place is never renamed.
15. **Saves are atomic:** write `.tmp`, then rename it into place.
16. **A failed save doesn't stop the game.** The entry stays in memory for
    the session, and a later save tries again (still with the backup if one
    is owed).
17. **Leaving early saves nothing.** If input ends or Ctrl-C is pressed
    during a round or at the name prompt, no entry is saved.
18. **Code structure:**
    - the separate `trivia/highscores.py` module
    - the `HighScoreList` class in `cli.py`
    - `scores_path=None`, meaning in memory only, so older tests can never
      touch the real file
    - `cli.parse_args()`
19. **Test changes:**
    - every scripted full game in `tests/test_cli.py` now types `NAME`
      (`"Ann"`) before the play-again reply
    - the R9 tests expect the extra menu line and range; the invalid example
      `"5"` became `"6"`
    - the subprocess tests go through `run_bundled_game(scores_path)`, which
      passes `--scores` with a temporary file
    - `Script.transcript` was added to `tests/helpers.py`
20. **Two ADRs:** 0005 (file format and handling) and 0006 (menu placement).
21. **New "Out of scope" entries in `spec.md`:**
    - separate lists per category or level
    - resetting or deleting scores in the game
    - dates or times on entries

    "High-score persistence" was removed from the list, since it is now in
    scope.
22. **The README and `.gitignore` were updated.**

## Unresolved

- Owner reviewed decisions 8–22 on Nov 22 and accepts all of them.
- No file locking: accepted as a known limit (ADR 0005).
- One mixed list for all levels: owner's choice; per-level lists stay out of scope.
- R7 and R9 changes are now noted in problem.md (done by owner at end of Round 5).

## Warnings for the next session

- **Six commits fail the test suite on purpose:**
  - Round 2: `ae66ed2` and `b03ac75`.
  - Round 3: `e8b1ebf` and `7091c12`.
  - Round 4: `d47788f` (tests first).
  - Round 5: `b45f0f8` (tests first).

  The suite passes from `2f59127` onward. Don't try to "fix" these commits,
  and keep them in mind if you use `git bisect`.
- **Never let a test touch `trivia/highscores.json`.**
  - `cli.run()` defaults to `scores_path=None` (in memory), so that is safe.
  - `cli.main()` defaults to the **real** file. Any test that calls `main()`
    and gets past loading the questions must pass `--scores`.
  - The same goes for any new subprocess test: use `run_bundled_game()`.
- **A completed game now needs a name in the script.** If you forget it, the
  play-again reply (`"n"`) is taken as the name. Then input ends at the
  play-again prompt and the game prints `Goodbye!`, so the test may still
  pass while checking the wrong thing.
- **The category menu numbers shifted.** In the tests' `sample_bank()` the
  menu is `1) Science`, `2) History`, `3) Sports`, `4) High Scores`
  (`HIGH_SCORES = "4"`, `MENU_PROMPT = "Category (1-4): "`). Adding a
  category to the sample bank moves High Scores to the next number, and the
  R9/R23 tests that use those numbers will need updating.
- **The subprocess stdin relies on padding.** It is `"1\n1\n" + "A\n"*200 +
  "n\n"`: the first spare `A` becomes the name and the rest are rejected by
  the play-again prompt. If you add a prompt after the round, check that the
  padding still lands where you expect.
- **`highscores.load()` never raises for bad contents.** Code that needs to
  know why a file was rejected has to call `entries_from_data()` itself.
- **`Entry` is frozen and compared by value.** Two entries with the same
  name, points, category and level are equal, which matters for
  `assertIn`/`assertNotIn` in tests.
- **The table's points column is 3 wide.** Totals of 1000 or more (possible
  only with a very large custom Hard bank) push the columns out of line
  without breaking anything.
- **Tests compare exact strings, including column spacing in the table.** If
  you change the table layout, update `spec.md` R21 and the tests in both
  `tests/test_highscores.py` and `tests/test_cli.py` (R19, R21, R22, R23).
