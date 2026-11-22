"""Unit tests for the high-score logic and file handling in trivia.highscores."""

import json
import os
import tempfile
import unittest

from trivia import highscores
from trivia.highscores import Entry

PACKAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "trivia")


def entry_data(name="Ana", points=12, category="Science", difficulty="Hard"):
    """One entry as it appears in the high-score file."""
    return {"name": name, "points": points, "category": category,
            "difficulty": difficulty}


def entries(*points):
    """Entries named P0, P1, … with the given points, in that order."""
    return [Entry(f"P{i}", p, "Science", "Easy") for i, p in enumerate(points)]


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "highscores.json")

    def write(self, content):
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(self.path, mode) as f:
            f.write(content)

    def read_json(self, path=None):
        with open(path or self.path, encoding="utf-8") as f:
            return json.load(f)


class TestR19NameAndEntry(TempDirTestCase):
    def test_R19_name_prompt_and_error_text(self):
        self.assertEqual(highscores.NAME_PROMPT,
                         "Enter your name for the high scores: ")
        self.assertEqual(highscores.NAME_ERROR, "Please type your name.")

    def test_R19_name_is_trimmed(self):
        self.assertEqual(highscores.parse_name("  Ana Lee  "), "Ana Lee")

    def test_R19_blank_name_is_rejected(self):
        for text in ("", "   ", "\t"):
            self.assertIsNone(highscores.parse_name(text), repr(text))

    def test_R19_name_is_cut_to_20_characters(self):
        self.assertEqual(highscores.NAME_MAX_LENGTH, 20)
        name = highscores.parse_name("  Bartholomew Alexander Smith ")
        self.assertEqual(name, "Bartholomew Alexande")
        self.assertEqual(highscores.parse_name("x" * 20), "x" * 20)

    def test_R19_cut_name_has_no_trailing_space(self):
        self.assertEqual(highscores.parse_name("Abcdefghijklmnopqrs tuv"),
                         "Abcdefghijklmnopqrs")

    def test_R19_entry_holds_name_points_category_difficulty(self):
        e = Entry("Ana", 12, "Science", "Hard")
        self.assertEqual((e.name, e.points, e.category, e.difficulty),
                         ("Ana", 12, "Science", "Hard"))

    def test_R19_save_writes_every_field_to_the_file(self):
        highscores.save(self.path, [Entry("Ana", 12, "Science", "Hard")])
        self.assertEqual(self.read_json(),
                         {"scores": [entry_data("Ana", 12, "Science", "Hard")]})

    def test_R19_saved_file_loads_back_the_same_entries(self):
        saved = [Entry("Ana", 12, "Science", "Hard"),
                 Entry("Ben", 3, "History", "Medium")]
        highscores.save(self.path, saved)
        self.assertEqual(highscores.load(self.path), (saved, False))

    def test_R19_save_leaves_no_temporary_file(self):
        highscores.save(self.path, entries(1))
        self.assertEqual(os.listdir(self._tmp.name), ["highscores.json"])

    def test_R19_save_error_message(self):
        error = FileNotFoundError(2, "No such file or directory")
        self.assertEqual(highscores.save_error_message(error),
                         "Could not save high scores: No such file or directory.")

    def test_R19_save_to_missing_folder_raises_oserror(self):
        with self.assertRaises(OSError):
            highscores.save(os.path.join(self._tmp.name, "no", "x.json"),
                            entries(1))

    def test_R19_default_file_is_next_to_the_questions(self):
        self.assertEqual(highscores.DEFAULT_SCORES_PATH,
                         os.path.join(PACKAGE_DIR, "highscores.json"))


