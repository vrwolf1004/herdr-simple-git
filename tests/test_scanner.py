import os
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
os.environ.setdefault("HERDR_SIMPLE_GIT_LANG", "en")

import dock  # noqa: E402


class RepoScannerTest(unittest.TestCase):
    def wait_for(self, scanner, folder, timeout=3.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            scanned, repos = scanner.latest()
            if scanned == folder:
                return repos
            time.sleep(0.02)
        self.fail("scan did not finish")

    def test_request_fills_results_in_background(self):
        with mock.patch.object(dock, "find_repos", return_value=["/x/a", "/x/b"]), \
                mock.patch.object(dock, "repo_status", side_effect=lambda p: {"name": os.path.basename(p)}), \
                mock.patch.object(dock, "SCAN_MIN_SECONDS", 0):
            scanner = dock.RepoScanner()
            scanner.request("/x")
            repos = self.wait_for(scanner, "/x")
        self.assertEqual([r["name"] for r in repos], ["a", "b"])

    def test_latest_is_empty_before_any_request(self):
        with mock.patch.object(dock, "SCAN_MIN_SECONDS", 0):
            scanner = dock.RepoScanner()
        self.assertEqual(scanner.latest(), (None, []))


if __name__ == "__main__":
    unittest.main()
