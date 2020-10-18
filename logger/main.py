import sys
from datetime import datetime

import discord
import config
from logger import data

client = discord.Client()


@client.event
async def on_ready():
    print("=====================")
    print("Discord Chat Logger, by Jack Webb")
    print("https://github.com/jack-webb/discord-chat-logger/")
    print(f"Python version {sys.version}")
    print(f"discord.py version {discord.__version__}")
    print(f"Logger ready, logged in as {client.user}")
    print("=====================")


@client.event
async def on_message(message):
    data.log_message(message)

    if message.channel.id == config.log_channel and message.content[0] == config.prefix:
        _, channel_id, *optional_args = message.content.split(" ")
        channel_id = channel_id[2:-1]  # Hacky way of removing "<#...>"

        if len(optional_args) > 1:
            # too many args
            pass
        if len(optional_args) == 1:
            # Should be a date arg
            date = datetime.strptime(optional_args[0], '%Y-%m-%d').date()
            logs = data.get_messages_from_channel(channel_id, date)
            for log in logs:
                print(log)
        else:
            logs = data.get_messages_from_channel(channel_id)
            for log in logs:
                print(log)

@client.event
async def on_message_edit(_, message):
    data.log_message(message)


if __name__ == '__main__':
    data.setup_database()
    client.run(config.token)
