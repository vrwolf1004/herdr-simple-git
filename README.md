# herdr-simple-git

[**English**](README.md) | [한국어](README.ko.md)

Run `git pull`, `git commit`, and `git push` on one repository from inside herdr. No AI. Each action prints a short status line such as "pulled 3 commit(s)" or "pushed 1 commit(s)".

## Requirements

- herdr 0.9.0 or later
- Python 3.10 or later
- Git on `PATH`
- A repository that already exists and has an upstream branch set

## Quick start

1. Install the plugin:

   ```sh
   herdr plugin install vrwolf1004/herdr-simple-git
   ```

2. Create `repo.txt` in the plugin's config folder with the absolute path of the repository to sync. Find the folder with:

   ```sh
   herdr plugin config-dir local.simple-git
   ```

   For example, put this line in `repo.txt`:

   ```
   C:\work\app
   ```

3. Run an action:

   ```sh
   herdr plugin action invoke local.simple-git.all
   ```

## Actions

| Action | What it does |
|--------|--------------|
| `update` | `git pull --ff-only` |
| `commit` | `git add -A`, then `git commit` with `commit-message.txt` or a timestamp message |
| `push` | `git push` |
| `all` | `update`, then `commit`, then `push`. Stops at the first failure |

Action IDs are `local.simple-git.<action>`. Results are printed in English or in your language (see below). Errors go to stderr and exit with code 1.

On Windows, append `-windows` to the dock action ids (`dock-start-windows`, `dock-stop-windows`). On Linux and macOS, use `dock-start` and `dock-stop`.

## Dock agent

| Action | What it does |
|--------|--------------|
| `dock-start` | Adds one `N repos` entry to the `herdr-dock` workspace, listing the git repos under the folder you type in its pane |
| `dock-stop` | Removes the entry and closes its pane (the workspace closes only if nothing else is left in it) |

The entry's state follows the repos: `blocked` if a repo cannot be read, `working` if a repo has uncommitted or unpushed changes, and `idle` when every repo is clean. See [Dock agent](docs/dock.md).

## Language

The messages are available in English, Korean (`ko`), Japanese (`ja`), Russian (`ru`), French (`fr`), Spanish (`es`), and German (`de`). The language is picked in this order:

1. Environment variable `HERDR_SIMPLE_GIT_LANG`
2. `lang` in `config.json` in the config folder, for example `{ "lang": "ko" }`
3. The OS language
4. English

## Documentation

- [Usage](docs/usage.md): overview, install, configuration, actions (Korean: usage.ko.md)
- [Setup](docs/setup.md): install, configuration files, language, keyboard shortcut, troubleshooting
- [Troubleshooting](docs/troubleshooting.md): common problems and checks
- [Actions](docs/actions.md): what each action runs, messages, errors, behavior notes
- [Dock agent](docs/dock.md): one `N repos` entry in the herdr-dock workspace, with the state of each repo under a folder
- [Development](docs/development.md): code layout, translations, testing with scratch repositories
