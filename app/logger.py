import io
from datetime import datetime
from typing import List

import discord
from babel.dates import format_timedelta
from peewee import prefetch

from data.models import Message
from data.database import log_message, get_messages_from_channel, update_user


def get_log_file(channel_id: int, date: datetime.date):
    messages = get_messages_from_channel(str(channel_id), date)
    return create_log_file(messages, date)


def create_log_file(messages: List[Message], date: datetime.date) -> io.StringIO:
    if len(messages) == 0:
        raise IndexError

    s = io.StringIO()

    s.write(f"--- Chat logs for #{messages[0].channel.name} on {date.strftime('%Y-%m-%d')} ---\n")

    for message in messages:
        s.write(process_message_out(message))
        s.write("\n")

    s.seek(0)

    return s


def process_message_out(message: Message):
    output = ""

    ordered_contents = list(reversed(sorted(message.content, key=lambda x: x.timestamp)))
    current, previous = ordered_contents[0], ordered_contents[1:]

    if str(message.author.nickname) == f"{message.author.username}":
        output += f"[{message.timestamp.strftime('%H:%M:%S')}] {message.author.username}#{message.author.discriminator}: {current.text} {current.attachment_url}"
    else:
        output += f"[{message.timestamp.strftime('%H:%M:%S')}] {message.author.username}#{message.author.discriminator} ({message.author.nickname}): {current.text} {current.attachment_url}"

    for content in previous:
        relative_time = current.timestamp - content.timestamp
        output += f"\n↪ {format_timedelta(relative_time, locale='en_US')} ago: {content.text} {content.attachment_url}"

    return output
