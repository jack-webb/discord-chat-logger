import os
import config
from peewee import Model, CharField, ForeignKeyField, DateTimeField, PostgresqlDatabase, BigIntegerField

# DATABASE = os.path.join(
#     os.path.dirname(os.path.realpath(__file__)),
#     'logger.db'
# )
# DATABASE_PRAGMAS = {'foreign_keys': 1}

database = PostgresqlDatabase(
    config.database['name'],
    user=config.database['user'],
    password=config.database['password'],
    host=config.database['host']
)


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
    discriminator = CharField()
    nickname = CharField()
    name = CharField()

    class Meta:
        table_name = 'users'


class Message(BaseModel):
    id = BigIntegerField(primary_key=True)
    author = ForeignKeyField(column_name='author_id', model=User)
    channel = ForeignKeyField(column_name='channel_id', model=TextChannel)
    created_at = DateTimeField()
    jump_url = CharField()

    class Meta:
        table_name = 'messages'


class MessageContent(BaseModel):
    content = CharField()
    message = ForeignKeyField(column_name='message_id', model=Message, backref="contents")
    timestamp = DateTimeField()

    class Meta:
        table_name = 'message_contents'
