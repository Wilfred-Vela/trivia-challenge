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


def choose_category(bank, input_fn, output_fn):
    """Show the category menu until the player picks one that has questions
    (R9, R12). Returns the chosen category name."""
    categories = bank.categories
    while True:
        output_fn("")
        output_fn(game.format_category_menu(categories))
        category = ask(game.category_prompt(categories),
                       lambda text: game.parse_category(text, categories),
                       game.category_error(categories), input_fn, output_fn)
        if bank.questions_in(category):
            return category
        output_fn(game.no_questions_message(category))


def play_round(questions, category, input_fn, output_fn):
    """Ask every question once and return the round's Score."""
    score = game.Score()
    total = len(questions)
    output_fn("")
    output_fn(game.category_banner(category))
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


def run(bank, input_fn=input, output_fn=print, shuffle=random.shuffle):
    """Play rounds until the player declines or input ends. Returns exit code 0.
    Each round starts by choosing a category from ``bank`` (R9, R7)."""
    output_fn("Welcome to Trivia Challenge!")
    try:
        while True:
            category = choose_category(bank, input_fn, output_fn)
            round_questions = bank.questions_in(category)
            shuffle(round_questions)
            play_round(round_questions, category, input_fn, output_fn)
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
        bank = game.load_bank(args.questions)
    except game.QuestionFileError as e:
        output_fn(f"Could not load questions: {e}")
        return 1
    return run(bank, input_fn, output_fn)
