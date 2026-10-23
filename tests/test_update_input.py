import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
os.environ.setdefault("HERDR_SIMPLE_GIT_LANG", "en")

import dock  # noqa: E402

REPOS = ["C:/work/app/alpha", "C:/work/app/herdr-tetris", "C:/work/app/beta"]


class UpdateInputTest(unittest.TestCase):
    def test_number_selects_repo_and_names_it(self):
        with mock.patch.object(dock, "find_repos", return_value=REPOS), \
                mock.patch.object(dock, "pull_repo") as pull:
            _, redraw, notice, selected = dock.handle_input("2", "C:/work/app", None)
        pull.assert_not_called()
        self.assertTrue(redraw)
        self.assertEqual(selected, REPOS[1])
        self.assertEqual(notice, "Selected: herdr-tetris, type u to update (pull)")

    def test_number_then_u_pulls_selected_repo(self):
        with mock.patch.object(dock, "find_repos", return_value=REPOS), \
                mock.patch.object(dock, "pull_repo", return_value=True) as pull:
            _, _, _, selected = dock.handle_input("2", "C:/work/app", None)
            _, redraw, notice, selected = dock.handle_input("u", "C:/work/app", selected)
        pull.assert_called_once_with(REPOS[1])
        self.assertTrue(redraw)
        self.assertIsNone(selected)
        self.assertEqual(notice, "herdr-tetris update (pull) completed")

    def test_u_is_case_insensitive(self):
        with mock.patch.object(dock, "pull_repo", return_value=True) as pull:
            dock.handle_input("U", "C:/work/app", REPOS[0])
        pull.assert_called_once_with(REPOS[0])

    def test_failed_pull_reports_failure_and_clears_selection(self):
        with mock.patch.object(dock, "pull_repo", return_value=False):
            _, _, notice, selected = dock.handle_input("u", "C:/work/app", REPOS[0])
        self.assertEqual(notice, "alpha update (pull) failed (check local changes or divergence)")
        self.assertIsNone(selected)

    def test_u_without_selection_does_not_pull(self):
        with mock.patch.object(dock, "pull_repo") as pull:
            _, redraw, notice, selected = dock.handle_input("u", "C:/work/app", None)
        pull.assert_not_called()
        self.assertTrue(redraw)
        self.assertIsNone(selected)
        self.assertEqual(notice, "Enter a repo number first")

    def test_other_input_clears_selection(self):
        with mock.patch.object(dock, "find_repos", return_value=REPOS), \
                mock.patch.object(dock, "pull_repo") as pull:
            for text in ("/refresh", ""):
                _, _, _, selected = dock.handle_input(text, "C:/work/app", REPOS[1])
                self.assertIsNone(selected, text)
                dock.handle_input("u", "C:/work/app", selected)
        pull.assert_not_called()

    def test_another_number_replaces_selection(self):
        with mock.patch.object(dock, "find_repos", return_value=REPOS), \
                mock.patch.object(dock, "pull_repo") as pull:
            _, _, notice, selected = dock.handle_input("3", "C:/work/app", REPOS[1])
        pull.assert_not_called()
        self.assertEqual(selected, REPOS[2])
        self.assertEqual(notice, "Selected: beta, type u to update (pull)")

    def test_number_out_of_range_selects_nothing(self):
        with mock.patch.object(dock, "find_repos", return_value=REPOS), \
                mock.patch.object(dock, "pull_repo") as pull:
            _, redraw, notice, selected = dock.handle_input("9", "C:/work/app", REPOS[0])
        pull.assert_not_called()
        self.assertTrue(redraw)
        self.assertIsNone(selected)
        self.assertEqual(notice, "Repo not found: 9")

    def test_number_alone_is_not_treated_as_folder(self):
        with mock.patch.object(dock, "find_repos", return_value=[]), \
                mock.patch.object(dock, "save_folder") as save:
            _, _, notice, _ = dock.handle_input("10", "C:/work/app", None)
        save.assert_not_called()
        self.assertEqual(notice, "Repo not found: 10")

    def test_folder_path_still_sets_folder_and_clears_selection(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(dock, "save_folder") as save, \
                mock.patch.object(dock, "pull_repo") as pull:
            folder, redraw, notice, selected = dock.handle_input(tmp, "C:/work/app", REPOS[0])
            pull.assert_not_called()
        save.assert_called_once_with(os.path.abspath(tmp))
        self.assertEqual(folder, os.path.abspath(tmp))
        self.assertTrue(redraw)
        self.assertIsNone(selected)
        self.assertEqual(notice, f"Folder set: {os.path.abspath(tmp)}")

    def test_missing_folder_path_reports_missing(self):
        with mock.patch.object(dock, "save_folder") as save:
            folder, _, notice, selected = dock.handle_input("no-such-dir-xyz", "C:/work/app", None)
        save.assert_not_called()
        self.assertEqual(folder, "C:/work/app")
        self.assertIsNone(selected)
        self.assertIn("no-such-dir-xyz", notice)


if __name__ == "__main__":
    unittest.main()
