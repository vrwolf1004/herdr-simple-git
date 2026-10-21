# Architecture

`herdr-plugin.toml` registers the repository actions and the dock start/stop actions. `src/index.py` runs the Git actions against the repository configured in `repo.txt`; the push path checks whether the current branch has an upstream and prints setup guidance instead of pushing if it does not.

The optional dock host in `src/dock.py` runs in a pane in the shared `herdr-dock` workspace. Start checks whether its saved pane is still present, then reuses it; if it is gone, the host selects an empty pane or splits an existing pane. The host reports repository count and status to herdr while a background `RepoScanner` discovers repositories and checks their status, so scanning does not block pane input.

Repository status is collected with `git status --porcelain=v1 -b -z`. `src/gitstatus.py` parses the branch header and NUL-delimited changes; for rename and copy records it skips the separate old-path token. The dock does not fetch, so ahead counts reflect the upstream information recorded locally by Git, not a live remote check.

See [Dock agent](dock.md) for pane behavior, limits, and display details, and [Development](development.md) for the source layout and test commands.
