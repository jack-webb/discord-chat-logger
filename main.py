import io
import traceback

import sys
from datetime import datetime
from typing import List, Optional

import discord
from discord.ext import commands
import logging
from babel.dates import format_timedelta

import config
import data
import models

logging.basicConfig(level=logging.DEBUG)

description = config.description

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=config.prefix, description=description, intents=intents)


@bot.event
async def on_ready():
    print("=====================")
    print("Discord Chat Logger, by Jack Webb")
    print("https://github.com/jack-webb/discord-chat-logger/")
    print(f"Python version {sys.version}")
    print(f"discord.py version {discord.__version__}")
    print(f"Logger ready, logged in as {bot.user}")
    print("=====================")


@bot.listen("on_message")
async def log_on_message(message: discord.Message):
    data.log_message(message)


@bot.listen("on_message_edit")
async def log_on_message_edit(_, message: discord.Message):
    data.log_message(message)


@bot.listen("on_member_update")
async def update_member(before: discord.Member, after: discord.Member):
    if before.display_name != after.display_name \
            or before.name != after.name \
            or before.discriminator != after.discriminator:
        data.update_user(after)


# todo Add a loading message for long-running operations
@bot.command(name="logs", brief="Get chat logs for a given text channel",
             help="Retrieve one day's chat logs, including edit history, for a text channel. Provide the channel in "
                  "the form #channel. Optionally provide a date (YYYY-MM-DD), otherwise get today's logs.",
             usage="channel date"
             )
async def get_log_file(ctx: commands.Context, channel: discord.TextChannel, date_str: Optional[str] = datetime.now().strftime('%Y-%m-%d')):
    if ctx.channel.id != config.log_channel:
        return

    start_time = datetime.now()

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await ctx.channel.send(content=f"Invalid date. Dates should be formatted as YYYY-MM-DD.")
        return

    messages = data.get_messages_from_channel(channel.id, date)
    try:
        file = create_log_file(messages, date)
    except IndexError:
        await ctx.channel.send(content=f"No messages available for {channel.mention} on {date.strftime('%Y-%m-%d')}")
        return

    end_time = datetime.now()
    duration = int((end_time - start_time).microseconds * 0.001)

    await ctx.channel.send(
        content=f"Retrieved {len(messages)} messages in {duration}ms.",
        file=discord.File(file, filename=f"{ctx.guild.name}-{channel.name}-{date.strftime('%Y-%m-%d')}-log.txt")
    )
    # todo Remove "reference before assignment" warnings


# todo Is there an error-specific way to handle this? Or a better way to handle params?
@bot.listen("on_command_error")
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == "channel":
            await ctx.channel.send("You must supply a channel name!")
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.channel.send(f"Channel `{error.argument}` not found. Valid channels will autocomplete.")
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def process_message_out(message: models.Message):
    output = ""

    current, previous = message.content[0], message.content[1:]

    if str(message.author.nickname) == f"{message.author.username}":
        output += f"[{message.timestamp.strftime('%H:%M:%S')}] {message.author.username}#{message.author.discriminator}: {current.text} {current.attachment_url}"
    else:
        output += f"[{message.timestamp.strftime('%H:%M:%S')}] {message.author.username}#{message.author.discriminator} ({message.author.nickname}): {current.text} {current.attachment_url}"

    for content in previous:
        relative_time = current.timestamp - content.timestamp
        output += f"\n↪ {format_timedelta(relative_time, locale='en_US')} ago: {content.text} {content.attachment_url}"

    return output


def create_log_file(messages: List[models.Message], date: datetime.date) -> io.StringIO:
    if len(messages) == 0:
        raise IndexError

    s = io.StringIO()

    s.write(f"--- Chat logs for #{messages[0].channel.name} on {date.strftime('%Y-%m-%d')} ---\n")

    for message in messages:
        s.write(process_message_out(message))
        s.write("\n")

    s.seek(0)

    return s


if __name__ == "__main__":
    data.setup_database()
    bot.run(config.token)
