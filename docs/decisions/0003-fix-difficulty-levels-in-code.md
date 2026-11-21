# 0003. Fix the three difficulty levels in code, tag each question with one

- Status: accepted
- Date: 2026-11-21

## Decision (Y-statement)

In the context of **adding difficulty levels (R13) that the player chooses
after a category (R14), where every question has a level (R15) and a category
may have no questions at the chosen level (R18)**,
facing **the choice of where the list of levels lives, given that ADR 0002
put the category list in `questions.json` so authors can add categories
without changing code**,
we decided for **fixing the levels in `trivia/game.py` as
`DIFFICULTIES = ("Easy", "Medium", "Hard")` and requiring a `difficulty` field
on every question whose value is exactly one of them**,
and neglected **(a) a declared `difficulties` list in `questions.json`, just
like `categories`, (b) deriving the levels from the questions' own
`difficulty` fields, and (c) a numeric level (1–3) on each question mapped
to names in code**,
to achieve **a menu that always shows exactly the three levels R13 asks for,
in a natural Easy→Hard order, for every category and every custom file, so
that R18 (a level with no questions) can occur and is handled the same way
everywhere, and load-time errors that catch a misspelt level**,
accepting that **a custom file can't add or rename levels without changing
code, that the two menus (categories from the file, levels from code) come
from different places, and that every Round 2 question file must gain a
`difficulty` field before it will load**.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **Fixed in code + exact-name tag on each question (chosen)** | R13 is met by construction; order is guaranteed; R18 needs no extra data; same validation style as `category` | Levels can't be customised per file |
| Declared `difficulties` list in the file | Symmetric with ADR 0002; authors could add e.g. "Expert" | A file could declare two levels or "Expert", which breaks R13; validation would need to insist on exactly Easy/Medium/Hard anyway, so the list adds nothing but a way to get it wrong |
| Derived from the questions' fields | No extra list | A level no question uses would vanish from the menu, so R18 could never happen and the menu would differ between categories; order would have to be invented |
| Numeric level (1, 2, 3) on each question | Short to type; easy to sort | The file is harder to read (`"difficulty": 2` vs `"Medium"`); the number still has to be mapped to the names R13 requires |

The owner decided before implementation that the field is required, not
defaulting to Medium. Where the list lives and how the field is spelt were
implementation decisions.

## Consequences

- `game.parse_bank()` rejects a question whose `difficulty` is missing or is
  not exactly `Easy`, `Medium` or `Hard`, and the error names the question.
- `QuestionBank.questions_in(category, difficulty=None)` filters by both;
  leaving out `difficulty` keeps the Round 2 behaviour.
- The difficulty menu shows all three levels plus `Back to categories`, for
  every category. Choosing a level with no questions shows the R18 message
  and the menu again.
- Customisable levels would be a new requirement and would supersede this
  ADR.
