"""Pull, commit, and push one repository.

Usage: python -X utf8 src/index.py <update|commit|push|all>
"""

import datetime
import os
import subprocess
import sys
from pathlib import Path

from i18n import t

PLUGIN_DIR = Path(__file__).resolve().parent.parent

# repo.txt holds the absolute path of the repository to sync.
# commit-message.txt is optional; without it the commit message is "update <time>".
CONFIG_DIR = Path(os.environ.get("HERDR_PLUGIN_CONFIG_DIR") or PLUGIN_DIR / "config")


class PluginError(Exception):
    pass


def read_config(name):
    file = CONFIG_DIR / name
    if not file.exists():
        return None
    return file.read_text(encoding="utf-8-sig").strip()


def git(repo, args):
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise PluginError(t("error.git_failed", args=" ".join(args), stderr=result.stderr.strip()))
    return result.stdout.strip()


def update(repo):
    before = git(repo, ["rev-parse", "HEAD"])
    git(repo, ["pull", "--ff-only"])
    after = git(repo, ["rev-parse", "HEAD"])
    if before == after:
        print(t("update.up_to_date"))
        return
    count = git(repo, ["rev-list", "--count", f"{before}..{after}"])
    print(t("update.pulled", count=count))


def commit(repo):
    changed = git(repo, ["status", "--porcelain"])
    if changed == "":
        print(t("commit.nothing"))
        return
    message = read_config("commit-message.txt") or f"update {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    git(repo, ["add", "-A"])
    git(repo, ["commit", "-m", message])
    print(t("commit.done", count=len(changed.split("\n")), message=message))


def push(repo):
    ahead = git(repo, ["rev-list", "--count", "@{u}..HEAD"])
    if ahead == "0":
        print(t("push.nothing"))
        return
    git(repo, ["push"])
    print(t("push.done", count=ahead))


def main(action):
    repo = read_config("repo.txt")
    if not repo:
        raise PluginError(t("error.no_repo_config", path=CONFIG_DIR / "repo.txt"))

    match action:
        case "update":
            update(repo)
        case "commit":
            commit(repo)
        case "push":
            push(repo)
        case "all":
            update(repo)
            commit(repo)
            push(repo)
        case _:
            raise PluginError(t("error.unknown_action", action=action))


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "")
    except (PluginError, OSError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
