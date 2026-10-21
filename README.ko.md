# herdr-simple-git

[English](README.md) | [**한국어**](README.ko.md)

지원 언어: 영어 · 한국어 · 러시아어 · 프랑스어 · 스페인어 · 독일어 · 일본어

설정한 저장소에서 `git pull`, `git commit`, `git push`를 herdr 안에서 AI 없이 실행합니다.

## 대시보드 디자인

선택 기능인 dock 에이전트는 폴더 아래의 저장소 목록과 각 저장소가 깨끗한지, 변경사항이나 푸시할 커밋이 있는지 보여 줍니다.

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

Windows에서는 dock 액션 ID 뒤에 `-windows`를 붙입니다. Git 액션 전에 저장소 경로를 설정하세요. 자세한 방법은 [사용법](docs/usage.ko.md)을 참고하세요.

## 요구 사항

- herdr 0.9.0 이상
- Python 3.10 이상
- `PATH`에 Git이 있어야 함
- upstream 브랜치가 설정된 기존 저장소

## 문서

- [사용법 (한국어)](docs/usage.ko.md)
- [Usage (English)](docs/usage.md)
- [설정](docs/setup.md)
- [액션](docs/actions.md)
- [Dock 에이전트](docs/dock.md)
- [문제 해결](docs/troubleshooting.md)
- [개발](docs/development.md)

## 프로젝트 응원하기

프로젝트가 도움이 되셨다면 커피 한 잔으로 개발을 응원해 주세요.

[![Ko-fi에서 응원하기](https://img.shields.io/badge/Ko--fi-%EC%9D%91%EC%9B%90%ED%95%98%EA%B8%B0-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)
