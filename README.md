# Svetlana

[![pipeline status](https://gitlab.jhartog.dev/jhartog/svetlana/badges/master/pipeline.svg)](https://gitlab.jhartog.dev/jhartog/svetlana/-/commits/master)
[![coverage report](https://gitlab.jhartog.dev/jhartog/svetlana/badges/master/coverage.svg)](https://gitlab.jhartog.dev/jhartog/svetlana/-/commits/master)

A quick-and-dirty Discord bot which notifies about deadlines in WebDiplomacy
games.

## Installation

Installing is simple, just clone this repository and install using `pip` (the
Python 3.x one):

```bash
pip install .
```

## Commands

Svetlana understands the following commands:

| Command                    | Description                                    |
|----------------------------|------------------------------------------------|
| Svetlana hi/help           | Shows this list of commands.                   |
| Svetlana follow [GAMEID]   | Start following a certain WebDiplomacy game.   |
| Svetlana unfollow [GAMEID] | Stop following a certain WebDiplomacy game.    |
| Svetlana list              | Show list of followed games.                   |

## Development

As always, work in a virtual environment and you'll be fine:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
