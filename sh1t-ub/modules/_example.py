#    Sh1t-UB (telegram userbot by sh1tn3t)
#    Copyright (C) 2021 Sh1tN3t

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

from pyrogram import Client, types
from lightdb import LightDB

from asyncio import sleep
from .. import loader, utils


class ExampleMod(loader.Module): # Example - название класса модуля
                                 # Mod в конце названия обязательно
    """Описание модуля"""

    strings = {"name": "Example"} # Название модуля

    async def init(self, db: LightDB): # Инициализация модуля,
                                       # обязательно, если нужно пользоваться базой данных
        self.db = db

    async def example_cmd(self, app: Client, message: types.Message, args: str): # _cmd на конце функции чтобы обозначить что это команда
                                                                                 # args - аргументы после команды. необязательный аргумент
        """Описание команды"""
        await utils.answer(
            message, "Ого пример команды" + (                                    # utils.answer - это круто
                f"\nАргументы: {args}" if args
                else ""
            )
        )

        await sleep(1)
        return await utils.answer(message, "Прошла 1 секунда!")

    @loader.on(lambda _, __, m: "тест" in m.text) # Сработает только если есть "тест" в тексте с командой
    async def example2_cmd(self, app: Client, message: types.Message):
        """Описание для второй команды с фильтрами"""
        return await utils.answer(message, "Да")

    @loader.on(lambda _, __, m: m.text == "Привет, это проверка вотчера щит-юб")
    async def watcher(self, app: Client, message: types.Message): # watcher - функция которая работает при получении нового сообщения
        return await message.reply("Привет, все работает отлично")
