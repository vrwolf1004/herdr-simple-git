# herdr-simple-git

[**English**](README.md) | [한국어](README.ko.md)

UI languages: English · Korean · Russian · French · Spanish · German · Japanese

Run `git pull`, `git commit`, and `git push` for a configured repository from inside herdr, without AI.

## Dashboard design

Agents sidebar:

```text
◐ 3 repos
```

Dock pane:

```text
╭─────────────────────────────────────────────────────────────╮
│              🐺  herdr-simple-git  🌕                      │
├─────────────────────────────────────────────────────────────┤
│ Folder: C:\work\app                                          │
│ herdr-talk               main           clean               │
│ herdr-timekit            main           1 changed           │
│ herdr-simple-git         main           1 ahead             │
├─────────────────────────────────────────────────────────────┤
│ [folder path] choose folder   [n] select repo, then [u] update (pull) │
│ [/refresh] update now                                        │
╰─────────────────────────────────────────────────────────────╯
```

The optional dock agent lists repositories directly under a folder and shows local changes and commits ahead of each branch's locally recorded upstream state. It does not fetch. Starting it checks for its existing pane and reuses it when available; otherwise it reuses an empty dock pane or creates one. Repository scans run in the background, and `git status --porcelain=v1 -b -z` is parsed safely for paths that contain spaces, quotes, or newlines.

## Installation

```sh
herdr plugin install vrwolf1004/herdr-simple-git
```

## Actions

| Action | What it does |
| --- | --- |
| `local.simple-git.update` | Run `git pull --ff-only` |
| `local.simple-git.commit` | Stage all changes and commit |
| `local.simple-git.push` | Run `git push` |
| `local.simple-git.all` | Update, commit, then push; stop on the first failure |
| `dock-start` / `dock-stop` | Show or hide the repository dock agent |

Append `-windows` to the dock action IDs on Windows. Configure the repository before running Git actions. The current branch needs an upstream for `update`; see the [usage guide](docs/usage.md).
If `push` finds no upstream, it prints a `git push -u origin <branch>` setup command and does not push.

## Requirements

- herdr 0.9.0 or later
- Python 3.10 or later
- Git on `PATH`
- An existing Git repository; `update` requires an upstream branch

## Documentation

- [Usage (English)](docs/usage.md)
- [사용법 (한국어)](docs/usage.ko.md)
- [Setup](docs/setup.md)
- [Actions](docs/actions.md)
- [Architecture](docs/architecture.md)
- [Dock agent](docs/dock.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development](docs/development.md)
- [TODO](docs/todo.md)

## Support the project

If this project is useful to you, consider buying the developer a coffee.

[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)
