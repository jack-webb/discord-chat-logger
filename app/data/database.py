import io
from typing import List

import discord
import datetime

from babel.dates import format_timedelta
from peewee import prefetch

from data.models import TextChannel, User, Message, MessageContent, database


class PeeweeDataSource:
    def setup_database(self):
        database.connect()
        database.create_tables([TextChannel, User, Message, MessageContent], safe=True)
        database.close()

    # todo Error handling
    def log_message(self, message: discord.Message):
        database.connect()
        user, _ = User.get_or_create(
            id=message.author.id,
            defaults={
                "username": message.author.name,
                "discriminator": message.author.discriminator,
                "nickname": message.author.display_name
            })

        text_channel, _ = TextChannel.get_or_create(
            id=message.channel.id,
            defaults={"name": message.channel.name}
        )

        msg, _ = Message.get_or_create(
            id=message.id,
            defaults={
                "author": user,
                "channel": text_channel,
                "timestamp": message.created_at,
                "jump_url": message.jump_url
            })

        attachment = ""
        try:
            attachment = message.attachments[0].proxy_url
        except IndexError:
            pass  # Ignore, just means we don't have an attachment

        # todo Embeds show as an empty message - this needs better handling
        MessageContent.create(
            message_id=msg,
            timestamp=message.edited_at or message.created_at,
            text=message.clean_content,
            attachment_url=attachment
        )

        database.close()

    def update_user(self, user: discord.Member):
        database.connect()
        User.update(
            username=user.name,
            discriminator=user.discriminator,
            nickname=user.display_name
        ).where(
            User.id == user.id
        ).execute()
        database.close()

    def create_log_file(self, messages: List[Message], date: datetime.date) -> io.StringIO:
        if len(messages) == 0:
            raise IndexError

        s = io.StringIO()

        s.write(f"--- Chat logs for #{messages[0].channel.name} on {date.strftime('%Y-%m-%d')} ---\n")

        for message in messages:
            s.write(self.process_message_out(message))
            s.write("\n")

        s.seek(0)

        return s

    def process_message_out(self, message: Message):
        output = ""

        ordered_contents = message.content.order_by(MessageContent.timestamp.desc())
        current, previous = ordered_contents[0], ordered_contents[1:]

        if str(message.author.nickname) == f"{message.author.username}":
            output += f"[{message.timestamp.strftime('%H:%M:%S')}] {message.author.username}#{message.author.discriminator}: {current.text} {current.attachment_url}"
        else:
            output += f"[{message.timestamp.strftime('%H:%M:%S')}] {message.author.username}#{message.author.discriminator} ({message.author.nickname}): {current.text} {current.attachment_url}"

        for content in previous:
            relative_time = current.timestamp - content.timestamp
            output += f"\n↪ {format_timedelta(relative_time, locale='en_US')} ago: {content.text} {content.attachment_url}"

        return output

    def get_messages_from_channel(self, channel_id: str, date: datetime.date):
        channel = TextChannel.get_by_id(channel_id)
        users = User.select()
        message_contents = MessageContent.select().order_by(MessageContent.timestamp.desc())
        messages = Message \
            .select() \
            .where((Message.channel == channel) & (Message.timestamp.day == date.day)) \
            .order_by(Message.timestamp)
        return prefetch(messages, users, message_contents)