class TestR20TopTen(TempDirTestCase):
    def test_R20_list_holds_at_most_ten(self):
        self.assertEqual(highscores.MAX_ENTRIES, 10)
        result = []
        for p in range(15):
            result = highscores.add_entry(result, Entry(f"P{p}", p, "S", "Easy"))
        self.assertEqual(len(result), 10)
        self.assertEqual([e.points for e in result], list(range(14, 4, -1)))

    def test_R20_score_below_tenth_is_dropped(self):
        full = entries(*range(20, 10, -1))
        result = highscores.add_entry(full, Entry("Low", 5, "S", "Easy"))
        self.assertEqual(result, full)

    def test_R20_score_above_tenth_pushes_lowest_out(self):
        full = entries(*range(20, 10, -1))
        result = highscores.add_entry(full, Entry("New", 15, "S", "Easy"))
        self.assertEqual(len(result), 10)
        self.assertIn(Entry("New", 15, "S", "Easy"), result)
        self.assertNotIn(full[-1], result)

    def test_R20_tie_with_tenth_does_not_get_in(self):
        full = entries(*range(20, 10, -1))
        result = highscores.add_entry(full, Entry("Tie", 11, "S", "Easy"))
        self.assertEqual(result, full)

    def test_R20_add_entry_does_not_change_its_argument(self):
        before = entries(5, 3)
        copy = list(before)
        highscores.add_entry(before, Entry("New", 4, "S", "Easy"))
        self.assertEqual(before, copy)

    def test_R20_file_with_more_than_ten_is_cut_to_ten_on_load(self):
        self.write(json.dumps({"scores": [entry_data(f"P{p}", p)
                                          for p in range(12)]}))
        loaded, corrupted = highscores.load(self.path)
        self.assertFalse(corrupted)
        self.assertEqual([e.points for e in loaded], list(range(11, 1, -1)))


class TestR21HighestFirst(TempDirTestCase):
    def test_R21_add_entry_keeps_highest_first(self):
        result = []
        for p in (3, 12, 1, 5):
            result = highscores.add_entry(result, Entry(f"P{p}", p, "S", "Easy"))
        self.assertEqual([e.points for e in result], [12, 5, 3, 1])

    def test_R21_equal_points_keep_older_entry_first(self):
        result = highscores.add_entry(entries(5), Entry("Newer", 5, "S", "Easy"))
        self.assertEqual([e.name for e in result], ["P0", "Newer"])

    def test_R21_load_sorts_highest_first_keeping_file_order_for_ties(self):
        self.write(json.dumps({"scores": [
            entry_data("A", 1), entry_data("B", 7), entry_data("C", 1),
            entry_data("D", 9)]}))
        loaded, _ = highscores.load(self.path)
        self.assertEqual([e.name for e in loaded], ["D", "B", "A", "C"])

    def test_R21_table_matches_agreed_layout(self):
        table = highscores.format_high_scores([
            Entry("Ana", 12, "Science", "Hard"),
            Entry("Ben", 3, "History", "Medium"),
            Entry("Cy", 1, "Sports", "Easy"),
        ])
        self.assertEqual(table, "\n".join([
            "High Scores",
            "   1. Ana                   12 points  Science (Hard)",
            "   2. Ben                    3 points  History (Medium)",
            "   3. Cy                     1 point   Sports (Easy)",
        ]))

    def test_R21_tenth_rank_lines_up_and_zero_is_plural(self):
        table = highscores.format_high_scores(entries(*range(10, 0, -1))[:9]
                                              + [Entry("Zed", 0, "Art", "Easy")])
        self.assertEqual(table.splitlines()[-1],
                         "  10. Zed                    0 points  Art (Easy)")

    def test_R21_twenty_character_name_fills_its_column(self):
        line = highscores.format_high_scores(
            [Entry("x" * 20, 5, "Science", "Hard")]).splitlines()[1]
        self.assertEqual(line, "   1. " + "x" * 20 + "   5 points  Science (Hard)")

    def test_R21_empty_list(self):
        self.assertEqual(highscores.format_high_scores([]),
                         "High Scores\nNo high scores yet.")


class TestR24MissingFile(TempDirTestCase):
    def test_R24_missing_file_loads_as_empty_and_not_corrupted(self):
        self.assertEqual(highscores.load(self.path), ([], False))
        self.assertFalse(os.path.exists(self.path))

    def test_R24_first_save_creates_the_file(self):
        highscores.save(self.path, entries(4))
        self.assertTrue(os.path.isfile(self.path))
        self.assertEqual(len(self.read_json()["scores"]), 1)

    def test_R24_save_without_backup_creates_no_bak_file(self):
        highscores.save(self.path, entries(4))
        highscores.save(self.path, entries(5, 4))
        self.assertFalse(os.path.exists(self.path + ".bak"))


