import logging
import sys

import discord

import config
from logger import data

client = discord.Client()


class ChatLogger(discord.Client):
    async def on_ready(self):
        print("=====================")
        print("Chat Logger ready")
        print(f"Python version {sys.version}")
        print(f"d.py version {discord.__version__}")
        print(f"Logged in as {self.user}")
        print("=====================")

    async def on_message(self, message):
        data.log_message(message)

    async def on_message_edit(self, _, message):
        data.log_message(message)


if __name__ == '__main__':
    if config.verbose:
        logger = logging.getLogger('peewee')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    data.setup_database()
    bot = ChatLogger()
    bot.run(config.token)
