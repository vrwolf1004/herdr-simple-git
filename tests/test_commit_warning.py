import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

from test_gitstatus import SRC, make_repo

import index  # noqa: E402

LOCALES = sorted((SRC / "locales").glob("*.json"))
NEW_KEYS = ("commit.staging_header", "commit.sensitive_warning")
GIT_IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def commit_and_collect(repo):
    printed = []
    with mock.patch.object(index, "read_config", return_value=None), \
            mock.patch.dict(os.environ, GIT_IDENTITY), \
            mock.patch("builtins.print", side_effect=lambda *args: printed.append(" ".join(map(str, args)))):
        index.commit(str(repo))
    return printed


def commit_count(repo):
    out = subprocess.run(["git", "-C", str(repo), "rev-list", "--count", "HEAD"],
                         check=True, capture_output=True, text=True)
    return int(out.stdout.strip())


class SensitivePathsTest(unittest.TestCase):
    def test_matches_secret_like_basenames_in_any_folder(self):
        paths = ["app/.env", ".env.local", "certs/server.pem", "keys/id.key", "ssh/id_rsa",
                 "src/main.py", "docs/key-notes.md", "envfile.txt"]
        self.assertEqual(index.sensitive_paths(paths),
                         ["app/.env", ".env.local", "certs/server.pem", "keys/id.key", "ssh/id_rsa"])

    def test_no_sensitive_names(self):
        self.assertEqual(index.sensitive_paths(["a.txt", "b/c.py"]), [])


class CommitWarningTest(unittest.TestCase):
    def test_lists_staged_files_and_warns_about_env_then_commits(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            (repo / ".env").write_text("TOKEN=<DUMMY_TOKEN>", encoding="utf-8")
            (repo / "a.txt").write_text("changed", encoding="utf-8")
            before = commit_count(repo)
            printed = commit_and_collect(repo)
            after = commit_count(repo)
        self.assertEqual(after, before + 1)  # 경고가 있어도 커밋은 진행된다
        self.assertEqual(printed[0], index.t("commit.staging_header"))
        self.assertIn("  ?? .env", printed)
        self.assertIn("   M a.txt", printed)  # 상태 코드 " M" 앞에 들여쓰기 2칸
        warning = index.t("commit.sensitive_warning", files=".env")
        self.assertIn(warning, printed)
        self.assertLess(printed.index("  ?? .env"), printed.index(warning))  # 목록 뒤에 경고
        self.assertNotEqual(printed[-1], warning)  # 마지막 줄은 커밋 완료 메시지

    def test_no_warning_without_sensitive_files_and_commit_happens(self):
        with tempfile.TemporaryDirectory() as root:
            repo = make_repo(root)
            (repo / "new.txt").write_text("x", encoding="utf-8")
            before = commit_count(repo)
            printed = commit_and_collect(repo)
            after = commit_count(repo)
        self.assertEqual(after, before + 1)
        self.assertEqual(printed[0], index.t("commit.staging_header"))
        self.assertIn("  ?? new.txt", printed)
        self.assertFalse(any("sensitive" in line or "warning" in line.lower() for line in printed))
        self.assertNotIn(index.t("commit.sensitive_warning", files="new.txt"), printed)


class LocaleKeysTest(unittest.TestCase):
    def test_every_language_has_the_same_keys_including_the_new_ones(self):
        key_sets = {}
        for path in LOCALES:
            data = json.loads(path.read_text(encoding="utf-8"))
            key_sets[path.name] = set(data)
            for key in NEW_KEYS:
                self.assertTrue(data.get(key), f"{path.name} 에 {key} 가 없다")
        reference = key_sets["en.json"]
        for name, keys in key_sets.items():
            self.assertEqual(keys, reference, name)
        self.assertEqual(len(LOCALES), 7)


if __name__ == "__main__":
    unittest.main()
