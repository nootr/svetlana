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

| Command                     | Description                                    |
|-----------------------------|------------------------------------------------|
| @Svetlana follow [GAMEID]   | Start following a certain WebDiplomacy game.   |
| @Svetlana unfollow [GAMEID] | Stop following a certain WebDiplomacy game.    |
| @Svetlana list              | Show list of followed games.                   |
| @Svetlana status [GAMENO]   | Show status of certain game. Default GAMENO: 1 |

## TODO

[ ] Create WebDiplomacy class as interface
[ ] Create Bot class
[ ] Create setup.py
[ ] Add CI/CD pipeline
