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

import logging
import re

from loguru import logger
from typing import Union

from pyrogram import errors

from .types import Item
from .. import utils, fsm


class TokenManager(Item):
    """Менеджер токенов"""

    async def _create_bot(self) -> Union[str, None]:
        """Создать и настроить бота"""
        logging.info("Начался процесс создания нового бота...")

        async with fsm.Conversation(self._app, "@BotFather", True) as conv:
            try:
                await conv.ask("/cancel")
            except errors.UserIsBlocked:
                await self._app.unblock_user("@BotFather")

            await conv.get_response()

            await conv.ask("/newbot")
            response = await conv.get_response()

            if not all(
                phrase not in response.text
                for phrase in ["That I cannot do.", "Sorry"]
            ):
                logging.error(f"Произошла ошибка при создании бота. Ответ @BotFather:")
                logging.error(response.text)
                return False

            await conv.ask(f"Sh1tN3t UserBot of {utils.get_display_name(self._all_modules.me)[:45]}")
            await conv.get_response()

            bot_username = f"sh1tub_{utils.random_id(6)}_bot"

            await conv.ask(bot_username)
            response = await conv.get_response()

            search = re.search(r"(?<=<code>)(.*?)(?=</code>)", response.text.html)
            if not search:
                logging.error("Произошла ошибка при создании бота. Ответ @BotFather:")
                return logging.error(response.text)

            token = search.group(0)

            await conv.ask("/setuserpic")
            await conv.get_response()

            await conv.ask("@" + bot_username)
            await conv.get_response()

            await conv.ask_media("bot_avatar.png", media_type="photo")
            await conv.get_response()

            await conv.ask("/setinline")
            await conv.get_response()

            await conv.ask("@" + bot_username)
            await conv.get_response()

            await conv.ask("sh1t-команда")
            await conv.get_response()

            logger.success("Бот успешно создан")
            return token

    async def _revoke_token(self) -> str:
        """Сбросить токен бота"""
        async with fsm.Conversation(self._app, "@BotFather", True) as conv:
            try:
                await conv.ask("/cancel")
            except errors.UserIsBlocked:
                await self._app.unblock_user("@BotFather")

            await conv.get_response()

            await conv.ask("/revoke")
            response = await conv.get_response()

            if "/newbot" in response.text:
                return logging.error("Нет созданных ботов")

            for row in response.reply_markup.keyboard:
                for button in row:
                    search = re.search(r"@sh1tub_[0-9a-zA-Z]{6}_bot", button)
                    if search:
                        await conv.ask(button)
                        break
                else:
                    return logging.error("Нет созданного sh1t-ub бота")

            response = await conv.get_response()
            search = re.search(r"\d{1,}:[0-9a-zA-Z_-]{35}", response.text)

            logger.success("Бот успешно сброшен")
            return search.group(0)
