import discord
import datetime

from peewee import prefetch

from DataSource import DataSource
from models import TextChannel, User, Message, MessageContent, database


class PeeweeDataSource(DataSource):
    def setup_database(self):
        # create file
        database.connect()
        # with database:
        #     database.drop_tables([TextChannel, User, MessageContent, Message])
        #     database.create_tables([TextChannel, User, MessageContent, Message])

    # todo Error handling
    def log_message(self, message: discord.Message):
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

    def update_user(self, user: discord.Member):
        User.update(
            username=user.name,
            discriminator=user.discriminator,
            nickname=user.display_name
        ).where(
            User.id == user.id
        ).execute()

    def get_messages_from_channel(self, channel_id: str, date: datetime.date):
        channel = TextChannel.get_by_id(channel_id)
        users = User.select()
        message_contents = MessageContent.select().order_by(MessageContent.timestamp.desc())
        messages = Message \
            .select() \
            .where((Message.channel == channel) & (Message.timestamp.day == date.day)) \
            .order_by(Message.timestamp)
        return prefetch(messages, users, message_contents)
    # todo rewrite to return common value - bytes? use a formatter here (or make a separate class)
