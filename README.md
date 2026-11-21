# Trivia Challenge

A multiple-choice trivia game that runs in your terminal. It works fully
offline: no internet connection, account, API key, or installation needed —
just Python 3 (standard library only).

Each round asks every question in `trivia/questions.json` in a random order.
Type the letter of your answer (A, B, C, or D); the game tells you whether you
were right, keeps a running score, shows your final score at the end, and asks
if you want to play again.

## Run the game

From the project root:

```sh
python3 -m trivia
```

To use your own question file (format described in `spec.md`):

```sh
python3 -m trivia --questions path/to/questions.json
```

## Run the tests

```sh
python3 -m unittest discover tests
```

## Project docs

- `problem.md` — problem statement and requirements R1–R7
- `spec.md` — detailed behaviour, question file format, design
- `docs/decisions/` — architecture decision records
