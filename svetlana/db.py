import sqlite3

class Pollers:
    """A simple list of Game ID-Discord channel pairs."""
    def __init__(self, dbfile='pollers.db'):
        self.connection = sqlite3.connect(dbfile)
        self.connection.execute("""CREATE TABLE IF NOT EXISTS pollers (
            id      INTEGER PRIMARY KEY,
            game    INTEGER NOT NULL,
            channel INTEGER NOT NULL
        );""")
        self.connection.commit()

    def __iter__(self):
        pollers = self.connection.execute('SELECT game, channel FROM pollers;')
        for game, channel in pollers:
            yield (int(game), int(channel))

    def __contains__(self, item):
        game, channel = item
        cursor = self.connection.cursor()
        cursor.execute('SELECT id FROM pollers WHERE game = ? AND channel = ?',
                (int(game), int(channel)))
        data = cursor.fetchall()
        return len(data) > 0

    def __str__(self):
        return str(list(self))

    def append(self, item):
        """Append a game-channel pair to the list."""
        game, channel = item
        self.connection.execute('INSERT INTO pollers(game,channel) VALUES(?,?)',
                (int(game), int(channel)))
        self.connection.commit()

    def remove(self, item):
        """Remove a game-channel pair from the list."""
        game, channel = item
        self.connection.execute("""DELETE FROM pollers
                WHERE game=? AND channel=?""", (int(game), int(channel)))
        self.connection.commit()
