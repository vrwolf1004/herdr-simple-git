import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
os.environ.setdefault("HERDR_SIMPLE_GIT_LANG", "en")

import dock  # noqa: E402
import gitstatus  # noqa: E402
import index  # noqa: E402


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


def make_repo(root):
    repo = Path(root) / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "a.txt").write_text("a", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo


class ParseStatusTest(unittest.TestCase):
    def test_rename_counts_once_and_skips_original_path(self):
        output = "## main\0R  new name.txt\0old name.txt\0 M other.txt\0?? untracked file.txt\0"
        entries = gitstatus.parse_status_z(output)
        self.assertEqual(entries, [("R ", "new name.txt"), (" M", "other.txt"), ("??", "untracked file.txt")])

    def test_newline_in_path_is_kept(self):
        output = "## main\0?? odd\nname.txt\0"
        self.assertEqual(gitstatus.parse_status_z(output), [("??", "odd\nname.txt")])


class ParseBranchTest(unittest.TestCase):
    def test_upstream_and_ahead(self):
        header = "## main...origin/main [ahead 2]"
        self.assertEqual(gitstatus.parse_branch(header), "main")
        self.assertEqual(gitstatus.ahead_count(header), 2)

    def test_no_commits_yet(self):
        self.assertEqual(gitstatus.parse_branch("## No commits yet on develop"), "develop")

    def test_detached_head(self):
        self.assertEqual(gitstatus.parse_branch("## HEAD (no branch)"), "HEAD")

    def test_branch_with_slash_and_no_upstream(self):
        self.assertEqual(gitstatus.parse_branch("## feature/x"), "feature/x")
        self.assertEqual(gitstatus.ahead_count("## feature/x"), 0)


class RealRepoTest(unittest.TestCase):
    def test_repo_status_counts_entries_with_spaces_in_names(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            (repo / "with space.txt").write_text("x", encoding="utf-8")
            (repo / "a.txt").write_text("changed", encoding="utf-8")
            status = dock.repo_status(str(repo))
        self.assertEqual(status["branch"], "main")
        self.assertEqual(status["changed"], 2)
        self.assertFalse(status["error"])

    def test_commit_counts_rename_as_one_entry(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            git(repo, "mv", "a.txt", "renamed file.txt")
            with mock.patch.object(index, "read_config", return_value=None), \
                    mock.patch("builtins.print") as printed:
                index.commit(str(repo))
        printed_text = printed.call_args[0][0]
        self.assertIn("1", printed_text)  # rename 은 항목 하나로 센다

    def test_push_without_upstream_gives_guidance(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            with mock.patch("builtins.print") as printed:
                index.push(str(repo))
        printed_text = printed.call_args[0][0]
        self.assertIn("upstream", printed_text)
        self.assertIn("git push -u origin main", printed_text)

    def test_detached_head_push_message(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            git(repo, "checkout", "-q", "--detach")
            with mock.patch("builtins.print") as printed:
                index.push(str(repo))
        self.assertIn("detached", printed.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
