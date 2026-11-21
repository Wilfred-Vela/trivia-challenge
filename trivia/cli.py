"""Terminal front end: the game loop. All input/output goes through
injectable functions so the loop can be tested with scripted input."""

import argparse
import random

from trivia import game


def ask(prompt, parse, error, input_fn, output_fn):
    """Prompt until ``parse`` returns a non-None value."""
    while True:
        value = parse(input_fn(prompt))
        if value is not None:
            return value
        output_fn(error)


def play_round(questions, input_fn, output_fn):
    """Ask every question once and return the round's Score."""
    score = game.Score()
    total = len(questions)
    for number, question in enumerate(questions, start=1):
        output_fn("")
        output_fn(game.format_question(question, number, total))
        choice = ask("Your answer (A-D): ", game.parse_choice,
                     "Please type A, B, C, or D.", input_fn, output_fn)
        score.record(game.is_correct(question, choice))
        output_fn(game.feedback(question, choice))
        output_fn(score.running_text())
    output_fn("")
    output_fn(game.final_score_message(score))
    return score


def run(questions, input_fn=input, output_fn=print, shuffle=random.shuffle):
    """Play rounds until the player declines or input ends. Returns exit code 0."""
    output_fn("Welcome to Trivia Challenge!")
    try:
        while True:
            round_questions = list(questions)
            shuffle(round_questions)
            play_round(round_questions, input_fn, output_fn)
            again = ask("Play again? (y/n): ", game.parse_play_again,
                        "Please type y or n.", input_fn, output_fn)
            if not again:
                break
    except (EOFError, KeyboardInterrupt):
        output_fn("")
    output_fn("Goodbye!")
    return 0


def main(argv=None, input_fn=input, output_fn=print):
    parser = argparse.ArgumentParser(prog="python3 -m trivia",
                                     description="Terminal trivia game.")
    parser.add_argument("--questions", default=game.DEFAULT_QUESTIONS_PATH,
                        help="path to a JSON question file")
    args = parser.parse_args(argv)
    try:
        questions = game.load_questions(args.questions)
    except game.QuestionFileError as e:
        output_fn(f"Could not load questions: {e}")
        return 1
    return run(questions, input_fn, output_fn)
