# herdr-simple-git

[English](README.md) | [**한국어**](README.ko.md)

herdr 안에서 저장소 하나에 대해 `git pull`, `git commit`, `git push`를 실행합니다. AI는 쓰지 않습니다. 각 action은 "3개 커밋 받음", "1개 커밋 푸시"처럼 짧은 결과 한 줄을 보여 줍니다.

## 요구 사항

- herdr 0.9.0 이상
- Python 3.10 이상
- `PATH`에 있는 Git
- 이미 있는 저장소, upstream 브랜치가 설정되어 있어야 합니다

## 빠른 시작

1. 플러그인을 설치합니다:

   ```sh
   herdr plugin install vrwolf1004/herdr-simple-git
   ```

2. 플러그인 설정 폴더에 `repo.txt`를 만들고, 동기화할 저장소의 절대 경로를 적습니다. 폴더 위치는 다음 명령으로 확인합니다:

   ```sh
   herdr plugin config-dir local.simple-git
   ```

   예를 들어 `repo.txt`에 이렇게 적습니다:

   ```
   C:\work\app
   ```

3. action을 실행합니다:

   ```sh
   herdr plugin action invoke local.simple-git.all
   ```

## Action

| Action | 하는 일 |
|--------|---------|
| `update` | `git pull --ff-only` |
| `commit` | `git add -A` 후 `commit-message.txt` 또는 시각 기반 메시지로 커밋 |
| `push` | `git push` |
| `all` | `update`, `commit`, `push`를 순서대로 실행. 실패하면 거기서 멈춤 |

action ID는 `local.simple-git.<action>`입니다. 결과 메시지는 아래 설정에 따라 한국어 또는 영어 등으로 나옵니다. 오류는 stderr로 출력되고 종료 코드는 1입니다.

Windows에서 dock 액션 id 뒤에는 `-windows`를 붙입니다. 예를 들어 Windows에서 dock 시작은 `dock-start-windows`입니다.

## Dock 에이전트

| Action | 하는 일 |
|--------|---------|
| `dock-start` | `herdr-dock` workspace에 `N repos` 항목 하나를 추가합니다. pane에 입력한 폴더 아래의 git 저장소 목록을 보여 줍니다 |
| `dock-stop` | 항목을 빼고 pane을 닫습니다 (다른 것이 남아 있지 않을 때만 workspace를 닫습니다) |

항목 상태는 저장소를 따릅니다. 저장소를 읽을 수 없으면 `blocked`, 커밋하지 않았거나 푸시하지 않은 변경이 있으면 `working`, 모두 깨끗하면 `idle`입니다. [Dock 에이전트](docs/dock.md)를 보세요.

## 언어

메시지는 영어, 한국어(`ko`), 일본어(`ja`), 러시아어(`ru`), 프랑스어(`fr`), 스페인어(`es`), 독일어(`de`)를 지원합니다. 언어는 다음 순서로 정해지고, 먼저 찾은 값을 씁니다:

1. 환경변수 `HERDR_SIMPLE_GIT_LANG`
2. 설정 폴더의 `config.json`에 있는 `lang`, 예: `{ "lang": "ko" }`
3. OS 언어
4. 영어

## 문서

- [사용법](docs/usage.ko.md): 개요, 설치, 설정, 액션 (영문: usage.md)
- [설정](docs/setup.md): 설치, 설정 파일, 언어, 단축키, 문제 해결 (영문)
- [문제 해결](docs/troubleshooting.md): 자주 겪는 문제와 확인 방법 (영문)
- [Action](docs/actions.md): 각 action이 하는 일, 메시지, 오류, 동작 참고 (영문)
- [Dock agent](docs/dock.md): herdr-dock 워크스페이스에 `N repos` 항목 하나, 폴더 아래 각 repo의 상태 (영문)
- [개발](docs/development.md): 코드 구조, 번역 추가, 임시 저장소로 테스트 (영문)
