# Dock agent

The dock agent shows how many git repos are in a folder, in herdr's agents panel. It lives in the shared `herdr-dock` workspace, next to other plugins such as herdr-timekit.

## What you see

- **Agents panel:** one entry named `N repos`. Its state follows the repos:
  - `blocked`: a repo cannot be read (for example, a broken `.git`)
  - `working`: a repo has uncommitted changes or unpushed commits
  - `idle`: every repo is clean and up to date with its upstream
- **Focus the entry** (click it in the agents panel): the pane shows each repo with its branch and state.

```
Git 저장소

폴더: C:\work\app
  herdr-talk               main           변경 없음
  herdr-timekit            main           변경 1개
  herdr-simple-git         main           push 전 1개

폴더 경로를 입력하고 Enter를 누르세요. /refresh 는 바로 갱신합니다.
```

## Choose the folder

Type the folder path in the pane and press Enter. The path is saved to `config.json` in the plugin's config folder, so the next start remembers it.

- Only git repos **directly** under the folder are listed. Subfolders of those repos are not scanned.
- `/refresh` redraws the list now. The list also refreshes every 5 seconds.

## Start and stop

```sh
herdr plugin action invoke local.simple-git.dock-start-windows   # Windows
herdr plugin action invoke local.simple-git.dock-start           # Linux, macOS
herdr plugin action invoke local.simple-git.dock-stop-windows    # Windows
herdr plugin action invoke local.simple-git.dock-stop            # Linux, macOS
```

- `dock-start` creates the `herdr-dock` workspace if it does not exist. It reuses an empty pane there, or splits a new one.
- `dock-stop` releases the agent and closes its pane. The workspace is closed only if nothing else is left in it.
- Starting twice is safe. A running host is detected through its heartbeat.

## How it works

- The host loop runs inside the dock pane. Closing the pane stops it.
- Each refresh runs `git status --porcelain=v1 -b` for every repo. No fetch and no network, so `ahead` shows only commits you have not pushed yet, based on the last fetch.
- Every third refresh, the workspace is moved to the bottom of the list, as herdr-timekit does.
- The host reads the state, config, and language paths from `start`, because the pane does not get the `HERDR_PLUGIN_*` variables.

## Limits

- Repos are found by looking one level down. A repo nested deeper is not listed.
- The agent count is the number of repos found, so a repo that disappears from the folder drops out on the next refresh.
- `behind` (commits on the remote you have not pulled) is not shown, because it needs a fetch.

## Files

- `src/dock.py`: dock host and commands (`start`, `stop`, `host`)
- `src/herdr_api.py`: herdr CLI and socket helper, copied from herdr-timekit (plugins do not share modules)
- `src/locales/*.json`: `dock.*` messages, same languages as the rest of the plugin