class TestR25CorruptedFile(TempDirTestCase):
    MESSAGE = "High scores could not be read, so the list starts empty."

    BAD_CONTENTS = [
        "",
        "not json",
        '{"scores": [',
        b"\xff\xfe\x00junk",
        "[]",
        '"text"',
        "{}",
        '{"scores": 5}',
        '{"scores": {"name": "Ana"}}',
        json.dumps({"scores": ["Ana"]}),
        json.dumps({"scores": [{"name": "Ana", "points": 3,
                                "category": "Science"}]}),
        json.dumps({"scores": [entry_data(name="")]}),
        json.dumps({"scores": [entry_data(name="   ")]}),
        json.dumps({"scores": [entry_data(name=7)]}),
        json.dumps({"scores": [entry_data(points=-1)]}),
        json.dumps({"scores": [entry_data(points=2.5)]}),
        json.dumps({"scores": [entry_data(points="12")]}),
        json.dumps({"scores": [entry_data(points=True)]}),
        json.dumps({"scores": [entry_data(category="")]}),
        json.dumps({"scores": [entry_data(category=None)]}),
        json.dumps({"scores": [entry_data(difficulty="Expert")]}),
        json.dumps({"scores": [entry_data(difficulty="hard")]}),
        json.dumps({"scores": [entry_data(), entry_data(points=None)]}),
    ]

    def test_R25_message_text(self):
        self.assertEqual(highscores.UNREADABLE_MESSAGE, self.MESSAGE)

    def test_R25_every_kind_of_corruption_loads_as_empty(self):
        for content in self.BAD_CONTENTS:
            with self.subTest(content=content):
                self.write(content)
                self.assertEqual(highscores.load(self.path), ([], True))

    def test_R25_one_bad_entry_discards_the_whole_list(self):
        self.write(json.dumps({"scores": [entry_data("Good", 9),
                                          entry_data(points=-5)]}))
        self.assertEqual(highscores.load(self.path), ([], True))

    def test_R25_extra_keys_are_ignored(self):
        data = entry_data("Ana", 4)
        data["when"] = "yesterday"
        self.write(json.dumps({"scores": [data], "version": 1}))
        self.assertEqual(highscores.load(self.path),
                         ([Entry("Ana", 4, "Science", "Hard")], False))

    def test_R25_unreadable_path_loads_as_empty(self):
        os.mkdir(self.path)  # a folder where the file should be
        self.assertEqual(highscores.load(self.path), ([], True))

    def test_R25_save_with_backup_keeps_the_bad_file_as_bak(self):
        self.write("not json")
        highscores.save(self.path, entries(4), backup=True)
        with open(self.path + ".bak", encoding="utf-8") as f:
            self.assertEqual(f.read(), "not json")
        self.assertEqual(self.read_json(),
                         {"scores": [entry_data("P0", 4, "Science", "Easy")]})

    def test_R25_backup_replaces_an_older_bak(self):
        with open(self.path + ".bak", "w", encoding="utf-8") as f:
            f.write("old backup")
        self.write("{broken")
        highscores.save(self.path, entries(4), backup=True)
        with open(self.path + ".bak", encoding="utf-8") as f:
            self.assertEqual(f.read(), "{broken")

    def test_R25_backup_of_a_vanished_file_is_skipped(self):
        highscores.save(self.path, entries(4), backup=True)
        self.assertTrue(os.path.isfile(self.path))
        self.assertFalse(os.path.exists(self.path + ".bak"))

    def test_R25_folder_in_the_way_is_not_renamed(self):
        os.mkdir(self.path)
        with self.assertRaises(OSError):
            highscores.save(self.path, entries(4), backup=True)
        self.assertTrue(os.path.isdir(self.path))
        self.assertFalse(os.path.exists(self.path + ".bak"))


if __name__ == "__main__":
    unittest.main()
