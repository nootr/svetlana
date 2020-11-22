import logging
import discord
import asyncio

from datetime import datetime, timedelta
from time import sleep

from svetlana.db import Pollers

DESCRIPTION = """I respond to the following commands (friends call me 'svet'):
    * Svetlana hi - I simply respond to let you know I'm alive :)
    * Svetlana help - Well.. you already know this one, don't you?
    * Svetlana follow <ID> - I'll keep track of a game with this ID.
    * Svetlana unfollow <N> - I'll stop following this given game.
    * Svetlana list - I'll give you a list of the games I'm following.

I will give a notification when a new round starts and two hours before it
starts and will warn you if players have not given their orders yet.

For more info, check out https://gitlab.jhartog.dev/jhartog/svetlana
"""


class DiscordClient(discord.Client):
    def __init__(self, wd_client, db_file='pollers.db', polling=True):
        self.wd_client = wd_client
        self._pollers = Pollers(db_file)
        if polling:
            asyncio.Task(self._start_poll())
        super(DiscordClient, self).__init__()

    def _follow(self, id, channel):
        """Start following a given game by adding it to a list."""
        obj = (id, channel.id)
        if obj in self._pollers:
            return False

        self._pollers.append(obj)
        logging.info('Following: %s', self._pollers)
        return True

    def _unfollow(self, id, channel):
        """Stop following a given game by adding it to a list."""
        obj = (id, channel.id)
        if obj not in self._pollers:
            return False

        self._pollers.remove(obj)
        logging.info('Following: %s', self._pollers)
        return True

    async def _start_poll(self, period=1):
        """Keep polling a list of games every X minutes.

        Note that it first waits, then polls to prevent issues with fetching a
        channel before the client is actually logged in.
        """
        while True:
            await asyncio.sleep(60*period)
            for gameid, channelid in self._pollers:
                try:
                    await self._poll(gameid, channelid, period)
                except Exception as e:
                    logging.error('Error while polling %d: %s', gameid, e)

    async def _poll(self, gameid, channelid, period=1):
        """Poll a game."""
        channel = self.get_channel(channelid)
        assert channel

        async def _say(msg):
            await channel.send(f'[ {gameid} ] {msg}')

        game = self.wd_client.fetch(gameid)
        if game.pregame:
            if game.hours_left == 0 and game.minutes_left == 0:
                await _say(
                    f'The game starts in {timedelta.days_left} days!')
        elif game.won:
            await _say(f'{game.won} has won!')
            await _say('I will stop following this game :)')
            self._unfollow(gameid, channel)
        elif game.drawn:
            countries = ', '.join(game.drawn)
            await _say(f'The game was a draw between {countries}!')
            await _say('I will stop following this game :)')
            self._unfollow(gameid, channel)
        elif game.hours_left == 2 and game.minutes_left < period:
            if game.not_ready:
                countries = ', '.join(game.not_ready)
                await _say('@here Two hours left!')
                await _say(f"These countries aren't ready: {countries}")
            else:
                await _say("Two hours left, everybody's ready!")
        elif game.hours_left == 23 and game.minutes_left > 60 - period:
            await _say('Starting new round! Good luck :)')

    async def on_message(self, message):
        if message.content in {'lol', 'rofl', 'lmao', 'haha', 'hihi'}:
            await message.channel.send('lol xD')

        words = message.content.split(' ')
        if words[0].lower() in {'svetlana', 'svet'}:
            try:
                command = words[1]
                arguments = words[2:]
                logging.debug('Received command: %s', command)

                if command == 'hi':
                    await message.channel.send(f'Hello, {message.author.name}!')
                elif command == 'help':
                    await message.channel.send(DESCRIPTION)
                elif command == 'follow':
                    if len(arguments) != 1:
                        msg = 'Could you please give me a valid ID?'
                        await message.channel.send(msg)
                    else:
                        gameid = int(arguments[0])
                        if self._follow(gameid, message.channel):
                            await message.channel.send('Will do!')
                        else:
                            await message.channel.send(
                                "I'm already following that game!")
                elif command == 'unfollow':
                    if len(arguments) != 1:
                        msg = 'Could you please give me a valid ID?'
                        await message.channel.send(msg)
                    else:
                        gameid = int(arguments[0])
                        if self._unfollow(gameid, message.channel):
                            await message.channel.send('Consider it done!')
                        else:
                            await message.channel.send('Huh? What game?')
                elif command == 'list':
                    gameids = [id for id, channel_id in self._pollers \
                            if channel_id == message.channel.id]
                    await message.channel.send(f"I'm following: {gameids}")
            except Exception as e:
                logging.error(e)
                await message.channel.send('Huh?')
