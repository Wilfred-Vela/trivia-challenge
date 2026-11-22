# Trivia Challenge

A multiple-choice trivia game that runs in your terminal. It works fully
offline: no internet connection, account, API key, or installation needed —
just Python 3 (standard library only).

Questions are grouped into categories (Science, History, Sports, Geography),
and each has a difficulty: Easy, Medium, or Hard. Each game starts by choosing
a category and then a difficulty, by number or by name (the difficulty menu
also lets you go back to the categories); the round then asks every question
of that category and difficulty in a random order. Type the letter of your
answer (A, B, C, or D); the game tells you whether you were right, keeps a
running score, shows your final score at the end, and asks if you want to play
again (you choose a category and difficulty again for the next game).

A correct answer earns points by difficulty: Easy 1, Medium 3, Hard 5. The
score shows your points and how many you got right, e.g.
`Final score: 12 points (4 of 5 correct).`

## Run the game

From the project root:

```sh
python3 -m trivia
```

To use your own question file (format, including how to declare categories
and give each question a difficulty, described in `spec.md`):

```sh
python3 -m trivia --questions path/to/questions.json
```

## Run the tests

```sh
python3 -m unittest discover tests
```

## Project docs

- `problem.md` — problem statement and requirements R1–R18 (R5 and R6 changed in Round 4)
- `spec.md` — detailed behaviour, question file format, design
- `docs/decisions/` — architecture decision records
