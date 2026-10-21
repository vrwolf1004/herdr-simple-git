# herdr-simple-git

[English](README.md) | [**한국어**](README.ko.md)

지원 언어: 영어 · 한국어 · 러시아어 · 프랑스어 · 스페인어 · 독일어 · 일본어

설정한 저장소에서 `git pull`, `git commit`, `git push`를 herdr 안에서 AI 없이 실행합니다.

## 대시보드 디자인

Agents 사이드바:

```text
◐ 3 repos
```

Dock pane:

```text
╭─────────────────────────────────────────────────────────────╮
│              🐺  herdr-simple-git  🌕                      │
├─────────────────────────────────────────────────────────────┤
│ 폴더: C:\work\app                                             │
│ herdr-talk               main           변경 없음           │
│ herdr-timekit            main           변경 1개            │
│ herdr-simple-git         main           push 전 1개          │
├─────────────────────────────────────────────────────────────┤
│ [폴더 경로] 폴더 선택   [/refresh] 지금 갱신                │
╰─────────────────────────────────────────────────────────────╯
```

선택 기능인 dock 에이전트는 지정한 폴더 바로 아래의 저장소와 로컬 변경사항, 로컬에 기록된 upstream보다 앞선 커밋을 보여 줍니다. 원격에서 fetch하지는 않습니다.
Dock을 시작할 때 기존 pane을 확인해 재사용하고, 사용할 수 없으면 빈 pane을 고르거나 새 pane을 만듭니다. 저장소 스캔은 백그라운드에서 수행하며 `git status --porcelain=v1 -b -z`를 파싱해 공백·따옴표·줄바꿈이 든 경로도 처리합니다.

## 설치

```sh
herdr plugin install vrwolf1004/herdr-simple-git
```

## 액션

| 액션 | 기능 |
| --- | --- |
| `local.simple-git.update` | `git pull --ff-only` 실행 |
| `local.simple-git.commit` | 변경사항을 모두 스테이징하고 커밋 |
| `local.simple-git.push` | `git push` 실행 |
| `local.simple-git.all` | 업데이트, 커밋, 푸시를 순서대로 실행하고 실패 시 중단 |
| `dock-start` / `dock-stop` | 저장소 dock 에이전트 표시 또는 숨기기 |

Windows에서는 dock 액션 ID 뒤에 `-windows`를 붙입니다. Git 액션 전에 저장소 경로를 설정하세요. `update`에는 현재 브랜치의 upstream이 필요합니다. 자세한 방법은 [사용법](docs/usage.ko.md)을 참고하세요.
`push` 대상 브랜치에 upstream이 없으면 `git push -u origin <branch>` 설정 명령을 안내하고 push하지 않습니다.

## 요구 사항

- herdr 0.9.0 이상
- Python 3.10 이상
- `PATH`에 Git이 있어야 함
- 기존 Git 저장소 (`update`에는 upstream 브랜치 필요)

## 문서

- [사용법 (한국어)](docs/usage.ko.md)
- [Usage (English)](docs/usage.md)
- [설정](docs/setup.md)
- [액션](docs/actions.md)
- [구조](docs/architecture.md)
- [Dock 에이전트](docs/dock.md)
- [문제 해결](docs/troubleshooting.md)
- [개발](docs/development.md)
- [할 일](docs/todo.md)

## 프로젝트 응원하기

프로젝트가 도움이 되셨다면 커피 한 잔으로 개발을 응원해 주세요.

[![Ko-fi에서 응원하기](https://img.shields.io/badge/Ko--fi-%EC%9D%91%EC%9B%90%ED%95%98%EA%B8%B0-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)
