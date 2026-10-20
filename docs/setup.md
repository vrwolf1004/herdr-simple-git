# Setup

This guide covers installing `herdr-simple-git` and configuring the repository it syncs.

## Requirements

- [herdr](https://herdr.dev) 0.9.0 or later
- Python 3.10 or later (the plugin runs `python -X utf8 src/index.py`)
- Git on `PATH`

## Install

Link the plugin folder into herdr from a local clone:

```sh
herdr plugin link "C:\path\to\herdr-simple-git"
```

Confirm the actions are registered:

```sh
herdr plugin action list --plugin local.simple-git
```

To remove the link later (this does not delete any files):

```sh
herdr plugin unlink local.simple-git
```

## Configure

The plugin reads its settings from herdr's per-plugin config directory. Find the path with:

```sh
herdr plugin config-dir local.simple-git
```

On Windows this is usually:

```
C:\Users\<you>\AppData\Roaming\herdr\plugins\config\local.simple-git
```

Create these files in that folder:

| File | Required | Contents |
| --- | --- | --- |
| `repo.txt` | Yes | Absolute path of the repository to sync, for example `C:\work\app` |
| `commit-message.txt` | No | Commit message used by `commit` and `all`. If missing, the message is `update <local time>` |
| `config.json` | No | Plugin settings. Currently only `"lang"`, see [Language](#language) |

Example `repo.txt`:

```
C:\work\app
```

The repository must already exist and be initialized with `git init` (or cloned). The plugin does not create repositories.

## Language

Messages are shown in one of these languages: `en`, `ko`, `ja`, `ru`, `fr`, `es`, `de`. The language is chosen in this order, and the first match wins:

1. Environment variable `HERDR_SIMPLE_GIT_LANG`, for example `ko`
2. `lang` in `config.json`, for example `{ "lang": "ko" }`
3. The OS language
4. `en`

A message missing in the chosen language falls back to English.

## Git prerequisites for the repository

- `update` uses `git pull --ff-only`, so the current branch needs an upstream branch set.
- `push` uses `git push` and needs an upstream as well. Set one once with `git push -u origin <branch>`.
- `commit` runs `git add -A`, so untracked files are staged unless they match `.gitignore`. Check `.gitignore` before using `commit` on a new repository.

## Optional: keyboard shortcut

Bind an action to a key in `~/.config/herdr/config.toml`:

```toml
[[keys.command]]
key = "prefix+g"
type = "plugin_action"
command = "local.simple-git.all"
description = "git update, commit, push"
```

Then reload the configuration with `herdr server reload-config`. Pick a key that the built-in keymap does not use.

## Troubleshooting

Common problems and checks are in [troubleshooting.md](troubleshooting.md).
