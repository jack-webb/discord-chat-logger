import io
import traceback
import os

import sys
from datetime import datetime
from typing import List, Optional, BinaryIO

import discord
from discord.ext import commands
import logging
from babel.dates import format_timedelta

from FlatDataSource import FlatDataSource

logging.basicConfig(level=logging.DEBUG)

description = os.getenv("DESCRIPTION", default=None)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=os.getenv("PREFIX", default="!"), description=description, intents=intents)

data_source = FlatDataSource()


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
    data_source.log_message(message)


@bot.listen("on_message_edit")
async def log_on_message_edit(_, message: discord.Message):
    data_source.log_message(message)


@bot.listen("on_member_update")
async def update_member(before: discord.Member, after: discord.Member):
    if before.display_name != after.display_name \
            or before.name != after.name \
            or before.discriminator != after.discriminator:
        data_source.update_user(after)


# todo Add a loading message for long-running operations
@bot.command(name="logs", brief="Get chat logs for a given text channel",
             help="Retrieve one day's chat logs, including edit history, for a text channel. Provide the channel in "
                  "the form #channel. Optionally provide a date (YYYY-MM-DD), otherwise get today's logs.",
             usage="channel date"
             )
async def get_log_file(ctx: commands.Context, channel: discord.TextChannel,
                       date_str: Optional[str] = datetime.now().strftime('%Y-%m-%d')):
    if ctx.channel.id != int(os.getenv("LOG_CHANNEL")):
        return

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await ctx.channel.send(content=f"Invalid date. Dates should be formatted as YYYY-MM-DD.")
        return

    try:
        log_bytes = data_source.get_bytes(channel.id, date)
        await ctx.channel.send(
            content=f"Logs for {channel.name} on {date.strftime('%Y-%m-%d')}:",
            file=discord.File(io.BytesIO(log_bytes), filename="file.txt")
        )
    except:
        await ctx.channel.send("Could not retrieve logs. Are you using the right channel? Is the date correctly "
                               "formatted? (YYYY-MM-DD)")

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


if __name__ == "__main__":
    data_source.setup_database()
    print(os.getenv("TOKEN"))
    bot.run(os.getenv("TOKEN"))
