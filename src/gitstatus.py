"""git status 출력 파싱. index.py 와 dock.py 가 같이 쓴다.

- porcelain v1 을 `-z` 로 받아 경로에 줄바꿈이나 따옴표가 있어도 안전하게 나눈다.
  rename/copy 항목은 `XY new\\0old\\0` 형식이라 뒤의 원래 경로를 건너뛴다.
- branch 헤더(`## ...`)는 detached HEAD, 아직 커밋 없는 저장소, upstream 표기를 구분한다.
"""

import re

RENAME_OR_COPY = ("R", "C")


def parse_status_z(output):
    """`git status --porcelain=v1 -z` 출력 → [(XY, 경로)]. 헤더(## 로 시작하는 항목)는 뺀다."""
    entries = []
    tokens = output.split("\0")
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if len(token) < 4 or token.startswith("## "):
            continue
        code, path = token[:2], token[3:]
        entries.append((code, path))
        if code[0] in RENAME_OR_COPY or code[1] in RENAME_OR_COPY:
            index += 1  # 원래 경로는 다음 토큰이므로 건너뛴다
    return entries


def parse_branch(header):
    """`## ...` 헤더 한 줄에서 브랜치 이름만 꺼낸다.

    - `## main...origin/main [ahead 1]` → main
    - `## No commits yet on main` → main
    - `## HEAD (no branch)` → HEAD (detached)
    - `## feature/x` → feature/x
    """
    text = header[3:] if header.startswith("## ") else header
    if text.startswith("No commits yet on "):
        return text[len("No commits yet on "):].strip()
    if text.startswith("HEAD (no branch)"):
        return "HEAD"
    name = re.split(r"\.\.\.| \[", text, maxsplit=1)[0]
    return name.strip()


def ahead_count(header):
    match = re.search(r"ahead (\d+)", header)
    return int(match.group(1)) if match else 0


def behind_count(header):
    match = re.search(r"behind (\d+)", header)
    return int(match.group(1)) if match else 0
