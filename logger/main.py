import io
import sys
from datetime import datetime
from typing import List

import discord
import logging
from babel.dates import format_timedelta

import config
from logger import data, models
from logger.models import MessageContent

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    print("=====================")
    print("Discord Chat Logger, by Jack Webb")
    print("https://github.com/jack-webb/discord-chat-logger/")
    print(f"Python version {sys.version}")
    print(f"discord.py version {discord.__version__}")
    print(f"Logger ready, logged in as {client.user}")
    print("=====================")


# todo Nickname/user updates
@client.event
async def on_message(message: discord.Message):
    data.log_message(message)

    # todo this is kinda messy, doesn't really support multiple commands nicely
    if str(message.channel.id) == config.log_channel and message.content[0] == config.prefix: # todo just checks prefix, not for command
        _, channel_id, *optional_args = message.content.split(" ")
        if channel_id[0].isdigit():
            error("Embedded channel required, not ID")
        channel_id = channel_id[
                     2:-1]  # Hacky way of removing "<#...>" todo can we get this from the object instead of the str repr

        if len(optional_args) > 1:
            # too many args
            pass
        if len(optional_args) == 1: # todo date isnt recognised lmao
            # Should be a date arg, todo validate
            date = datetime.strptime(optional_args[0], '%Y-%m-%d').date()
            messages = data.get_messages_from_channel(channel_id, date)  # todo this is hit twice?
            file = x(messages)  ## todo rename
            await message.channel.send(file=discord.File(file, filename="logs.txt"))
        else:
            messages = data.get_messages_from_channel(channel_id)
            file = x(messages)  ## todo rename
            await message.channel.send(file=discord.File(file, filename="logs.txt"))


@client.event
async def on_message_edit(_, message: discord.Message):
    data.log_message(message)


@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.display_name != after.display_name \
            or before.name != after.name \
            or before.discriminator != after.discriminator:
        data.update_user(after)


# todo this is spitting out a shitload of queries - investigate
def process_message_out(message: models.Message):
    output = ""

    ordered_contents = message.content.order_by(MessageContent.timestamp.desc())
    current, previous = ordered_contents[0], ordered_contents[1:]

    if str(message.author.nickname) == f"{message.author.username}#{message.author.discriminator}":
        output += f"[{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message.author.username}#{message.author.discriminator}: {current.text} {current.attachment_url}"
    else:
        output += f"[{message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message.author.username}#{message.author.discriminator} ({message.author.nickname}): {current.text} {current.attachment_url}"

    for content in previous:
        relative_time = current.timestamp - content.timestamp
        output += f"\n↪ {format_timedelta(relative_time, locale='en_US')} ago: {content.text} {content.attachment_url}"

    return output


def x(messages: List[models.Message]):
    s = io.StringIO()

    for message in messages:
        s.write(process_message_out(message))
        s.write("\n")

    s.seek(0)  # Seek back to the beginning ready to send

    return s


def error(message: str):
    # Send some error message
    pass


if __name__ == '__main__':
    data.setup_database()
    client.run(config.token)
