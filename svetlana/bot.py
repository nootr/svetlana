"""
This module contains a Discord client which acts as a WebDiplomacy notification
bot.
"""

import hashlib
import logging
import asyncio

from time import sleep

import discord

from svetlana.db import Pollers, Alarms
from svetlana.webdiplomacy import InvalidGameError


DESCRIPTION = """I respond to the following commands (friends call me 'svet'):
    * Svetlana hi/help - I'll show you this list!
    * Svetlana follow <ID> - I'll keep track of a game with this ID.
    * Svetlana unfollow <N> - I'll stop following this given game.
    * Svetlana alert <N> - I'll alert N hours before a deadline.
    * Svetlana silence <N> - I won't alert N hours before a deadline.
    * Svetlana list - I'll give you a list of the games I'm following.

I will give a notification when a new round starts and two hours before it
starts and will warn you if players have not given their orders yet.

For more info, check out https://gitlab.jhartog.dev/jhartog/svetlana
"""


class DiscordClient(discord.Client):
    """A Discord client which is used to poll WebDiplomacy games."""
    def __init__(self, wd_client, db_file='svetlana.db', polling=True):
        self.wd_client = wd_client
        self._pollers = Pollers(db_file)
        self._alarms = Alarms(db_file)
        if polling:
            asyncio.Task(self._start_poll())
        super().__init__()

    def _follow(self, game_id, channel_id):
        """Start following a given game by adding it to a list."""
        if not channel_id:
            return False

        obj = (game_id, channel_id)
        if obj in self._pollers:
            return False

        self._pollers.append(obj)
        logging.info('Following: %s', self._pollers)
        return True

    def _unfollow(self, game_id, channel_id):
        """Stop following a given game by removing it to a list."""
        if not channel_id:
            return False

        obj = (game_id, channel_id)
        if obj not in self._pollers:
            return False

        self._pollers.remove(obj)
        logging.info('Following: %s', self._pollers)
        return True

    def _add_alert(self, hours, channel_id):
        """Add an alert for X hours before a deadline."""
        if not channel_id:
            return False

        obj = (hours, channel_id)
        if obj in self._alarms:
            return False

        self._alarms.append(obj)
        logging.info('Alerting at: %s', self._alarms)
        return True

    def _remove_alert(self, hours, channel_id):
        """Stop alerting X hours before a deadline."""
        if not channel_id:
            return False

        obj = (hours, channel_id)
        if obj not in self._alarms:
            return False

        self._alarms.remove(obj)
        logging.info('Alerting at: %s', self._alarms)
        return True

    async def _start_poll(self, period=30):
        """Keep polling a list of games every X minutes.

        Note that it first waits, then polls to prevent issues with fetching a
        channel before the client is actually logged in.
        """
        while True:
            await asyncio.sleep(period)
            for game_id, channel_id, last_delta in self._pollers:
                try:
                    game = self.wd_client.fetch(game_id)
                    result = self._poll(game, channel_id, last_delta)
                    if result:
                        channel = self.get_channel(channel_id)
                        embed = self._get_embed(game, result)

                        await channel.send(embed=embed)
                except InvalidGameError:
                    self._unfollow(game_id, channel_id)
                    channel = self.get_channel(channel_id)
                    await channel.send(
                            'The game seems to be cancelled! Unfollowing..')


    def _poll(self, game, channel_id, last_delta, map_generate_seconds=10):
        """Poll a game. Returns a message, if needed."""
        msg = None
        if game.pregame:
            if game.hours_left % 24 == 0 and game.minutes_left == 0:
                msg = f'The game starts in {game.days_left} days!'
        elif game.won:
            self._unfollow(game.game_id, channel_id)
            msg = f'{game.won} has won!'
        elif game.drawn:
            countries = ', '.join(game.drawn)
            self._unfollow(game.game_id, channel_id)
            msg = f'The game was a draw between {countries}!'
        elif last_delta and game.delta > last_delta:
            # NOTE(jhartog): We need to give WebDiplomacy some time to generate
            # a map, otherwise we'll get the map from last turn.
            sleep(map_generate_seconds)
            msg = 'Starting new round! Good luck :)'

        for hours, ch_id in self._alarms:
            if ch_id != channel_id:
                continue

            if last_delta and game.delta <= hours*3600 and \
                    last_delta > hours*3600:
                if game.not_ready:
                    countries = ', '.join(game.not_ready)
                    msg = f"{hours}h left! These countries aren't ready: " + \
                            countries
                else:
                    msg = f"{hours}h left, everybody's ready!"

        self._pollers.update_delta((game.game_id, channel_id), game.delta)
        return msg

    @staticmethod
    def _get_embed(game, msg=''):
        embed = discord.Embed(
                title=f'{game.title} - {game.date} - {game.phase} phase',
                description=msg,
                url=game.url,
            )
        embed.set_image(url=game.map_url)

        return embed

    def _answer_message(self, message):
        """React to a message."""
        # pylint: disable=too-many-branches
        # NOTE(jhartog): This method, although ugly, contains the bulk of the
        # logic, the heart and soul of the bot. Which sophisticated AI doesn't
        # have too many branches?

        def _hash(string):
            return hashlib.sha256(string.encode('utf-8')).digest()

        words = message.content.split(' ')
        command = words[1]
        arguments = words[2:]
        msg = None
        logging.debug('Received command: %s', command)

        if command in {'hi', 'hello', 'help'}:
            msg = f'Hello, {message.author.name}!\n{DESCRIPTION}'
        elif command == 'follow':
            game_id = int(arguments[0])
            game = self.wd_client.fetch(game_id)
            if self._follow(game_id, message.channel.id):
                desc = f'Now following {game_id}!'
            else:
                desc = "I'm already following that game!"
            msg = self._get_embed(game, desc)
        elif command == 'unfollow':
            game_id = int(arguments[0])
            if self._unfollow(game_id, message.channel.id):
                msg = 'Consider it done!'
            else:
                msg = 'Huh? What game?'
        elif command == 'alert':
            if arguments[0] == 'list':
                alarms = [f'T-{h}h' for h, c in self._alarms \
                        if c == message.channel.id]
                msg = "I'm alerting at: " + ', '.join(alarms)
            else:
                hours = int(arguments[0])
                if self._add_alert(hours, message.channel.id):
                    msg = f'OK, I will alert {hours} hours before a deadline.'
                else:
                    msg = \
                        f"I'm already alerting {hours} hours before a deadline!"
        elif command == 'silence':
            hours = int(arguments[0])
            if self._remove_alert(hours, message.channel.id):
                msg = f'Understood, I will stop alerting T-{hours}h..'
            else:
                msg = f"I already don't alert {hours} hours before a deadline?!"
        elif command == 'list':
            game_ids = [str(g) for g, c, _ in self._pollers \
                    if c == message.channel.id]
            msg = "I'm following: " + ', '.join(game_ids)
        elif _hash(command) == b'\xb9\xa3e\xc4\xd2g]_\xd8\xecwg*+' + \
                b'\xc2\x94t\x18L8\x05\xb5P\xb9\x87\xb60\xc8< \x0c\x9c':
            # There are no easter eggs here, just serious features
            msg = f'pls {command}?'

        return msg

    async def on_message(self, message):
        """Recieve, parse and possibly react to a message."""
        if message.content in {'lol', 'rofl', 'lmao', 'haha', 'hihi'}:
            await message.channel.send('lol xD')

        words = message.content.split(' ')
        if words[0].lower() in {'svetlana', 'svet'}:
            try:
                answer = self._answer_message(message)
                if not answer:
                    raise ValueError(f'Unknown command: {message.content}')
                if isinstance(answer, discord.Embed):
                    await message.channel.send(embed=answer)
                else:
                    await message.channel.send(answer)
            except InvalidGameError:
                await message.channel.send('That game seems to be invalid!')
            except Exception as exc: # pylint: disable=broad-except
                # NOTE(jhartog): A broad except is justified here as it saves a
                # huge amount of input validation and sanitization while not
                # being dangerous. The bot needs to let the user know it
                # couldn't parse the message.
                logging.warning(exc)
                await message.channel.send('Huh?')
