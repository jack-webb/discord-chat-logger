import os

from peewee import SqliteDatabase, BooleanField
from playhouse.migrate import SqliteMigrator, migrate

database = SqliteDatabase(os.path.join("app", "database", "chat-logger.db"))
migrator = SqliteMigrator(database)

was_deleted_field = BooleanField(default=False)

migrate(
    migrator.add_column("messages", "was_deleted", was_deleted_field)
)
