"""Pull, commit, and push one repository.

Usage: python -X utf8 src/index.py <update|commit|push|all>
"""

import datetime
import fnmatch
import os
import subprocess
import sys
from pathlib import Path

from gitstatus import parse_status_z
from i18n import t

PLUGIN_DIR = Path(__file__).resolve().parent.parent

# repo.txt holds the absolute path of the repository to sync.
# commit-message.txt is optional; without it the commit message is "update <time>".
CONFIG_DIR = Path(os.environ.get("HERDR_PLUGIN_CONFIG_DIR") or PLUGIN_DIR / "config")

# Windows 에서 git 이 콘솔 창을 띄우지 않게 한다 (herdr-radio 와 같은 방식)
NO_WINDOW = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}


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
        **NO_WINDOW,
    )
    if result.returncode != 0:
        raise PluginError(t("error.git_failed", args=" ".join(args), stderr=result.stderr.strip()))
    return result.stdout.strip()


def has_commits(repo):
    result = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--verify", "--quiet", "HEAD"],
        capture_output=True,
        text=True,
        **NO_WINDOW,
    )
    return result.returncode == 0


def update(repo):
    if not has_commits(repo):
        # 커밋이 없으면 HEAD 를 풀 수 없어 git 오류가 난다. 먼저 커밋하라고 알려 준다.
        print(t("update.no_commits"))
        return
    branch = git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    if branch == "HEAD":
        print(t("update.detached"))
        return
    if not has_upstream(repo):
        # upstream 이 없으면 pull 하지 않고 다음에 할 일을 알려 준다 (push 와 같은 안내).
        print(t("update.no_upstream", branch=branch))
        return
    before = git(repo, ["rev-parse", "HEAD"])
    git(repo, ["pull", "--ff-only"])
    after = git(repo, ["rev-parse", "HEAD"])
    if before == after:
        print(t("update.up_to_date"))
        return
    count = git(repo, ["rev-list", "--count", f"{before}..{after}"])
    print(t("update.pulled", count=count))


def git_raw(repo, args):
    """앞뒤 공백을 지우지 않은 출력. porcelain 의 첫 글자가 공백인 항목을 잘못 자르지 않게 한다."""
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        **NO_WINDOW,
    )
    if result.returncode != 0:
        raise PluginError(t("error.git_failed", args=" ".join(args), stderr=result.stderr.strip()))
    return result.stdout


# 이름만 보고 민감해 보이는 파일을 찾는다 (내용은 읽지 않는다). 커밋을 막지는 않는다.
SENSITIVE_PATTERNS = (".env", ".env.*", "*.pem", "*.key", "id_rsa")


def sensitive_paths(paths):
    return [path for path in paths
            if any(fnmatch.fnmatch(os.path.basename(path), pattern) for pattern in SENSITIVE_PATTERNS)]


def commit(repo):
    entries = parse_status_z(git_raw(repo, ["status", "--porcelain=v1", "-z"]))
    if not entries:
        print(t("commit.nothing"))
        return
    message = read_config("commit-message.txt") or f"update {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    # 스테이징될 파일 목록을 먼저 보여 준다 (git add -A 가 잡는 목록과 같다)
    print(t("commit.staging_header"))
    for code, path in entries:
        print(f"  {code} {path}")
    sensitive = sensitive_paths(path for _, path in entries)
    if sensitive:
        print(t("commit.sensitive_warning", files=", ".join(sensitive)))
    git(repo, ["add", "-A"])
    git(repo, ["commit", "-m", message])
    print(t("commit.done", count=len(entries), message=message))


def has_upstream(repo):
    result = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        capture_output=True,
        text=True,
        **NO_WINDOW,
    )
    return result.returncode == 0


def push(repo):
    branch = git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    if branch == "HEAD":
        print(t("push.detached"))
        return
    if not has_upstream(repo):
        # upstream 이 없으면 @{u} 를 조회할 수 없다. 다음에 할 일을 알려 준다.
        print(t("push.no_upstream", branch=branch))
        return
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
