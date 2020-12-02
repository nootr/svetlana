"""
This module contains a Discord client which acts as a WebDiplomacy notification
bot.
"""

import logging
import asyncio

from time import sleep

import discord

from svetlana.bot.actions import respond_hi, respond_follow, respond_unfollow, \
        respond_alert, respond_silence, respond_list
from svetlana.db import Pollers, Alarms
from svetlana.webdiplomacy import InvalidGameError


class DiscordClient(discord.Client):
    """A Discord client which is used to poll WebDiplomacy games."""
    def __init__(self, wd_client, db_file='svetlana.db', polling=True):
        self.wd_client = wd_client
        self.pollers = Pollers(db_file)
        self.alarms = Alarms(db_file)
        if polling:
            asyncio.Task(self._start_poll())
        super().__init__()

    def follow(self, game_id, channel_id):
        """Start following a given game by adding it to a list."""
        if not channel_id:
            return False

        obj = (game_id, channel_id)
        if obj in self.pollers:
            return False

        self.pollers.append(obj)
        logging.info('Following: %s', self.pollers)
        return True

    def unfollow(self, game_id, channel_id):
        """Stop following a given game by removing it to a list."""
        if not channel_id:
            return False

        obj = (game_id, channel_id)
        if obj not in self.pollers:
            return False

        self.pollers.remove(obj)
        logging.info('Following: %s', self.pollers)
        return True

    def add_alert(self, hours, channel_id):
        """Add an alert for X hours before a deadline."""
        if not channel_id:
            return False

        obj = (hours, channel_id)
        if obj in self.alarms:
            return False

        self.alarms.append(obj)
        logging.info('Alerting at: %s', self.alarms)
        return True

    def remove_alert(self, hours, channel_id):
        """Stop alerting X hours before a deadline."""
        if not channel_id:
            return False

        obj = (hours, channel_id)
        if obj not in self.alarms:
            return False

        self.alarms.remove(obj)
        logging.info('Alerting at: %s', self.alarms)
        return True

    async def _start_poll(self, period=30):
        """Keep polling a list of games every X minutes.

        Note that it first waits, then polls to prevent issues with fetching a
        channel before the client is actually logged in.
        """
        while True:
            await asyncio.sleep(period)
            for game_id, channel_id, last_delta in self.pollers:
                try:
                    game = self.wd_client.fetch(game_id)
                    result = self._poll(game, channel_id, last_delta)
                    if result:
                        channel = self.get_channel(channel_id)
                        embed = self.get_embed(game, result)

                        await channel.send(embed=embed)
                except InvalidGameError:
                    self.unfollow(game_id, channel_id)
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
            self.unfollow(game.game_id, channel_id)
            msg = f'{game.won} has won!'
        elif game.drawn:
            countries = ', '.join(game.drawn)
            self.unfollow(game.game_id, channel_id)
            msg = f'The game was a draw between {countries}!'
        elif last_delta and game.delta > last_delta:
            # NOTE(jhartog): We need to give WebDiplomacy some time to generate
            # a map, otherwise we'll get the map from last turn.
            sleep(map_generate_seconds)
            msg = 'Starting new round! Good luck :)'

        for hours, ch_id in self.alarms:
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

        self.pollers.update_delta((game.game_id, channel_id), game.delta)
        return msg

    @staticmethod
    def get_embed(game, msg=''):
        """Embeds a given message to show relevant game info."""
        embed = discord.Embed(
                title=f'{game.name} - {game.date} - {game.phase} phase',
                description=msg,
                url=game.url,
            )
        embed.set_image(url=game.map_url)

        return embed

    def _answer_message(self, message):
        """React to a message."""
        words = message.content.split(' ')
        command = words[1]
        arguments = words[2:]
        logging.debug('Received command: %s', command)

        response_generators = {
            'hi':       respond_hi,
            'help':     respond_hi,
            'follow':   respond_follow,
            'unfollow': respond_unfollow,
            'alert':    respond_alert,
            'silence':  respond_silence,
            'list':     respond_list,
        }

        try:
            resp_gen = response_generators.get(command, lambda *args: 'Huh?')
            response = resp_gen(
                bot=self,
                message=message,
                command=command,
                arguments=arguments
            )
            return response
        except ValueError:
            return 'Huh?'

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
