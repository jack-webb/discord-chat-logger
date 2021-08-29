import os

from peewee import Model, CharField, ForeignKeyField, DateTimeField, SqliteDatabase, BigIntegerField, TextField, \
    BooleanField

database = SqliteDatabase(os.path.join("app", "database", "chat-logger.db"))


class BaseModel(Model):
    class Meta:
        database = database


class TextChannel(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = CharField()

    class Meta:
        table_name = 'text_channels'


class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    username = CharField()
    discriminator = CharField()
    nickname = CharField()

    class Meta:
        table_name = 'users'


class Message(BaseModel):
    id = BigIntegerField(primary_key=True)
    author = ForeignKeyField(column_name='author_id', model=User)
    channel = ForeignKeyField(column_name='channel_id', model=TextChannel)
    timestamp = DateTimeField()
    jump_url = CharField()
    was_deleted = BooleanField(default=False)

    class Meta:
        table_name = 'messages'


class MessageContent(BaseModel):
    message = ForeignKeyField(column_name='message_id', model=Message, backref="content")
    timestamp = DateTimeField()
    text = TextField()
    attachment_url = CharField(null=True)

    class Meta:
        table_name = 'message_contents'
