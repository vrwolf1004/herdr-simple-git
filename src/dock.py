"""herdr-simple-git dock: one agent in the shared herdr-dock workspace that shows how many git repos a folder has.

Focus the agent to see the repos and their state. Type a folder path in that pane to choose the folder.
Only git repos directly under the chosen folder are listed. Everything is local: no fetch, no network.

Commands
  start   show the dock agent (creates the herdr-dock workspace and pane when needed)
  stop    release the agent and close its pane
  host    loop that runs inside the dock pane (started by start)

Agent state: blocked if a repo cannot be read, working if a repo has changes or unpushed commits, idle otherwise.
"""

import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
from pathlib import Path

import herdr_api


def load_dock_layout():
    """설치된 herdr-dock-grid 가 있으면 그 원본을, 없으면 이 plugin 의 복사본(src/dock_layout.py)을 쓴다."""
    grid = herdr_api.installed_plugin_path("herdr-dock-grid")
    if grid:
        sys.path.insert(0, os.path.join(grid, "src"))
    import dock_layout
    return dock_layout


dock = load_dock_layout()
from gitstatus import ahead_count, behind_count, parse_branch, parse_status_z


def _apply_flags_to_environment(argv):
    """host 는 herdr 가 준 HERDR_PLUGIN_* 환경변수 없이 pane 에서 뜬다. start 가 넘긴 경로와 언어를
    i18n 이 import 되기 전에 환경변수로 옮긴다."""
    flags = {"--state": "HERDR_PLUGIN_STATE_DIR", "--config": "HERDR_PLUGIN_CONFIG_DIR", "--lang": "HERDR_SIMPLE_GIT_LANG"}
    for flag, name in flags.items():
        if flag in argv and argv.index(flag) + 1 < len(argv):
            os.environ[name] = argv[argv.index(flag) + 1]


_apply_flags_to_environment(sys.argv)

import i18n  # noqa: E402
from i18n import t  # noqa: E402

SOURCE = "plugin:herdr-simple-git"
DOCK_LABEL = "herdr-dock"
# 도크 블록이 3개일 때 빈 4번째 칸에 띄우는 소개 pane 의 이름 (정의는 intro.py 에 있다)
INTRO_LABEL = "herdr-dock-intro"
INTRO_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intro.py")
AGENT_ID = "git"
TICK_SECONDS = 5
INPUT_POLL_SECONDS = 0.5
TOKEN_TTL_MS = 15_000
LAYOUT_EVERY_TICKS = 3
ALIVE_WITHIN_SECONDS = 15
GIT_TIMEOUT_SECONDS = 10
GIT_PULL_TIMEOUT_SECONDS = 120  # 원격 pull 은 네트워크를 타므로 상태 조회보다 길게 기다린다
SCAN_MIN_SECONDS = 2  # 백그라운드 스캔은 이 간격보다 자주 하지 않는다
# Windows 에서 git 이 콘솔 창을 띄우지 않게 한다 (herdr-radio 와 같은 방식)
NO_WINDOW = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
CURSOR_HOME = "\x1b[H"
PROMPT = "> "
ERASE_LINE = "\x1b[K"
ERASE_BELOW = "\x1b[J"
AGENT_RANK = {"idle": 0, "working": 1, "blocked": 2}
BOX_MIN_INNER = 44
BOX_MAX_INNER = 64
# 도크 화면 테마 (t 키로 순서대로 바꾼다). 빈 문자열은 터미널 기본색이다.
THEMES = {
    "phosphor": "\x1b[38;2;51;255;51m",  # 형광 녹색 #33FF33
    "amber": "\x1b[38;2;255;176;0m",     # 호박색 #FFB000
    "default": "",
}
DEFAULT_THEME = "phosphor"
HELP_TOKEN = "\x00help"  # Ctrl+H 가 입력 맨 앞에서 눌렸을 때 입력 큐에 넣는 값 (Windows)

PLUGIN_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- paths and state


def state_dir():
    return Path(os.environ.get("HERDR_PLUGIN_STATE_DIR") or PLUGIN_DIR / "state")


