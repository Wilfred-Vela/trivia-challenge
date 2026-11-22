# 0006. Offer High Scores as the last option of the category menu

- Status: accepted
- Date: 2026-11-22

## Decision (Y-statement)

In the context of **R23, which asks for a "High Scores option in the menu"
in a game whose first screen is the category menu (R9) and which has no
main menu**,
facing **the need to place the option somewhere the player always passes,
without adding a prompt that every scripted test would have to step
through**,
we decided for **adding `N+1) High Scores` as the last line of the category
menu (chosen by number or by typing `high scores`), which shows the list and
then the category menu again, and reserving the name `High Scores` so no
question file can declare a category with it**,
and neglected **(a) a new main menu (Play / High Scores / Quit) before the
category menu, and (b) offering it only at the play-again prompt**,
to achieve **an option that is reachable before the first game and between
games, works the same way as the existing `Back to categories` option in the
difficulty menu, and leaves the prompt order of a game unchanged**,
accepting that **a non-category option sits in the category menu, that
the R9 menu text, prompt range and error range all change (`Category (1-5): `
for the bundled file), and that a custom file can't use `High Scores` as a
category name**.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **Last item of the category menu (chosen)** | No new prompt; same pattern as `Back to categories`; reachable any time the menu shows | Mixes an action into a list of categories; R9 wording changes |
| New main menu first | Cleanest separation; room for later options (e.g. Quit) | Adds a prompt to every game, so every scripted test and the subprocess stdin change; one more step for players who just want to play |
| Only at play again | Category menu unchanged | Can't view the list before the first game; play-again becomes a three-way choice |

The owner chose the placement before implementation. Accepting the typed
name `high scores`, reserving that category name, and returning to the
category menu afterwards were implementation decisions.

## Consequences

- `game.parse_category()` can return `game.HIGH_SCORES`.
  `cli.choose_category()` returns it without checking for questions, and
  `cli.run()` shows the list and loops back to the menu.
- `game.category_prompt()` and `game.category_error()` count the extra
  option. The error still says "or a category name".
- `parse_bank()` rejects a category named `High Scores` in any case, with an
  error saying it is reserved.
- If a main menu is added later, it would supersede this ADR.
