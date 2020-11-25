import sqlite3

DEFAULT_DB_NAME = 'svetlana.db'


class Pollers:
    """A simple list of Game ID-Discord channel pairs."""
    def __init__(self, dbfile=DEFAULT_DB_NAME):
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
        assert game > 0
        assert channel > 0
        self.connection.execute('INSERT INTO pollers(game,channel) VALUES(?,?)',
                (int(game), int(channel)))
        self.connection.commit()

    def remove(self, item):
        """Remove a game-channel pair from the list."""
        game, channel = item
        assert game > 0
        assert channel > 0
        self.connection.execute("""DELETE FROM pollers
                WHERE game=? AND channel=?""", (int(game), int(channel)))
        self.connection.commit()


class Alarms:
    """A simple list of alarms."""
    def __init__(self, dbfile=DEFAULT_DB_NAME):
        self.connection = sqlite3.connect(dbfile)
        self.connection.execute("""CREATE TABLE IF NOT EXISTS alarms (
            id      INTEGER PRIMARY KEY,
            hours   INTEGER NOT NULL,
            channel INTEGER NOT NULL
        );""")
        self.connection.commit()

    def __iter__(self):
        alarms = self.connection.execute('SELECT hours, channel FROM alarms;')
        for hours, channel in alarms:
            yield (int(hours), int(channel))

    def __contains__(self, item):
        alarm, channel = item
        cursor = self.connection.cursor()
        cursor.execute('SELECT id FROM alarms WHERE hours = ? AND channel=?;',
                (int(alarm), int(channel)))
        data = cursor.fetchall()
        return len(data) > 0

    def __str__(self):
        return str(list(self))

    def append(self, item):
        """Append an alarm-channel pair to the list."""
        alarm, channel = item
        assert alarm > 0
        assert channel > 0
        self.connection.execute(
                'INSERT INTO alarms(hours, channel) VALUES(?,?);',
                (int(alarm), int(channel)))
        self.connection.commit()

    def remove(self, item):
        """Remove an alarm-channel pair from the list."""
        alarm, channel = item
        assert alarm > 0
        assert channel > 0
        self.connection.execute("""DELETE FROM alarms
                WHERE hours=? AND channel=?""", (int(alarm), int(channel)))
        self.connection.commit()
