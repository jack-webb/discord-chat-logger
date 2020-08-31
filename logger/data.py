import discord
import config
from logger.models import TextChannel, User, Message, MessageContent, database


def setup_database():
    database.connect()
    with database:
        if config.debug:
            database.drop_tables([TextChannel, User, MessageContent, Message])
        database.create_tables([TextChannel, User, MessageContent, Message])


def log_message(message: discord.Message):
    user, _ = User.get_or_create(
        id=message.author.id,
        defaults={
            "name": message.author.name,
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
            "created_at": message.created_at,
            "author": user,
            "channel": text_channel,
            "jump_url": message.jump_url
        })

    MessageContent.create(
        message_id=msg,
        timestamp=message.created_at,
        content=message.clean_content
    )
