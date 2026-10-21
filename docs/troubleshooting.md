# Troubleshooting

Common problems and where to look.

- **`repo.txt` error:** the file is missing or empty. Create it with the repository path. See [Setup: Configure](setup.md#configure).
- **git failure:** the message says which git command failed and shows git's stderr. Check the repository path and, for `update`, that the upstream is set. See [Setup: Git prerequisites](setup.md#git-prerequisites-for-the-repository).
- **`push` says the branch has no upstream:** the action prints `git push -u origin <branch>` guidance and does not push. Run that command to set the upstream, then retry.
- **`Unknown action: <name>`:** the manifest and `src/index.py` are out of sync. See [Actions: Errors](actions.md#errors).
- **No visible output:** herdr's UI for plugin output is not documented. Read the log instead:

  ```sh
  herdr plugin log list --plugin local.simple-git
  ```

- **`update` fails after the branches diverged:** `update` uses `--ff-only`, so it stops without changing anything. Merge or rebase by hand, then run it again. See [Actions: Behavior notes](actions.md#behavior-notes).
- **`push` says there is nothing to push:** the local branch has no commits ahead of its upstream. This is expected.

## Related

- [Usage](usage.md): overview of the plugin
- [Setup](setup.md): install, configuration files, language, keyboard shortcut
- [Actions](actions.md): what each action runs and prints
- [Dock agent](dock.md): the `N repos` entry in the herdr-dock workspace
