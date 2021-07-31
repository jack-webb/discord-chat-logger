from typing import List

import discord
import datetime


class DataSource:
    def setup_database(self):
        pass

    def log_message(self, message: discord.Message):
        pass

    def update_user(self, user: discord.Member):
        pass

    def get_messages_from_channel(self, channel_id: str, date: datetime.date) -> List[str]:
        pass

    def get_bytes(self, channel_id: str, date:datetime.date) -> bytes:
        pass
