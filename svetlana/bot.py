import logging
import discord

class Client(discord.Client):
    async def on_ready(self):
        logging.info(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        logging.debug(message)
        if message.content == 'lol':
            await message.channel.send('haha')

        if message.content == 'hi':
            await message.channel.send(f'Hello, {message.author.name}!')

bot = Client()
