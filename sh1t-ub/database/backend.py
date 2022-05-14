#    Sh1t-UB (telegram userbot by sh1tn3t)
#    Copyright (C) 2021-2022 Sh1tN3t

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio

from pyrogram import Client, types
from typing import Union


class CloudDatabase:
    """Чат в Telegram с данными для базы данных"""

    def __init__(self, app: Client, me: types.User):
        self._app = app
        self._me = me
        self.data_chat = None

        asyncio.get_event_loop().create_task(
            self.find_data_chat())

    async def find_data_chat(self):
        """Информация о чате с данными"""
        if not self.data_chat:
            chat = [
                dialog.chat async for dialog in self._app.iter_dialogs()
                if dialog.chat.title == f"sh1t-{self._me.id}-data"
                and dialog.chat.type == "supergroup"
            ]

            if not chat:
                self.data_chat = await self._app.create_supergroup(f"sh1t-{self._me.id}-data")
            else:
                self.data_chat = chat[0]

        return self.data_chat

    async def save_data(self, message: Union[types.Message, str]):
        """Сохранить данные в чат"""
        return (
            await self._app.send_message(
                self.data_chat.id, message
            )
            if isinstance(message, str)
            else await message.copy(self.data_chat.id)
        )

    async def get_data(self, message_id: int):
        """Найти данные по айди сообщения"""
        return await self._app.get_messages(
            self.data_chat.id, message_id
        )
