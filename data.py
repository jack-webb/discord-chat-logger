import discord
import datetime
from models import TextChannel, User, Message, MessageContent, database


def setup_database():
    database.connect()
    # with database:
    #     database.drop_tables([TextChannel, User, MessageContent, Message])
    #     database.create_tables([TextChannel, User, MessageContent, Message])


# todo error handling
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


def update_user(user: discord.Member):
    User.update(
        username=user.name,
        discriminator=user.discriminator,
        nickname=user.display_name
    ).where(
        User.id == user.id
    ).execute()

# todo Can we make this query more efficient?
def get_messages_from_channel(channel_id: str, date: datetime.date):
    channel = TextChannel.get_by_id(channel_id)
    return Message \
        .select() \
        .where((Message.channel == channel) & (Message.timestamp.day == date.day)) \
        .order_by(Message.timestamp)
