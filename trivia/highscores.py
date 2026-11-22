"""High-score list: ranking, formatting, and the high-score file (R19-R25).
Nothing in this module reads input or prints output."""

import json
import os
from dataclasses import asdict, dataclass

from trivia.game import DIFFICULTIES

# Only the best MAX_ENTRIES scores are kept (R20).
MAX_ENTRIES = 10
NAME_MAX_LENGTH = 20
DEFAULT_SCORES_PATH = os.path.join(os.path.dirname(__file__), "highscores.json")
NAME_PROMPT = "Enter your name for the high scores: "
NAME_ERROR = "Please type your name."
UNREADABLE_MESSAGE = "High scores could not be read, so the list starts empty."


@dataclass(frozen=True)
class Entry:
    name: str
    points: int
    category: str
    difficulty: str


class HighScoreFileError(Exception):
    """The high-score file's contents are not in the expected format."""


def parse_name(text):
    """Trim the typed name and cut it to NAME_MAX_LENGTH characters, or
    return None if nothing is left (R19)."""
    name = text.strip()[:NAME_MAX_LENGTH].rstrip()
    return name or None


def ranked(entries):
    """Highest points first, earlier entries first on equal points, cut to
    the top MAX_ENTRIES (R20, R21). Returns a new list."""
    return sorted(entries, key=lambda e: -e.points)[:MAX_ENTRIES]


def add_entry(entries, entry):
    """A new ranked list with ``entry`` added as the newest entry, so it
    ranks below any older entry with the same points."""
    return ranked(list(entries) + [entry])


def _points_text(points):
    return "point" if points == 1 else "points"


def format_high_scores(entries):
    """The list as shown after each game (R22) and from the menu (R23)."""
    if not entries:
        return "High Scores\nNo high scores yet."
    lines = ["High Scores"]
    lines += [f"{rank:>4}. {e.name:<{NAME_MAX_LENGTH}} {e.points:>3} "
              f"{_points_text(e.points):<6}  {e.category} ({e.difficulty})"
              for rank, e in enumerate(entries, start=1)]
    return "\n".join(lines)


def save_error_message(error):
    reason = getattr(error, "strerror", None) or str(error)
    return f"Could not save high scores: {reason}."


def entries_from_data(data):
    """Validate decoded JSON and return its entries, ranked."""
    if not isinstance(data, dict) or not isinstance(data.get("scores"), list):
        raise HighScoreFileError("expected an object with a 'scores' array")
    return ranked([_parse_entry(item) for item in data["scores"]])


def _parse_entry(item):
    if not isinstance(item, dict):
        raise HighScoreFileError("each score must be an object")
    name, points = item.get("name"), item.get("points")
    category, difficulty = item.get("category"), item.get("difficulty")
    if not isinstance(name, str) or not name.strip():
        raise HighScoreFileError("'name' must be a non-empty string")
    if isinstance(points, bool) or not isinstance(points, int) or points < 0:
        raise HighScoreFileError("'points' must be a whole number of 0 or more")
    if not isinstance(category, str) or not category.strip():
        raise HighScoreFileError("'category' must be a non-empty string")
    if difficulty not in DIFFICULTIES:
        raise HighScoreFileError(
            f"'difficulty' must be one of {', '.join(DIFFICULTIES)}")
    return Entry(name, points, category, difficulty)


def entries_to_data(entries):
    return {"scores": [asdict(e) for e in entries]}


def load(path):
    """Read the high-score file. Returns ``(entries, corrupted)``: a missing
    file gives ``([], False)`` (R24); a file that can't be read or isn't in
    the expected format gives ``([], True)`` (R25)."""
    try:
        with open(path, encoding="utf-8") as f:
            return entries_from_data(json.load(f)), False
    except FileNotFoundError:
        return [], False
    except (OSError, UnicodeDecodeError, ValueError, HighScoreFileError):
        # json.JSONDecodeError is a ValueError.
        return [], True


def save(path, entries, backup=False):
    """Write ``entries`` to ``path``, creating the file if needed (R24).
    With ``backup``, an existing file is first renamed to ``<path>.bak``
    (R25). Writes a temporary file and renames it into place, so an
    interrupted save never leaves half a list. Raises OSError on failure."""
    if backup and os.path.isfile(path):
        os.replace(path, path + ".bak")
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(entries_to_data(entries), f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except OSError:
        if os.path.isfile(tmp):
            os.remove(tmp)
        raise
