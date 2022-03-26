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

from pyrogram import Client, types

from asyncio import sleep
from .. import loader, utils  # ".." - т.к. модули находятся в папке sh1t-ub/modules, то нам нужно на уровень выше
                              # loader, modules - файлы из папки sh1t-ub


@loader.module(name="Example", author="sh1tn3t", version=1)  # name модуля ("name" обязательный аргумент, остальное — нет), author - автор, version - версия
class ExampleMod(loader.Module):  # Example - название класса модуля
                                  # Mod в конце названия обязательно
    """Описание модуля"""

    def __init__(self):
        self.test_attribute = "Это атрибут модуля"

    async def example_cmd(self, app: Client, message: types.Message, args: str):  # _cmd на конце функции чтобы обозначить что это команда
                                                                                  # args - аргументы после команды. необязательный аргумент
        """Описание команды"""
        await utils.answer( # utils.answer - это круто
            message, "Ого пример команды" + (
                f"\nАргументы: {args}" if args
                else ""
            )
        )

        await sleep(2.5)  # никогда не используй time.sleep, потому что это не асинхронная функция, она остановит весь юзербот
        return await utils.answer(
            message, "Прошло 2.5 секунды!")

    @loader.on(lambda _, __, m: m and m.text and "тест" in m.text)  # Сработает только если есть "тест" в тексте с командой
    async def example2_cmd(self, app: Client, message: types.Message):
        """Описание для второй команды с фильтрами"""
        return await utils.answer(message, f"Да, {self.test_attribute = }")

    @loader.on(lambda _, __, m: m and m.text == "Привет, это проверка вотчера щит-юб")
    async def watcher(self, app: Client, message: types.Message):  # watcher - функция которая работает при получении нового сообщения
        return await message.reply("Привет, все работает отлично")

    # Можно добавлять несколько вотчеров, главное чтобы функция начиналась на "watcher" 
    async def watcher_(self, app: Client, message: types.Message):
        if message.text == "Привет, это проверка второго вотчера щит-юб":
            return await message.reply("И тебе привет!")
