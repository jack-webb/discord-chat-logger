import discord
import datetime
from logger.models import TextChannel, User, Message, MessageContent, database


def setup_database():
    database.connect()
    with database:
        database.drop_tables([TextChannel, User, MessageContent, Message])
        database.create_tables([TextChannel, User, MessageContent, Message])


def log_message(message: discord.Message):
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

    MessageContent.create(
        message_id=msg,
        timestamp=message.created_at,
        text=message.clean_content
    )


def get_messages_from_channel(channel_id: str, date: datetime.date = datetime.date.today(), include_edits: bool = False):
    channel = TextChannel.get_by_id(channel_id)
    if include_edits:
        return Message.select().where(Message.channel == channel)
    return Message.select().where((Message.channel == channel) & (Message.timestamp == date)).prefetch()
