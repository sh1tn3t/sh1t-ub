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

from asyncio import sleep
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from pyrogram import Client, types
from .. import loader, utils  # ".." - т.к. модули находятся в папке sh1t-ub/modules, то нам нужно на уровень выше
                              # loader, modules, bot - файлы из папки sh1t-ub


@loader.module(name="Example", author="sh1tn3t", version=1)  # name модуля ("name" обязательный аргумент, остальное — нет), author - автор, version - версия
class ExampleMod(loader.Module):  # Example - название класса модуля
                                  # Mod в конце названия обязательно
    """Описание модуля"""

    def __init__(self):
        self.test_attribute = "Это атрибут модуля"

    async def on_load(self, app: Client):  # Можно считать что это асинхронный __init__
        """Вызывается когда модуль загружен"""
        logging.info(f"Модуль {self.name} загружен")

    # Если написать в лс/чате где есть бот "ты дурак?", то он ответит
    @loader.on_bot(lambda self, app, message: message.text and message.text.lower() == "ты дурак?")  # Сработает только если текст сообщения равняется "ты дурак?"
    async def example_message_handler(self, app: Client, message: Message):  # _message_handler на конце функции чтобы обозначить что это хендлер сообщения
        """Пример хендлера сообщения"""
        return await message.reply(
            "Сам такой!")

    async def example_inline_handler(self, app: Client, inline_query: InlineQuery, args: str):  # _inline_handler на конце функции чтобы обозначить что это инлайн-команда
                                                                                                # args - аргументы после команды. необязательный аргумент
        """Пример инлайн-команды. Использование: @bot example [аргументы]"""
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=utils.random_id(),
                    title="Тайтл",
                    description="Нажми на меня!" + (
                        f" Аргументы: {args}" if args
                        else ""
                    ),
                    input_message_content=InputTextMessageContent(
                        "Текст после нажатия на кнопку"),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("Текст кнопки", callback_data="example_button_callback"))
                )
            ]
        )

    @loader.on_bot(lambda self, app, call: call.data == "example_button_callback")  # Сработает только если каллбек дата равняется "example_button_callback"
    async def example_callback_handler(self, app: Client, call: CallbackQuery):  # _callback_handler на конце функции чтобы обозначить что это каллбек-хендлер
        """Пример каллбека"""
        return await call.answer(
            "Ого пример каллбека", show_alert=True)

    async def example_cmd(self, app: Client, message: types.Message, args: str):  # _cmd на конце функции чтобы обозначить что это команда
                                                                                  # args - аргументы после команды. необязательный аргумент
        """Описание команды. Использование: example [аргументы]"""
        await utils.answer(  # utils.answer - это круто
            message, "Ого пример команды" + (
                f"\nАргументы: {args}" if args
                else ""
            )
        )

        await sleep(2.5)  # никогда не используй time.sleep, потому что это не асинхронная функция, она остановит весь юзербот
        return await utils.answer(
            message, "Прошло 2.5 секунды!")

    @loader.on(lambda _, __, m: "тест" in getattr(m, "text", ""))  # Сработает только если есть "тест" в сообщении с командой
    async def example2_cmd(self, app: Client, message: types.Message):
        """Описание для второй команды с фильтрами"""
        return await utils.answer(
            message, f"Да, {self.test_attribute = }")

    @loader.on(lambda _, __, m: m and m.text == "Привет, это проверка вотчера щит-юб")
    async def watcher(self, app: Client, message: types.Message):  # watcher - функция которая работает при получении нового сообщения
        return await message.reply(
            "Привет, все работает отлично")

    # Можно добавлять несколько вотчеров, главное чтобы функция начиналась с "watcher"
    async def watcher_(self, app: Client, message: types.Message):
        if message.text == "Привет, это проверка второго вотчера щит-юб":
            return await message.reply(
                "И тебе привет!")
