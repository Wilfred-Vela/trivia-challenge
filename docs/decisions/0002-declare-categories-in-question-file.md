# 0002. Declare categories in the question file, tag each question with one

- Status: accepted
- Date: 2026-11-21

## Decision (Y-statement)

In the context of **adding question categories (R8) that the player chooses
from before each game (R9), where a category may have no questions and must
get a helpful message (R12)**,
facing **the need for an empty category to be representable at all, for the
menu order to be predictable, and for people who edit `questions.json` to add
or rename categories without changing code**,
we decided for **making `questions.json` an object with an ordered
`categories` array and a flat `questions` array in which every question has a
`category` field that must exactly match a declared name**,
and neglected **(a) a hard-coded category list in `game.py`, (b) deriving
categories from the questions' own `category` fields, and (c) a nested object
mapping each category name to its array of questions**,
to achieve **a menu whose contents and order come from one explicit list, a
natural way to have an empty category (declared, but no question uses it),
and load-time errors that catch a misspelt category instead of quietly
creating a new one**,
accepting that **a category name is written once in `categories` and again on
each of its questions, so a rename touches several lines, and that the
Round 1 bare-array file format no longer loads**.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **Declared list + `category` tag on each question (chosen)** | Empty categories are explicit; menu order is the list order; typos are rejected at load; each question stays self-contained, so moving one to another category is a one-word change | Name repeated on every question; old files must be converted |
| Hard-coded list in `game.py` | File format barely changes; the four example categories are guaranteed | Adding a category means editing code, and custom `--questions` files can't have their own categories |
| Derived from the questions' `category` fields | No separate list to keep in sync | An empty category can never exist, so R12 can't happen; menu order would have to be invented, e.g. alphabetical or first-seen; a typo silently creates a new category |
| Nested `{"Science": [...], "Sports": []}` | Category names written once; an empty category is just `[]`; no mismatches possible | Relies on JSON object key order for the menu, which the JSON spec doesn't guarantee, though Python keeps it; moving a question means cutting and pasting it into another block; validation errors would have to point to a question by category and position |

The project owner chose to declare categories in the file, rather than in code
or by deriving them, when asked before implementation. Choosing between the
flat-tagged shape and the nested shape was an implementation decision.

## Consequences

- `game.load_bank()` returns a `QuestionBank(categories, questions)`.
  `bank.questions_in(name)` gives one category's questions in file order.
- Validation (see `spec.md`): `categories` must be non-empty, with no
  case-insensitive duplicates, and every question's `category` must exactly
  match a declared name. At least one question is required in the file, so the
  menu always has a playable option.
- Since the menu lists declared categories, an empty one still appears in the
  menu. Choosing it shows the R12 message and the menu again.
