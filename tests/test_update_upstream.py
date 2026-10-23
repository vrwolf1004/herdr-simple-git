import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_gitstatus import SRC, git, make_repo

import index  # noqa: E402

LOCALES = sorted((SRC / "locales").glob("*.json"))
GIT_IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def run_update(repo):
    """update 를 실행하고 출력 줄과 git 호출 목록을 돌려준다 (pull 이 실행됐는지 확인용)."""
    printed = []
    calls = []
    real_git = index.git

    def spy(repo_path, args):
        calls.append(list(args))
        return real_git(repo_path, args)

    with mock.patch.object(index, "git", side_effect=spy), \
            mock.patch.dict(os.environ, GIT_IDENTITY), \
            mock.patch("builtins.print", side_effect=lambda *args: printed.append(" ".join(map(str, args)))):
        index.update(str(repo))
    return printed, calls


def add_remote_commit(root, remote, name):
    """bare 원격에 새 커밋을 하나 올린다 (다른 복제본에서)."""
    other = Path(root) / name
    git(Path(root), "clone", "-q", str(remote), str(other))
    (other / "remote.txt").write_text("remote", encoding="utf-8")
    git(other, "add", "-A")
    git(other, "commit", "-q", "-m", "remote change")
    git(other, "push", "-q", "origin", "main")


class UpdateWithoutCommitsTest(unittest.TestCase):
    def test_empty_repo_gives_one_guidance_line_without_git_error(self):
        with tempfile.TemporaryDirectory() as root:
            repo = Path(root) / "empty"
            repo.mkdir()
            git(repo, "init", "-q", "-b", "main")
            printed, calls = run_update(repo)
        self.assertFalse(any(args[:1] == ["pull"] for args in calls), calls)
        self.assertEqual(printed, [index.t("update.no_commits")])


class UpdateWithoutUpstreamTest(unittest.TestCase):
    def test_without_upstream_it_does_not_pull_and_gives_guidance(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            printed, calls = run_update(repo)
        self.assertFalse(any(args[:1] == ["pull"] for args in calls), calls)
        self.assertEqual(printed, [index.t("update.no_upstream", branch="main")])
        self.assertIn("git push -u origin main", printed[0])

    def test_detached_head_gives_its_own_message_and_does_not_pull(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            git(repo, "checkout", "-q", "--detach")
            printed, calls = run_update(repo)
        self.assertFalse(any(args[:1] == ["pull"] for args in calls), calls)
        self.assertEqual(printed, [index.t("update.detached")])


class UpdateWithUpstreamTest(unittest.TestCase):
    def test_with_upstream_it_pulls_and_reports_the_count(self):
        with tempfile.TemporaryDirectory() as root:
            remote = Path(root) / "remote.git"
            git(Path(root), "init", "-q", "--bare", "-b", "main", str(remote))
            repo = make_repo(root)
            git(repo, "remote", "add", "origin", str(remote))
            git(repo, "push", "-q", "-u", "origin", "main")
            add_remote_commit(root, remote, "other")
            printed, calls = run_update(repo)
        self.assertTrue(any(args[:2] == ["pull", "--ff-only"] for args in calls), calls)
        self.assertEqual(printed, [index.t("update.pulled", count="1")])

    def test_with_upstream_and_nothing_new_reports_up_to_date(self):
        with tempfile.TemporaryDirectory() as root:
            remote = Path(root) / "remote.git"
            git(Path(root), "init", "-q", "--bare", "-b", "main", str(remote))
            repo = make_repo(root)
            git(repo, "remote", "add", "origin", str(remote))
            git(repo, "push", "-q", "-u", "origin", "main")
            printed, _ = run_update(repo)
        self.assertEqual(printed, [index.t("update.up_to_date")])


class UpdateLocaleKeysTest(unittest.TestCase):
    def test_every_language_has_the_same_keys_including_the_new_ones(self):
        key_sets = {}
        for path in LOCALES:
            data = json.loads(path.read_text(encoding="utf-8"))
            key_sets[path.name] = set(data)
            for key in ("update.no_upstream", "update.detached", "update.no_commits"):
                self.assertTrue(data.get(key), f"{path.name} 에 {key} 가 없다")
        reference = key_sets["en.json"]
        for name, keys in key_sets.items():
            self.assertEqual(keys, reference, name)


if __name__ == "__main__":
    unittest.main()
