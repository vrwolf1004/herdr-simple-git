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

## 개선 제안 (2026-10-23)

### 1. 커밋 전에 들어갈 파일 목록을 보여 주지 않음

- **현상**: `commit` 은 확인 없이 `git add -A` 를 실행하고(`src/index.py:77`), 커밋 뒤에 파일 수만 출력한다(`src/index.py:79`). 어떤 파일이 들어갔는지 기록이 남지 않는다. `.gitignore` 에 없는 `.env` 나 임시 파일도 그대로 커밋된다.
- **개선안**: 출력에 스테이징 목록을 넣는다. `.env`, `*.pem` 같은 이름이 보이면 경고하고 커밋을 멈추는 방식을 검토한다. 기본 동작을 바꿀지는 정해야 한다(확인 필요).
- **범위**: `src/index.py` (`commit`), `src/locales/*.json`, `docs/actions.md`, `docs/usage.md`, `docs/usage.ko.md`
- **확인**: `.env` 를 넣은 저장소에서 `commit` 을 실행해 경고와 목록이 나오는지 본다.
→ 완료: 커밋 전에 파일 목록을 보여 주고, 민감해 보이는 파일 이름이 있으면 경고한다 (커밋은 막지 않는다).

### 2. upstream 이 없을 때 `update` 가 안내 없이 git 오류를 냄

- **현상**: `update` 는 upstream 을 확인하지 않고 `git pull --ff-only` 를 실행한다(`src/index.py:46-52`). upstream 이 없으면 git 의 영문 stderr 만 나온다. 같은 상황의 `push` 는 `git push -u origin <branch>` 안내를 준다(`src/index.py:82-99`, 키 `push.no_upstream`).
- **개선안**: `update` 도 `has_upstream` 을 먼저 확인하고, `push` 와 같은 형식의 안내 문구를 낸다.
- **범위**: `src/index.py` (`update`), `src/locales/*.json`, `docs/actions.md`
- **확인**: upstream 이 없는 브랜치에서 `update` 를 실행해 안내 문구가 나오는지 본다.
→ 완료: pull 전에 upstream 과 detached HEAD 를 확인하고, 없으면 pull 하지 않고 안내만 낸다.

### 3. 커밋이 하나도 없는 저장소에서 `update` 가 실패할 수 있음 (확인 필요)

- **현상**: `update` 는 pull 전후에 `git rev-parse HEAD` 를 실행한다(`src/index.py:47`, `:49`). 커밋이 없는 새 저장소에서는 HEAD 가 없어 이 호출이 실패할 것으로 보인다. git 동작에 근거한 추정이며 실행하지 않았다.
- **개선안**: 커밋이 없으면 pull 을 건너뛰고 안내한다.
- **범위**: `src/index.py` (`update`)
- **확인**: 빈 저장소(`git init` 만 한 상태)에서 `update` 를 실행해 실제 오류 문구를 본다.
→ 완료: 커밋이 없으면 pull 하지 않고 먼저 커밋하라는 안내 한 줄을 낸다.
