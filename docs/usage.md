# Usage

How to install and set up herdr-simple-git, what each action does, and where to find the details. The details live in the linked pages, so this page is the starting point.

## 1. Install

```sh
herdr plugin install vrwolf1004/herdr-simple-git
```

For a local clone, link the folder instead. Requirements: herdr 0.9.0 or later, Python 3.10 or later, Git on `PATH`. Full steps are in [Setup](setup.md#install).

## 2. Configure the repository

Create `repo.txt` in the plugin's config folder with the absolute path of the repository to sync. Optionally add `commit-message.txt` (the commit message) and `config.json` (`"lang"`). The folder is shown by:

```sh
herdr plugin config-dir local.simple-git
```

The repository must already exist. `update` needs an upstream branch; `commit` does not. If `push` has no upstream, it prints setup guidance and does not push. Details are in [Setup: Configure](setup.md#configure) and [Setup: Git prerequisites](setup.md#git-prerequisites-for-the-repository).

## 3. Actions

| Action ID | What it runs |
| --- | --- |
| `local.simple-git.update` | `git pull --ff-only` |
| `local.simple-git.commit` | `git add -A`, then `git commit -m <message>` |
| `local.simple-git.push` | `git push` |
| `local.simple-git.all` | `update`, then `commit`, then `push`. Stops at the first failing step |

Invoke one from the command line:

```sh
herdr plugin action invoke update --plugin local.simple-git
```

Each action prints one short line, for example `update: pulled 3 commit(s)`. The full list of messages and errors is in [Actions](actions.md).

A keyboard shortcut for an action is shown in [Setup: Optional: keyboard shortcut](setup.md#optional-keyboard-shortcut).

## 4. Dock agent

The plugin also adds one `N repos` entry to the `herdr-dock` workspace. It lists the git repositories under a folder and shows the state of each one. Starting checks for and reuses the plugin's existing pane when possible; repository scans run in the background. See [Dock agent](dock.md) for pane selection and status parsing details.

## 5. Language

Messages follow `HERDR_SIMPLE_GIT_LANG`, then `lang` in `config.json`, then the OS language, then English. Supported: `en`, `ko`, `ja`, `ru`, `fr`, `es`, `de`. See [Setup: Language](setup.md#language).

## 6. Troubleshooting

Common problems and checks are in [Troubleshooting](troubleshooting.md).

## Documentation

- [Usage (한국어)](usage.ko.md)
- [Setup](setup.md): install, configuration files, language, keyboard shortcut
- [Actions](actions.md): what each action runs, messages, errors, behavior notes
- [Dock agent](dock.md): one `N repos` entry in the herdr-dock workspace
- [Troubleshooting](troubleshooting.md): common problems and checks
- [Development](development.md): code layout, translations, testing with scratch repositories
