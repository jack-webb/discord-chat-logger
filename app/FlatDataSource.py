import os
from typing import List, BinaryIO

import discord
import datetime

from peewee import prefetch

from DataSource import DataSource
from models import TextChannel, User, Message, MessageContent, database


class FlatDataSource(DataSource):
    def setup_database(self):
        # create file
        pass

    # todo Error handling
    def log_message(self, message: discord.Message):
        filename = self._get_filename(message.channel.id, datetime.datetime.now())
        with open(filename, 'a') as f:
            f.write(f"{self._format_message(message)}\n")

    def update_user(self, user: discord.Member):
        # Not supported
        pass

    def get_messages_from_channel(self, channel_id: str, date: datetime.date) -> List[str]:
        # get filename for that day, based on str
        filename = self._get_filename(channel_id, date)

        with open(filename, "r") as f:
            lines = f.read().splitlines()
            return lines

    def get_bytes(self, channel_id: str, date: datetime.date) -> bytes:
        filename = self._get_filename(channel_id, date)
        with open(filename, "rb") as b:
            return b.read()

    @staticmethod
    def _get_filename(channel_id: str, date: datetime.date):
        date_format = "%Y-%b-%d"
        return f"{channel_id}-{date.strftime(date_format)}.txt"

    @staticmethod
    def _format_message(message: discord.Message) -> str:
        return f"[{message.created_at.strftime('%H:%M:%S')}] {message.author}: {message.content} | Message ID {message.id}"
