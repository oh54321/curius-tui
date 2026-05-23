# curius

A Textual-powered terminal UI for navigating the [Curius](https://curius.app) social knowledge graph — jump between users, browse their saved links, walk a merged feed of everyone they follow, and open anything in your browser without leaving the terminal.

[![CI](https://github.com/oh54321/curius-tui/actions/workflows/ci.yml/badge.svg)](https://github.com/oh54321/curius-tui/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Why

Curius is a great place to follow what people you respect are reading, but the web UI puts you one tab away from a doom-scroll. This CLI keeps you in a tight, keyboard-driven loop:

- **Pick a user.** See their links, who they follow, and a chronological feed of everything in their network.
- **Walk the graph.** Following → user → their links → open in browser. Back out, jump sideways, dive in.
- **Stay focused.** No images, no infinite scroll. Just titles, ordered by recency, paginated 30 at a time.

Under the hood, the merged-feed view uses an [order-statistic red-black tree](src/data_structures/order_statistic_red_black_tree.py) so that even when you're browsing the combined feed of dozens of users, pagination stays O(log n) and only fetches the pages it needs to fill the next screen.

## Install

Requires Python 3.10+.

```bash
git clone https://github.com/oh54321/curius-tui.git
cd curius-enhanced
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quickstart

```bash
# By argument
curius alice

# By environment variable
export CURIUS_START_USER_LINK=alice
curius

# Or it will prompt you
curius
```

`alice` here is the user's Curius handle (the `userLink` slug, the part of the URL after `curius.app/`).

### Authentication

Most of the Curius API works unauthenticated for public profiles, but some endpoints (network info, certain links) want a JWT. Provide one of:

- **Environment variable:** `export CURIUS_JWT=eyJhbGciOi...`
- **File:** put the token in `~/.credentials/curius_jwt` (one line, no quotes).
- **Custom path:** `export CURIUS_JWT_PATH=/path/to/token`

To get a JWT, sign in at [curius.app](https://curius.app) and grab the `Bearer` token from the `Authorization` header of any authenticated request in your browser's DevTools.

## Usage

The UI is a single keyboard-driven list. Each pane shows a title and a list of items; selecting an item either drills in (another pane) or fires an action (open a link in your browser).

| Key            | Action                          |
| -------------- | ------------------------------- |
| `↑` / `↓`      | Move selection                  |
| `Enter`        | Open / drill in                 |
| `Back` (entry) | Return to the previous pane     |
| `Ctrl+C`       | Quit                            |

Starting from a user, you'll see:

- **Links** — that user's own saved links, newest first.
- **Following** — the users they follow; pick one to dive into their world.
- **Feed** — a merged chronological stream of links saved by everyone they follow.

## Architecture

```
scripts/run_cli.py            # entry point; resolves start user, launches the app
src/
├── cli/
│   ├── app.py                # Curius-specific panes (User, Following, Feed, Link)
│   ├── base.py               # generic dropdown framework (Pane / Marker / Action nodes)
│   └── template.css          # Textual styling
├── client.py                 # thin Curius HTTP client with JWT auth
├── credentials.py            # JWT resolution (env / file)
├── graph.py                  # singleton in-memory cache for users/links/networks
├── nodes.py                  # typed dataclasses: User, Link, Highlight, Network
├── buffer.py                 # paginated merged-feed using an order-statistic RBT
└── data_structures/          # red-black tree, OS-RBT, treeset, doubly-linked list
```

Two ideas keep the code small:

1. **Lazy + memoized.** `User` and `Link` only fetch their dependencies (`links`, `following`, `network`) on first access. The graph-wide cache in `graph.py` ensures the same user reached via two different paths is the same object in memory.
2. **Pane / Marker split.** The UI doesn't construct a sub-pane until you select it. Each list item is either an `ActionNode` (do something), a `PaneNode` (already built), or a `PaneNodeMarker` (fetches its pane on demand). This keeps the graph from being eagerly walked when you only want to peek.

## Development

```bash
pip install -e ".[dev]"
pytest           # run the test suite
black .          # format
flake8 .         # lint
```

Tests live in `tests/`. The data-structure tests are pure and run in milliseconds; the rest stub out the network so nothing hits the Curius API.

## Docker

```bash
docker build -t curius .
docker run --rm -it -e CURIUS_START_USER_LINK=alice curius
```

If you need a JWT inside the container:

```bash
docker run --rm -it \
  -e CURIUS_START_USER_LINK=alice \
  -e CURIUS_JWT="$(cat ~/.credentials/curius_jwt)" \
  curius
```

## License

[MIT](LICENSE)
