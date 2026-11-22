# 0005. Store high scores in a validated JSON file, discarded whole if bad and replaced by rename

- Status: accepted
- Date: 2026-11-22

## Decision (Y-statement)

In the context of **saving a top-10 high-score list to a file after every
game (R19, R20), where a missing file must start an empty list (R24) and a
corrupted or unreadable one must start an empty list without crashing (R25)**,
facing **the choice of file format, of what to do with a file that is only
partly valid, and of how to write the file so an interrupted save can't
damage it, with only the standard library available**,
we decided for **a JSON object `{"scores": [...]}` in which every entry is
fully validated on load; any invalid entry makes the whole file count as
corrupted (empty list, one notice, the file renamed to `.bak` on the first
save); and every save writes `<file>.tmp` and renames it over the file with
`os.replace`, all in a new module with no `input()`/`print()`,
`trivia/highscores.py`**,
and neglected **(a) CSV or one-line-per-entry text, (b) `shelve`/`pickle` or
`sqlite3`, (c) keeping the valid entries and skipping only the bad ones, and
(d) writing the file in place with `open(path, "w")`**,
to achieve **a file in the same format as `questions.json` that a person can
read, a single clear rule for what "corrupted" means that is easy to test,
no silent loss of scores the player can't see (the bad file is kept), and a
list that is either the old one or the new one, never half-written**,
accepting that **one bad entry costs the whole list (the `.bak` keeps it for
manual repair), that the `.tmp` and `.bak` files sit beside the list, and that
there is no locking, so two games running at once could overwrite each
other's latest score**.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **Validated JSON, whole-file discard, rename into place (chosen)** | Matches `questions.json`; readable; `json` validates syntax for free; R25 has one simple rule; interrupted save is harmless | One bad entry empties the list; extra `.tmp` during a save |
| CSV / text lines | Even simpler to read; partial damage affects one line | Names containing commas or quotes need escaping; types (points) aren't checked by the parser; a different format from the question file |
| `shelve` / `pickle` | No format code to write | Binary, not readable; `pickle` runs code from the file when loading, so a tampered file is a risk; damage is hard to detect cleanly |
| `sqlite3` | Transactions and safe concurrent writes built in | Far heavier than ten rows need; a binary file; "corrupted" becomes a whole class of database errors to map onto R25 |
| Keep valid entries, skip bad ones | Loses less after partial damage | It's unclear what's still trustworthy (a damaged file may have lost entries too); the R25 notice would need a second form ("some scores could not be read"); more cases to test |
| Write in place | One file, simplest code | A crash or full disk mid-write leaves a truncated file, which R25 would then throw away on the next start |

The owner decided before implementation: one list for all categories and
levels, the file is `trivia/highscores.json` (or `--scores PATH`), a notice is
shown for a corrupted file, and the bad file is kept as `.bak`. The
format, the validation rule, discarding the whole list, and the
write-then-rename save were implementation decisions.

## Consequences

- `highscores.load(path)` returns `(entries, corrupted)`: `([], False)` for a
  missing file, `([], True)` for an unreadable or invalid one. It never
  raises for bad contents.
- `highscores.save(path, entries, backup=False)` raises `OSError` on failure.
  The game loop reports `Could not save high scores: <reason>.` and keeps the
  entry in memory for the session. With `backup=True` an existing *file*
  (not a folder) is renamed to `.bak` first, replacing any older `.bak`.
- The backup happens on the first successful save, not at start-up. Just
  opening the game and quitting leaves a bad file untouched.
- Entries are re-ranked on load (stable sort, so file order breaks ties) and
  cut to 10, so a hand-edited file with extra or unsorted entries still
  loads.
- Safe concurrent use (two games at once) is out of scope. It would need
  locking or a database and would supersede this ADR.
