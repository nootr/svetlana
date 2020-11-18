import logging
import discord
import asyncio

from datetime import datetime, timedelta
from time import sleep

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
    def __init__(self, wd_client):
        self.wd_client = wd_client
        self._pollers = []
        asyncio.Task(self._poll())
        super(DiscordClient, self).__init__()

    def _follow(self, id, channel):
        """Start following a given game by adding it to a list."""
        obj = (id, channel)
        if obj in self._pollers:
            return False

        self._pollers.append(obj)
        logging.info('Following: %s', self._pollers)
        return True

    def _unfollow(self, id, channel):
        """Stop following a given game by adding it to a list."""
        obj = (id, channel)
        if obj not in self._pollers:
            return False

        self._pollers.remove(obj)
        logging.info('Following: %s', self._pollers)
        return True

    async def _poll(self, period=1):
        """Keep polling a list of games every X minutes."""
        while True:
            for gameid, channel in self._pollers:
                async def _say(msg):
                    await channel.send(f'[ {gameid} ] {msg}')

                data = self.wd_client.fetch(gameid)
                if data['won']:
                    await _say(f"{data['won'][0]} has won!")
                    await _say(f'I will stop following this game :)')
                    self._unfollow(gameid, channel)
                elif data['drawn']:
                    countries = ', '.join(data['drawn'])
                    await _say(f'The game was a draw between {countries}!')
                    await _say(f'I will stop following this game :)')
                    self._unfollow(gameid, channel)
                elif datetime.now() + timedelta(hours=1, minutes=60-period) <= \
                        data['deadline'] <= datetime.now() + timedelta(hours=2):
                    if data['not_ready']:
                        countries = ', '.join(data['not_ready'])
                        await _say('@here Less than 2 hours left!')
                        await _say(f"These countries aren't ready: {countries}")
                    else:
                        await _say("Less than 2 hours left, everybody's ready!")
                elif datetime.now() + timedelta(hours=23,minutes=60-period) <= \
                        data['deadline']:
                    await _say('Starting new round! Good luck :)')
            await asyncio.sleep(60*period)

    async def on_message(self, message):
        if message.content in ['lol', 'rofl', 'lmao', 'haha', 'hihi']:
            await message.channel.send('lol xD')

        words = message.content.split(' ')
        if words[0] in ['Svetlana', 'svetlana', 'svet']:
            try:
                command = words[1]
                arguments = words[2:]
                logging.debug(command)

                if command == 'hi':
                    await message.channel.send(f'Hello, {message.author.name}!')
                elif command.startswith('help'):
                    await message.channel.send(DESCRIPTION)
                elif command.startswith('follow'):
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
                elif command.startswith('unfollow'):
                    if len(arguments) != 1:
                        msg = 'Could you please give me a valid ID?'
                        await message.channel.send(msg)
                    else:
                        gameid = int(arguments[0])
                        if self._unfollow(gameid, message.channel):
                            await message.channel.send('Consider it done!')
                        else:
                            await message.channel.send('Huh? What game?')
                elif command.startswith('list'):
                    gameids = [id for id, channel in self._pollers \
                            if channel == message.channel]
                    await message.channel.send(f"I'm following: {gameids}")
            except Exception as e:
                logging.error(e)
                await message.channel.send('Huh?')
