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
│ Folder: C:\\work\\app                                        │
│ herdr-talk               main           clean               │
│ herdr-timekit            main           1 changed           │
│ herdr-simple-git         main           1 ahead             │
├─────────────────────────────────────────────────────────────┤
│ [folder path] choose folder   [/refresh] update now         │
╰─────────────────────────────────────────────────────────────╯
```

The optional dock agent lists repositories under a folder and shows whether each is clean, has local changes, or has unpushed commits.

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

Append `-windows` to the dock action IDs on Windows. Configure the repository before running Git actions; see the [usage guide](docs/usage.md).

## Requirements

- herdr 0.9.0 or later
- Python 3.10 or later
- Git on `PATH`
- An existing repository with an upstream branch configured

## Documentation

- [Usage (English)](docs/usage.md)
- [사용법 (한국어)](docs/usage.ko.md)
- [Setup](docs/setup.md)
- [Actions](docs/actions.md)
- [Dock agent](docs/dock.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development](docs/development.md)

## Support the project

If this project is useful to you, consider buying the developer a coffee.

[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)
