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

import re

import logging
import asyncio

import inspect

import html
import string
import random

from loguru import logger

from aiogram import Bot, Dispatcher, exceptions
from aiogram.types import (
    Message,
    InlineQuery,
    CallbackQuery,
    InputTextMessageContent,
    InlineQueryResultArticle
)

from types import FunctionType
from typing import Union

from pyrogram import Client, errors
from . import loader, database, utils, fsm, __version__


def result_id(size: int = 10) -> str:
    """Возвращает идентификатор для результата"""
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(size)
    )


class BotManager:
    """Менеджер бота"""

    def __init__(
        self,
        app: Client,
        db: database.Database,
        all_modules: "loader.ModulesManager"
    ) -> None:
        """Инициализация класса

        Параметры:
            app (``pyrogram.Client``):
                Клиент

            db (``database.Database``):
                База данных

            all_modules (``loader.Modules``):
                Модули
        """
        self._app = app
        self._db = db
        self._all_modules = all_modules

        self._token = self._db.get("sh1t-ub.inline", "token", None)

    async def _check_filters(
        self,
        func: FunctionType,
        module: "loader.Module",
        update_type: Union[Message, InlineQuery, CallbackQuery],
    ) -> bool:
        """Проверка фильтров"""
        if (filters := getattr(func, "_filters", None)):
            coro = filters(module, self._app, update_type)
            if inspect.iscoroutine(coro):
                coro = await coro

            if not coro:
                return False
        else:
            if update_type.from_user.id != self._all_modules.me.id:
                return False

        return True

    async def load(self) -> bool:
        """Загружает менеджер бота"""
        logging.info("Загрузка менеджера бота...")

        if not self._token:
            self._token = await self._create_bot()
            if self._token is False:
                return False

            self._db.set("sh1t-ub.inline", "token", self._token)

        try:
            self.bot = Bot(self._token, parse_mode="html")
        except (exceptions.ValidationError, exceptions.Unauthorized):
            logging.error("Неверный токен. Попытка создать новый токен...")
            result = await self._revoke_token()
            if not result:
                self._token = await self._create_bot()
                if not self._token:
                    return

                self._db.set("sh1t-ub.inline", "token", self._token)
                return await self.load()

        self._dp = Dispatcher(self.bot)

        self._dp.register_inline_handler(
            self._inline_handler, lambda _: True
        )
        self._dp.register_callback_query_handler(
            self._callback_handler, lambda _: True
        )

        asyncio.ensure_future(
            self._dp.start_polling())

        logging.info("Менеджер бота успешно загружен")
        return True

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
                logging.error("Произошла ошибка при создании бота")
                return False

            await conv.ask(f"Sh1tN3t UserBot of {utils.get_display_name(self._all_modules.me)[:45]}")
            await conv.get_response()

            bot_username = f"sh1tub_{result_id(6)}_bot"

            await conv.ask(bot_username)
            response = await conv.get_response()

            search = re.search(r"(?<=<code>)(.*?)(?=</code>)", response.text.html)
            if not search:
                return logging.error("Произошла ошибка при создании бота")

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

    async def _inline_handler(self, inline_query: InlineQuery) -> InlineQuery:
        """Обработчик инлайн-хендеров"""
        if not (query := inline_query.query):
            commands = ""
            for command, func in self._all_modules.inline_handlers.items():
                if await self._check_filters(func, func.__self__, inline_query):
                    commands += f"\n💬 <code>@{(await self.bot.me).username} {command}</code>"

            message = InputTextMessageContent(
                f"👇 <b>Доступные команды</b>\n"
                f"{commands}"
            )

            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=result_id(),
                        title="Доступные команды",
                        input_message_content=message,
                        thumb_url="https://api.fl1yd.su/emoji/1f4ac.png",
                    )
                ], cache_time=0
            )

        query_ = query.split()

        cmd = query_[0]
        args = " ".join(query_[1:])

        func = self._all_modules.inline_handlers.get(cmd)
        if not func:
            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=result_id(),
                        title="Ошибка",
                        input_message_content=InputTextMessageContent(
                            "❌ Такой инлайн-команды нет"),
                        thumb_url="https://api.fl1yd.su/emoji/274c.png"
                    )
                ], cache_time=0
            )

        if not await self._check_filters(func, func.__self__, inline_query):
            return

        try:
            if (
                len(vars_ := inspect.getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(self._app, inline_query, args)
            else:
                await func(self._app, inline_query)
        except Exception as error:
            logging.exception(error)

        return inline_query

    async def _callback_handler(self, call: CallbackQuery) -> CallbackQuery:
        """Обработчик каллбек-хендлеров"""
        for func in self._all_modules.callback_handlers.values():
            if not await self._check_filters(func, func.__self__, call):
                continue
            try:
                await func(self._app, call)
            except Exception as error:
                logging.exception(error)

        return call
