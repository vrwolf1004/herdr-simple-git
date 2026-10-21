# Development

## Layout

```
herdr-simple-git/
  herdr-plugin.toml   plugin manifest: id, version, and action commands
  src/index.py        update, commit, push, and all action implementation
  src/gitstatus.py    porcelain status and branch parsing, shared by actions and dock
  src/dock.py         optional repository dock agent and background scanner
  src/herdr_api.py    herdr CLI and socket helpers
  src/intro.py        shared dock introduction pane
  src/i18n.py         language detection and t() for translated messages
  src/locales/        one <language>.json per supported language
  tests/              unittest coverage for status/branch parsing, repository actions, and scanning
  docs/               documentation
  README.md           English README
  README.ko.md        Korean README
```

`herdr-plugin.toml` maps each action to `python -X utf8 src/index.py <action>`. The script takes the action name as its only argument. `-X utf8` makes Korean and other non-ASCII output work on Windows consoles.

## Dock and status parsing

The dock host is started in a pane by `src/dock.py start`. It checks whether the saved pane still exists and reuses it; otherwise it selects an empty pane or creates one by splitting an existing pane. `RepoScanner` performs repository discovery and status reads on a daemon background thread, leaving the pane's input loop responsive. Each repository status comes from `git status --porcelain=v1 -b -z`; `src/gitstatus.py` parses the branch header and NUL-delimited status entries, including rename/copy records. The push action checks for an upstream before pushing and prints the `git push -u origin <branch>` command when one is missing.

## Translations

All user-facing text is in `src/locales/<language>.json`. Code calls `t('key', { name: value })`, and `{name}` in the text is replaced with the value.

To add a language:

1. Add its code to `SUPPORTED` in `src/i18n.py`.
2. Create `src/locales/<code>.json` with the same keys as `en.json`.
3. Add the code to the language list in `docs/setup.md` and both READMEs.

Every locale file must have the same keys. A missing key falls back to English, so a missing key does not crash the plugin, but it is still a bug.

## Run an action locally

Link the folder, then invoke an action through herdr:

```sh
herdr plugin link "C:\path\to\herdr-simple-git"
herdr plugin action invoke update --plugin local.simple-git
```

Re-link after changing `herdr-plugin.toml`, because herdr reads the manifest when the plugin is linked:

```sh
herdr plugin unlink local.simple-git
herdr plugin link "C:\path\to\herdr-simple-git"
```

## Run the tests

From the plugin folder:

```sh
python -m unittest discover -s tests
```

## Run the script without herdr

`src/index.py` reads its settings from `HERDR_PLUGIN_CONFIG_DIR`. Point it at a temporary config folder, then run it directly:

```sh
export HERDR_PLUGIN_CONFIG_DIR=/tmp/gs-cfg
mkdir -p "$HERDR_PLUGIN_CONFIG_DIR"
echo "/path/to/test/repo" > "$HERDR_PLUGIN_CONFIG_DIR/repo.txt"
python -X utf8 src/index.py update
```

## Test with scratch repositories

Do not test against a real working repository. Create a bare remote and two clones:

```sh
git init --bare remote.git
git clone remote.git work
git clone remote.git other
```

Make an initial commit in `work`, push it to `origin main`, then make a commit in `other` and push that. This gives `work` one remote commit to pull. Run the actions in this order to cover each path:

1. `update`: pulls one commit.
2. `update`: reports already up to date.
3. `commit`: nothing to commit.
4. Change a file, then `commit`.
5. `push`: pushes one commit.
6. `push`: nothing to push.
7. `all`: nothing to do.
8. Point `repo.txt` at a missing path: expect exit code 1.
9. Delete `repo.txt`: expect exit code 1 and the setup message.

## Conventions

- Keep the plugin dependency-free. It should only need Python 3.10 or later and git.
- Each action prints one line on success and exits with code 1 on failure.
- Put every user-facing string in the locale files. Do not hard-code text in `src/index.py`.
- Add a new action by adding a `[[actions]]` block in the manifest and a `case` in the `match` statement in `main()` in `src/index.py`. Keep the two in sync, and update [actions.md](actions.md).
