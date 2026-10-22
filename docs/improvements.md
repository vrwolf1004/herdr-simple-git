# 개선 문서

- 작성 기준: 2026-10-22, 커밋 `8924b2d` (`git log -1 --format=%h`)
- 공용 도크 모듈: `src/dock_layout.py` 는 복사본. `load_dock_layout()`(`src/dock.py:30`)이 설치된 herdr-dock-grid 원본을 먼저 찾고, 없으면 이 복사본을 쓴다. 복사본은 herdr-dock-grid 0.7.1 원본과 내용이 같다(diff 확인).
- 할 일 목록: [todo.md](todo.md). 이미 적힌 항목은 옮기지 않고 거기서 관리한다.
- 표기: "확인됨" = 현재 코드에서 직접 본 내용. "확인 필요" = 코드로 추정만 했고 실행해 보지 않음.

## 개선 항목

- **[높음] manifest 가 Linux/macOS 를 선언하지만 주요 액션은 `python` 만 부른다** (확인 필요, Windows 에서만 확인)
  - 근거: `herdr-plugin.toml:8-30` (`update`, `commit`, `push`, `all` 의 `command` 줄 12, 18, 24, 30). 파일 상단 `platforms = ["windows", "linux", "macos"]`.
  - 실행기 이름이 `python` 이라 Linux/macOS 에 `python` 이 없으면 이 네 액션이 실패한다. dock 액션(`:34-62`)만 `platforms` 로 OS 를 나눴다. herdr-timekit 처럼 OS 별 블록(`python3` / `python`)으로 나누는 방식을 따른다.

- **[중간] git 원격 호출에 시간 제한과 stdin 설정이 없음** (확인 필요)
  - 근거: `src/index.py:33-45`(`git()`), `:48`(`pull --ff-only`), `:104`(`push`)
  - `stdin` 을 막지 않아 자격 증명 입력을 기다리며 멈출 수 있다. `dock.py` 의 `repo_status` 는 `GIT_TIMEOUT_SECONDS` 를 쓰므로 같은 방식으로 맞출 수 있다.

- **[낮음] 같은 역할의 git 헬퍼가 두 개** (확인됨)
  - 근거: `src/index.py:33`(`git()`), `:57`(`git_raw()`)
  - 두 함수는 출력의 앞뒤 공백 처리만 다르다. `git()` 이 `git_raw()` 를 쓰도록 줄이면 중복이 줄어든다.

- **[낮음] 저장소에 CI가 없음** (확인됨)
  - 근거: 저장소 루트에 `.github/` 가 없다. herdr-stockpulse 의 `.github/workflows/test.yml` 을 참고할 수 있다.

## 관련 기존 항목 (todo.md)

- 저장소 스캔 진행 표시: [todo.md](todo.md) 의 "실행 확인에서 찾은 개선점" 절
