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

    async def _poll(self):
        """Keep polling a list of games every 15 minutes."""
        while True:
            for gameid, channel in self._pollers:
                data = self.wd_client.fetch(gameid)
                if data['won']:
                    await channel.send(f"{data['won'][0]} has won!")
                elif data['deadline'] < datetime.now() + timedelta(hours=2):
                    if data['not_ready']:
                        await channel.send('@here Less than 2 hours left!')
                        await channel.send(f"Not ready: {data['not_ready']}")
                    else:
                        await channel.send(
                            "Less than 2 hours left and everybody's ready!")
            await asyncio.sleep(60*15)

    async def on_ready(self):
        logging.info(f'{self.user} has connected to Discord!')

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