def config_dir():
    return Path(os.environ.get("HERDR_PLUGIN_CONFIG_DIR") or PLUGIN_DIR / "config")


def read_state(name):
    try:
        return (state_dir() / name).read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def write_state(name, value):
    # 임시 파일에 쓰고 바꿔 끼운다. 중간에 멈춰도 읽는 쪽은 예전 값이나 새 값 중 하나만 본다.
    state_dir().mkdir(parents=True, exist_ok=True)
    target = state_dir() / name
    temp = target.with_name(target.name + ".tmp")
    temp.write_text(value, encoding="utf-8")
    os.replace(temp, target)


def remove_state(name):
    try:
        (state_dir() / name).unlink()
    except OSError:
        pass


def recently(name):
    try:
        return time.time() - float(read_state(name)) < ALIVE_WITHIN_SECONDS
    except ValueError:
        return False


def load_config():
    try:
        data = json.loads((config_dir() / "config.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_folder(folder):
    data = load_config()
    data["folder"] = folder
    config_dir().mkdir(parents=True, exist_ok=True)
    (config_dir() / "config.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------- repos


def find_repos(folder):
    """folder 바로 아래 폴더 중 .git 이 있는 것."""
    if not folder or not os.path.isdir(folder):
        return []
    return [
        os.path.join(folder, name)
        for name in sorted(os.listdir(folder))
        if os.path.exists(os.path.join(folder, name, ".git"))
    ]


def repo_status(path):
    status = {"name": os.path.basename(path), "branch": "", "changed": 0, "ahead": 0, "behind": 0, "error": False}
    try:
        result = subprocess.run(
            ["git", "-C", path, "status", "--porcelain=v1", "-b", "-z"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT_SECONDS,
            **NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired):
        status["error"] = True
        return status
    if result.returncode != 0:
        status["error"] = True
        return status
    header = next((token for token in result.stdout.split("\0") if token.startswith("## ")), "")
    if header:
        status["branch"] = parse_branch(header)
        status["ahead"] = ahead_count(header)
        status["behind"] = behind_count(header)
    status["changed"] = len(parse_status_z(result.stdout))
    return status


def repo_state(repo):
    if repo["error"]:
        return "blocked"
    if repo["changed"] or repo["ahead"]:
        return "working"
    return "idle"


def agent_state(repos):
    return max((repo_state(repo) for repo in repos), key=AGENT_RANK.get, default="idle")


def display_width(text):
    """터미널에서 차지하는 칸 수. 한글과 전각 문자는 두 칸으로 세고, 색 코드는 세지 않는다."""
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    return sum(2 if unicodedata.east_asian_width(char) in ("W", "F") else 1 for char in text)


def pad_to(text, width):
    return text + " " * max(0, width - display_width(text))


def wrap(text, width):
    """공백 기준으로 접고, 공백 없이 너무 긴 말만 글자 단위로 자른다."""
    lines, current = [], ""
    for word in text.split(" "):
        candidate = word if not current else current + " " + word
        if display_width(candidate) <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        for char in word:
            if display_width(current + char) > width:
                lines.append(current)
                current = char
            else:
                current += char
    lines.append(current)
    return lines


def repo_line(repo, number):
    if repo["error"]:
        detail = t("dock.error")
    else:
        parts = []
        if repo["changed"]:
            parts.append(t("dock.changed", count=repo["changed"]))
        if repo["behind"]:
            parts.append(t("dock.behind", count=repo["behind"]))
        if repo["ahead"]:
            parts.append(t("dock.ahead", count=repo["ahead"]))
        detail = ", ".join(parts) or t("dock.clean")
    return f"{number:>2} {pad_to(repo['name'], 24)} {pad_to(repo['branch'], 14)} {detail}"


def panel(title, sections, color=""):
    """둥근 테두리 박스. sections 사이에는 구분선을 긋는다. 긴 줄은 박스 안에서 접는다. color 는 줄마다 입힌다."""
    texts = [title] + [text for section in sections for text in section]
    inner = min(BOX_MAX_INNER, max([BOX_MIN_INNER] + [display_width(text) + 2 for text in texts]))
    width = inner - 2
    out = ["╭" + "─" * inner + "╮"]
    left = max(0, (inner - display_width(title)) // 2)
    out.append("│" + pad_to(" " * left + title, inner) + "│")
    out.append("├" + "─" * inner + "┤")
    for index, section in enumerate(sections):
        if index:
            out.append("├" + "─" * inner + "┤")
        for text in section:
            # 짧은 줄은 접지 않는다. 접으면 앞쪽 공백(오른쪽 정렬)이 사라진다
            for piece in (wrap(text, width) if display_width(text) > width else [text]):
                out.append("│ " + pad_to(piece, width) + " │")
    out.append("╰" + "─" * inner + "╯")
    return [color + line + "\x1b[0m" for line in out]


def hint_row(width):
    """하단 줄: 오른쪽에 Ctrl+H 도움말(회색). 배경색 없이 글자만 쓴다."""
    text = t("hint.help")
    return " " * max(0, width - display_width(text)) + "[2m" + text + "[22m"


def shortcut_rows(text):
    """도움말 문구(항목 사이 세 칸)를 팝업 줄 목록으로 나눈다."""
    return [row.strip() for row in text.strip().split("   ")]


def overlay_popup(lines, rows, color):
    """lines 가운데에 도움말 팝업 상자를 덮어쓴다. 팝업 밖의 줄은 그대로 남는다."""
    popup = panel(t("hint.help"), [rows], color)
    width = display_width(lines[0])
    left = max(0, (width - display_width(popup[0])) // 2)
    top = max(0, (len(lines) - len(popup)) // 2)
    for index, row in enumerate(popup[:len(lines) - top]):
        lines[top + index] = " " * left + row


def build_screen(folder, repos, max_rows, notice="", color="", help_open=False):
    if not folder:
        body = [t("dock.no_folder")]
    elif not os.path.isdir(folder):
        body = [t("dock.folder_missing", path=folder)]
    else:
        body = [t("dock.folder", folder=folder)]
    if notice:
        body.append(notice)
    if folder and os.path.isdir(folder):
        listing = [repo_line(repo, number) for number, repo in enumerate(repos, 1)] or [t("dock.no_repos", folder=folder)]
    else:
        listing = []
    # pane 높이를 넘으면 목록 끝부터 줄인다. 맨 아래 입력줄이 들어갈 자리를 남겨야 스크롤이 생기지 않는다.
    while True:
        sections = [body] + ([listing] if listing else [])
        inner = display_width(panel("🐺  herdr-simple-git  🌕", sections)[0]) - 2
        # 힌트 줄은 상자 안쪽 너비(테두리 한 칸씩 제외)에 맞춘다. 그래야 상자 너비가 바뀌지 않는다
        lines = panel("🐺  herdr-simple-git  🌕", sections + [[hint_row(inner - 2)]], color)
        if len(lines) <= max_rows or len(listing) <= 1:
            break
        listing = listing[:-1]
    if help_open:
        overlay_popup(lines, shortcut_rows(t("dock.help")), color)
    return "\n".join(lines)


# ---------------------------------------------------------------- herdr dock


def is_sidebar(pane):
    return any(name.startswith("herdr-sidebar") for name in (pane.get("tokens") or {}))


def workspace_panes(workspace_id):
    panes = herdr_api.cli("pane", "list").get("panes", [])
    return [p for p in panes if p["workspace_id"] == workspace_id]


def ensure_intro(workspace_id, new_pane, cwd):
    """도크 블록이 3개이고 소개 칸이 없으면 빈 4번째 칸에 소개 문구를 띄운다. 이미 있으면 아무것도 하지 않는다."""
    agent_panes = {a["pane_id"] for a in herdr_api.cli("agent", "list").get("agents", [])}
    panes = [p for p in workspace_panes(workspace_id) if not is_sidebar(p)]
    if any(p.get("label") == INTRO_LABEL for p in panes):
        return
    blocks = [p for p in panes if p["pane_id"] in agent_panes or p["pane_id"] == new_pane]
    if len(blocks) != 3:
        return
    if any(not p.get("label") and not p.get("tokens") and p["pane_id"] not in agent_panes and p["pane_id"] != new_pane
           for p in panes):
        return  # 빈 칸이 이미 있으면 그 칸은 나중 블록이 쓴다
    pane_id = dock.grid_split(blocks[0]["pane_id"], cwd)
    herdr_api.cli("pane", "rename", pane_id, INTRO_LABEL)
    herdr_api.cli("pane", "run", pane_id, sys.executable, "-X", "utf8", INTRO_SCRIPT)


DOCK_KEY = "herdr-simple-git"
def plugins_folder():
    return os.path.dirname(os.path.abspath(state_dir()))


def ensure_workspace():
    """dock workspace 와 이 plugin 이 쓸 pane 을 확보한다. 자리 배정과 정리는 herdr-dock-grid 공용 모듈이 한다."""
    workspace_id, pane_id = dock.ensure_dock_pane(DOCK_KEY, str(state_dir()))
    write_state("workspace.id", workspace_id)
    panes = workspace_panes(workspace_id)
    if any(p["pane_id"] == pane_id and p.get("label") == INTRO_LABEL for p in panes):
        herdr_api.cli("pane", "rename", pane_id, "--clear")  # 소개 칸을 블록이 쓰므로 이름을 지운다
    write_state("pane.id", pane_id)
    ensure_intro(workspace_id, pane_id, str(state_dir()))
    return workspace_id, pane_id


def keep_at_bottom():
    workspace_id = read_state("workspace.id")
    try:
        workspaces = herdr_api.request("workspace.list", {}).get("workspaces", [])
    except (herdr_api.HerdrError, ValueError):
        return
    ids = [w["workspace_id"] for w in workspaces]
    if workspace_id in ids and ids[-1] != workspace_id:
        # insert_index 는 옮기기 전 목록 기준 "이 위치 앞에 넣기"다. 길이를 주면 맨 뒤로 간다.
        herdr_api.try_request("workspace.move", {"workspace_id": workspace_id, "insert_index": len(ids)})


def report(pane_id, state, count, state_changed):
    herdr_api.try_request("pane.report_metadata", {
        "pane_id": pane_id,
        "source": SOURCE,
        "display_agent": t("dock.agent_name", count=count),
        "tokens": {},
        "ttl_ms": TOKEN_TTL_MS,
    })
    if state_changed:
        herdr_api.try_request("pane.report_agent", {
            "pane_id": pane_id,
            "source": SOURCE,
            "agent": AGENT_ID,
            "state": state,
        })


# ---------------------------------------------------------------- commands


def read_lines(lines, typed):
    """stdin 줄 입력 (Windows 가 아닌 곳). Ctrl+H 는 구분할 수 없어서 도움말 키가 없다."""
    for line in sys.stdin:
        lines.put(line.rstrip("\r\n"))


def read_keys(lines, typed):
    """Windows 콘솔의 키를 직접 읽는다. Ctrl+H 와 Backspace 는 같은 \\x08 이라, 입력이 비었을 때만 도움말로 본다.
    typed["text"] 에 지금 입력 중인 글자를 둬서 화면에 바로 보이게 한다."""
    import _thread
    import msvcrt
    buffer = []
    while True:
        if not msvcrt.kbhit():
            time.sleep(0.03)
            continue
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):  # 화살표 같은 특수키는 뒤에 한 글자가 더 온다
            msvcrt.getwch()
            continue
        if ch in ("\r", "\n"):
            lines.put("".join(buffer).strip())
            buffer.clear()
        elif ch == "\x08" and not buffer:
            lines.put(HELP_TOKEN)
        elif ch in ("\x08", "\x7f"):
            if buffer:
                buffer.pop()
        elif ch == "\x03":
            _thread.interrupt_main()  # Ctrl+C 는 본 스레드에 KeyboardInterrupt 로 전한다
        elif ch.isprintable():
            buffer.append(ch)
        typed["text"] = "".join(buffer)


def pull_repo(path):
    """fast-forward 로만 받는다. 로컬 변경이 있거나 원격과 갈라졌으면 git 이 거부하고 False 를 돌려준다."""
    try:
        result = subprocess.run(
            ["git", "-C", path, "pull", "--ff-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_PULL_TIMEOUT_SECONDS,
            **NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def handle_input(text, folder, selected):
    """입력 한 줄을 처리한다.

    돌려주는 값은 (새 folder, 바로 다시 그릴지, 화면에 남길 알림, 선택된 저장소 경로).
    번호를 치면 그 저장소를 고르고, u 를 치면 고른 저장소를 pull 한다. 그 밖의 입력은 선택을 푼다.
    """
    text = text.strip().strip('"')
    if text.lower() == "u":
        if selected is None:
            return folder, True, t("dock.update_need_number"), None
        name = os.path.basename(selected)
        if pull_repo(selected):
            return folder, True, t("dock.update_done", name=name), None
        return folder, True, t("dock.update_failed", name=name), None
    if text.isdigit():
        repos = find_repos(folder)
        number = int(text)
        if not 1 <= number <= len(repos):
            return folder, True, t("dock.update_no_repo", target=text), None
        repo = repos[number - 1]
        return folder, True, t("dock.selected", name=os.path.basename(repo)), repo
    if text in ("", "/refresh"):
        return folder, True, "", None
    path = os.path.abspath(os.path.expanduser(text))
    if os.path.isdir(path):
        save_folder(path)
        return path, True, t("dock.folder_set", folder=path), None
    return folder, True, t("dock.folder_missing", path=text), None


class RepoScanner:
    """저장소 상태를 백그라운드 스레드에서 모은다. 입력 루프는 기다리지 않고 마지막 결과를 쓴다.

    요청은 folder 를 바꿔 두고 event 를 세운다. 스캔은 SCAN_MIN_SECONDS 간격보다 자주 하지 않는다.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.wanted = None
        self.result = (None, [])  # (스캔한 folder, 저장소 상태 목록)
        self.event = threading.Event()
        threading.Thread(target=self.run, daemon=True).start()

    def request(self, folder):
        with self.lock:
            self.wanted = folder
        self.event.set()

    def latest(self):
        with self.lock:
            return self.result

    def run(self):
        while True:
            self.event.wait()
            self.event.clear()
            with self.lock:
                folder = self.wanted
            repos = [repo_status(path) for path in find_repos(folder or "")]
            with self.lock:
                self.result = (folder, repos)
            time.sleep(SCAN_MIN_SECONDS)


def next_choice(current, options):
    return options[(options.index(current) + 1) % len(options)] if current in options else options[0]


def cmd_host(args):
    pane_id = args.pane
    lines = queue.Queue()
    typed = {"text": ""}  # 지금 입력 중인 글자 (화면에 바로 보이게 한다)
    reader = read_keys if os.name == "nt" else read_lines
    threading.Thread(target=reader, args=(lines, typed), daemon=True).start()
    folder = load_config().get("folder") or ""
    theme = read_state("theme")
    if theme not in THEMES:
        theme = DEFAULT_THEME
    saved_lang = i18n.normalize(read_state("lang"))  # t, l 키로 고른 값은 환경 설정보다 우선한다
    if saved_lang:
        i18n.set_language(saved_lang)
    help_open = False
    scanner = RepoScanner()
    shown = None
    last_state = None
    tick = 0
    next_refresh = 0.0
    notice = ""
    selected = None
    while True:
        now = time.monotonic()
        if now >= next_refresh:
            scanner.request(folder)
            _, repos = scanner.latest()
            state = agent_state(repos)
            report(pane_id, state, len(repos), state != last_state or tick % LAYOUT_EVERY_TICKS == 0)
            last_state = state
            write_state("heartbeat", str(time.time()))
            tick += 1
            if tick % LAYOUT_EVERY_TICKS == 0:
                keep_at_bottom()
            next_refresh = now + TICK_SECONDS
        _, repos = scanner.latest()
        rows = shutil.get_terminal_size((80, 24)).lines - 1
        screen = build_screen(folder, repos, rows, notice, THEMES[theme], help_open)
        frame = (screen, typed["text"])
        if frame != shown:
            # 같은 자리에 덮어쓴다. 화면을 지우면 터미널 스크롤백에 이전 프레임이 쌓인다.
            # 입력줄은 맨 아래 줄에 둔다. 입력한 글자는 이 줄에 바로 보인다.
            painted = "\n".join(line + ERASE_LINE for line in screen.split("\n"))
            print(CURSOR_HOME + painted + "\n" + ERASE_LINE + PROMPT + typed["text"] + ERASE_BELOW, end="", flush=True)
            shown = frame
        try:
            text = lines.get(timeout=INPUT_POLL_SECONDS)
        except queue.Empty:
            continue
        if text == HELP_TOKEN:
            help_open = not help_open
            shown = None
            continue
        if text == "t":
            theme = next_choice(theme, list(THEMES))
            write_state("theme", theme)
            shown = None
            continue
        if text == "l":
            # 순서: 시스템 설정 → 지원 언어들. 시스템 설정은 저장값을 지우고 환경에서 다시 정한다
            nxt = next_choice(saved_lang or "system", ["system", *i18n.SUPPORTED])
            if nxt == "system":
                remove_state("lang")
                i18n.set_language(i18n.detect())
            else:
                write_state("lang", nxt)
                i18n.set_language(nxt)
            saved_lang = None if nxt == "system" else nxt
            shown = None
            continue
        folder, redraw, notice, selected = handle_input(text, folder, selected)
        if redraw:
            shown = None
            next_refresh = 0.0
    return 0


def pane_alive(pane_id):
    """pane 이 아직 herdr 에 있는지. 닫힌 pane 의 heartbeat 가 몇 초 남아 있어도 블록은 다시 띄워야 한다."""
    if not pane_id:
        return False
    return herdr_api.cli("pane", "get", pane_id, check=False) is not None


def cmd_start(_args):
    if (recently("heartbeat") and pane_alive(read_state("pane.id"))) or recently("starting"):
        return 0
    write_state("starting", str(time.time()))
    _, pane_id = ensure_workspace()
    herdr_api.cli(
        "pane", "run", pane_id,
        sys.executable, "-X", "utf8", os.path.abspath(__file__), "host", "--pane", pane_id,
        "--state", str(state_dir()), "--config", str(config_dir()),
    )
    return 0


def cmd_stop(_args):
    pane_id = read_state("pane.id")
    workspace_id = read_state("workspace.id")
    if pane_id:
        herdr_api.try_request("pane.release_agent", {"pane_id": pane_id, "source": SOURCE, "agent": AGENT_ID})
    if workspace_id:
        # dock 은 다른 plugin 과 같이 쓴다. 자기 pane 만 닫고, 남은 pane 이 없으면 workspace 도 닫는다.
        others = [p for p in workspace_panes(workspace_id) if p["pane_id"] != pane_id and not is_sidebar(p)]
        if others and pane_id:
            herdr_api.cli("pane", "close", pane_id, check=False)
            ensure_intro(workspace_id, None, str(state_dir()))  # 블록이 빠져 생긴 빈 칸에 소개를 띄운다
        else:
            herdr_api.cli("workspace", "close", workspace_id, check=False)
    for name in ("pane.id", "workspace.id", "heartbeat", "starting"):
        remove_state(name)
    dock.release_dock_pane(DOCK_KEY)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="dock.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("start")
    sub.add_parser("stop")
    host = sub.add_parser("host")
    host.add_argument("--pane", required=True)
    # 값은 import 전에 _apply_flags_to_environment 가 읽는다. 여기서는 argparse 가 받기만 한다.
    for flag in ("--state", "--config", "--lang"):
        host.add_argument(flag, default=None)
    args = parser.parse_args(argv)
    handlers = {"start": cmd_start, "stop": cmd_stop, "host": cmd_host}
    try:
        return handlers[args.command](args) or 0
    except (herdr_api.HerdrError, OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0  # Ctrl+C 로 멈춘 것이므로 트레이스백 없이 끝낸다


if __name__ == "__main__":
    sys.exit(main())
