# Dock agent

The dock agent shows how many git repos are in a folder, in herdr's agents panel. It lives in the shared `herdr-dock` workspace, next to other plugins such as herdr-timekit.

## What you see

- **Agents panel:** one entry named `N repos`. Its state follows the repos:
  - `blocked`: a repo cannot be read (for example, a broken `.git`)
  - `working`: a repo has uncommitted changes or unpushed commits
  - `idle`: every repo is clean and up to date with its upstream
- **Focus the entry** (click it in the agents panel): the pane shows each repo with its branch and state.

The pane is a boxed panel titled `🐺  herdr-simple-git  🌕`. It shows the folder, then one line per repo with its branch and state, and an input help line at the bottom. Type your input on the line below the box. Korean example of the repo lines:

```
폴더: C:\work\app
  herdr-talk               main           변경 없음
  herdr-timekit            main           변경 1개
  herdr-simple-git         main           push 전 1개
```

The bottom help line reads `[folder path] choose folder   [/refresh] update now` in English, and the same keys are translated in the other languages.

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

- `dock-start` creates the `herdr-dock` workspace if it does not exist. It reuses an empty pane there. Otherwise it splits the dock into a 2×2 grid and takes the next free corner (top-left, top-right, bottom-left, bottom-right), the same rule as herdr-ai-feedbag and herdr-radio.
- `dock-stop` releases the agent and closes its pane. The workspace is closed only if nothing else is left in it.
- Pressing Ctrl+C in the dock pane stops the host cleanly without a traceback, but leaves the pane open at its shell prompt. Use `dock-stop` to release the agent and close the pane.
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
- If the pane is shorter than the list, the last repos are hidden so the input line stays at the bottom. Enlarge the pane to see them.

## Files

- `src/dock.py`: dock host and commands (`start`, `stop`, `host`)
- `src/herdr_api.py`: herdr CLI and socket helper, copied from herdr-timekit (plugins do not share modules)
- `src/locales/*.json`: `dock.*` messages, same languages as the rest of the plugin
