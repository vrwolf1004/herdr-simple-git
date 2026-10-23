# 사용법

herdr-simple-git을 설치하고 설정하는 방법, 각 액션이 하는 일, 세부 내용을 찾을 곳을 설명합니다. 세부 내용은 연결된 문서에 있으니, 이 문서는 시작점으로 보세요.

## 1. 설치

```sh
herdr plugin install vrwolf1004/herdr-simple-git
```

로컬 clone으로 쓰려면 폴더를 연결하세요. 요구 사항: herdr 0.9.0 이상, Python 3.10 이상, `PATH`에 있는 Git. 자세한 절차는 [설정: 설치](setup.md#install)에 있습니다.

## 2. 저장소 설정

플러그인 설정 폴더에 `repo.txt`를 만들고 동기화할 저장소의 절대 경로를 씁니다. 필요하면 `commit-message.txt`(커밋 메시지)와 `config.json`(`"lang"`)도 만듭니다. 설정 폴더 위치는 다음 명령으로 확인합니다.

```sh
herdr plugin config-dir local.simple-git
```

저장소는 이미 있어야 합니다. `update`에는 upstream 브랜치가 필요하지만 `commit`에는 필요하지 않습니다. `update`에 upstream이 없으면 pull하지 않고 `git push -u origin <브랜치>` 명령을 안내합니다. 커밋이 하나도 없으면 pull하지 않고 먼저 커밋하라고 안내합니다. `push`에 upstream이 없으면 설정 방법을 출력하고 push하지 않습니다. 자세한 내용은 [설정: 설정 파일](setup.md#configure)과 [설정: Git 준비 사항](setup.md#git-prerequisites-for-the-repository)에 있습니다.

## 3. 액션

| 액션 id | 실행하는 명령 |
| --- | --- |
| `local.simple-git.update` | `git pull --ff-only` |
| `local.simple-git.commit` | `git add -A` 후 `git commit -m <메시지>` |
| `local.simple-git.push` | `git push` |
| `local.simple-git.all` | `update`, `commit`, `push`를 차례로 실행. 실패한 단계에서 멈춤 |

명령줄에서 실행하려면:

```sh
herdr plugin action invoke update --plugin local.simple-git
```

각 액션은 한 줄의 짧은 결과를 보여 줍니다. 예: `업데이트(pull): 3개 커밋 받음` (영문 메시지는 `update (pull): pulled 3 commit(s)`). 메시지와 오류 전체 목록은 [액션](actions.md)에 있습니다.

`commit`은 커밋 전에 목록을 보여 줍니다. 민감해 보이는 파일 이름은 경고합니다. 커밋은 막지 않습니다.

액션에 단축키를 연결하는 방법은 [설정: 단축키](setup.md#optional-keyboard-shortcut)에 있습니다.

## 4. Dock 에이전트

플러그인은 `herdr-dock` workspace에 `N repos` 항목도 하나 추가합니다. 폴더 아래의 git 저장소 목록과 각 저장소의 상태를 보여 줍니다. 시작 시 기존 pane을 확인해 재사용하고 저장소 스캔은 백그라운드에서 실행합니다. pane 선택과 상태 파싱은 [Dock 에이전트](dock.md)를 보세요.

## 5. 언어

메시지 언어는 `HERDR_SIMPLE_GIT_LANG` 환경 변수, `config.json`의 `lang`, OS 언어, 영어 순서로 정해집니다. 지원 언어: `en`, `ko`, `ja`, `ru`, `fr`, `es`, `de`. [설정: 언어](setup.md#language)를 보세요.

## 6. 문제 해결

자주 겪는 문제와 확인 방법은 [문제 해결](troubleshooting.md)에 있습니다.

## 문서

- [Usage (English)](usage.md)
- [설정](setup.md): 설치, 설정 파일, 언어, 단축키 (영문)
- [액션](actions.md): 각 액션이 하는 일, 메시지, 오류, 동작 참고 (영문)
- [Dock 에이전트](dock.md): herdr-dock 워크스페이스의 `N repos` 항목 (영문)
- [문제 해결](troubleshooting.md): 자주 겪는 문제와 확인 방법 (영문)
- [개발](development.md): 코드 구조, 번역 추가, 임시 저장소로 테스트 (영문)
