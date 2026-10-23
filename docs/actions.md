# Actions

`herdr-simple-git` provides four repository actions. `update`, `commit`, and `push` run the corresponding Git operation against the repository set in `repo.txt`; `all` runs those three actions in order. Actions do not use AI or ask interactive questions.

| Action ID | Title | Runs |
| --- | --- | --- |
| `update` | Git update (pull --ff-only) | `git pull --ff-only` |
| `commit` | Git commit all changes | `git add -A` then `git commit -m <message>` |
| `push` | Git push | `git push` |
| `all` | Git update, commit, push | `update`, then `commit`, then `push` |

Full action IDs are `local.simple-git.<action>`, for example `local.simple-git.update`. Invoke one from the command line with:

```sh
herdr plugin action invoke update --plugin local.simple-git
```

## Output

Each action prints one line on success. The text is translated (see [setup](setup.md#language)). The English versions are shown below.

| Action | Result | English message |
| --- | --- | --- |
| `update` | New commits pulled | `update (pull): pulled N commit(s)` |
| `update` | Already up to date | `update (pull): already up to date` |
| `commit` | Changes committed | `commit: committed N file(s) (<message>)` |
| `commit` | Nothing to commit | `commit: nothing to commit` |
| `push` | Commits pushed | `push: pushed N commit(s)` |
| `push` | Nothing to push | `push: nothing to push` |

`all` prints one line per step. It stops at the first failing step, so later steps do not run.

## Errors

Git command failures print a message to stderr and exit with code 1. Common messages (English versions):

- `Write the repository path in <path>\repo.txt`: `repo.txt` is missing. See [setup](setup.md#configure).
- `git <args> failed` followed by git's stderr: a git command failed, for example a pull that cannot fast-forward.
- `Unknown action: <name>`: the plugin was invoked with an action name it does not know. This happens only when the manifest and `src/index.py` are out of sync.

`push` prints guidance and returns without pushing when the branch has no upstream or is detached; these cases are not reported as Git command failures.

## Behavior notes

- `update` uses `--ff-only`, so it never creates a merge commit. If the local branch has diverged, `update` fails and nothing changes.
- `update` checks for an upstream first. If there is none, it does not pull and prints the `git push -u origin <branch>` command instead.
- `update` also checks for commits. If the repository has no commits yet, it does not pull and asks you to make a commit first.
- `commit` stages everything with `git add -A`. Files matching `.gitignore` are skipped.
- `commit` shows the list of files before committing. If a file name looks sensitive, it prints a warning. The commit is not blocked.
- `commit` and `all` use `commit-message.txt` if it exists. Otherwise the message is `update` followed by the local time.
- `push` checks how many commits are ahead of the upstream before pushing. If there are none, it does nothing.
- A branch without an upstream prints the `git push -u origin <branch>` command to set one. A detached `HEAD` has no branch to push.
