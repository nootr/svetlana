# Svetlana

A quick-and-dirty Discord bot which notifies about deadlines in WebDiplomacy
games.

## Installation

Installing is simple, just clone this repository and install using `pip`:

```bash
pip install .
```

## Commands

Svetlana understands the following commands:

| Command                    | Description                                    |
|----------------------------|------------------------------------------------|
| Svetlana hi                | Just say hi! Useful to see if she's alive.     |
| Svetlana help              | Shows this list of commands.                   |
| Svetlana follow [GAMEID]   | Start following a certain WebDiplomacy game.   |
| Svetlana unfollow [GAMEID] | Stop following a certain WebDiplomacy game.    |
| Svetlana list              | Show list of followed games.                   |

## TODO

[x] Create WebDiplomacy class as interface
[x] Create Bot class
[x] Implement commands
[ ] Create setup.py
[ ] Add CI/CD pipeline
