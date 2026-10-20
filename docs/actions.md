# Actions

`herdr-simple-git` provides four actions. Each one runs a single command against the repository set in `repo.txt` and prints a one-line result. There is no AI and no interactive prompt.

| Action ID | Title | Runs |
| --- | --- | --- |
| `update` | Git update (pull --ff-only) | `git pull --ff-only` |
| `commit` | Git commit all changes | `git add -A` then `git commit -m <message>` |
| `push` | Git push | `git push` |
| `all` | Git update, commit, push | `update`, then `commit`, then `push` |

Full action IDs are `local.simple-git.<action>`, for example `local.simple-git.update`. Invoke one from the command line with:

```sh
herdr plugin action invoke local.simple-git.update
```

## Output

Each action prints one line on success. The text is translated (see [setup](setup.md#language)). The English versions are shown below.

| Action | Result | English message |
| --- | --- | --- |
| `update` | New commits pulled | `update: pulled N commit(s)` |
| `update` | Already up to date | `update: already up to date` |
| `commit` | Changes committed | `commit: committed N file(s) (<message>)` |
| `commit` | Nothing to commit | `commit: nothing to commit` |
| `push` | Commits pushed | `push: pushed N commit(s)` |
| `push` | Nothing to push | `push: nothing to push` |

`all` prints one line per step. It stops at the first failing step, so later steps do not run.

## Errors

Any failure prints a message to stderr and exits with code 1. Common messages (English versions):

- `Write the repository path in <path>\repo.txt`: `repo.txt` is missing. See [setup](setup.md#configure).
- `git <args> failed` followed by git's stderr: a git command failed, for example a pull that cannot fast-forward, or a push with no upstream.
- `Unknown action: <name>`: the plugin was invoked with an action name it does not know. This happens only when the manifest and `src/index.py` are out of sync.

## Behavior notes

- `update` uses `--ff-only`, so it never creates a merge commit. If the local branch has diverged, `update` fails and nothing changes.
- `commit` stages everything with `git add -A`. Files matching `.gitignore` are skipped.
- `commit` and `all` use `commit-message.txt` if it exists. Otherwise the message is `update` followed by the local time.
- `push` checks how many commits are ahead of the upstream before pushing. If there are none, it does nothing.
