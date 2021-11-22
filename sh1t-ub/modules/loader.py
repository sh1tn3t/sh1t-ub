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

import os
import sys

import atexit
import requests
import tempfile

from git import Repo
from pyrogram import Client, types

from .. import loader, utils, database


class LoaderMod(loader.Module):
    """Загрузчик модулей"""

    strings = {"name": "Loader"}

    async def init(self, db: database.Database):
        self.db = db

    async def dlmod_cmd(self, app: Client, message: types.Message, args: str):
        """Загрузить модуль по ссылке"""
        if not args:
            return await utils.answer(
                message, "Нет ссылки на модуль")

        try:
            r = await utils.run_sync(requests.get, args)
            if not (module_name := await self.all_modules.load_module(r.text, r.url)):
                return await utils.answer(
                    message, "Не удалось загрузить модуль")
        except requests.exceptions.ConnectionError:
            return await utils.answer(
                message, "Модуль недоступен по ссылке")

        self.db.set("sh1t-ub.loader", "modules",
                    list(set(self.db.get("sh1t-ub.loader", "modules", []) + [args])))
        return await utils.answer(
            message, f"Модуль \"{module_name}\" загружен")

    async def loadmod_cmd(self, app: Client, message: types.Message):
        """Загрузить модуль по файлу"""
        if not (file := message if message.document else message.reply_to_message):
            return await utils.answer(
                message, "Нет реплая на файл")

        temp_file = tempfile.NamedTemporaryFile("w")
        await file.download(temp_file.name)

        try:
            module_source = open(temp_file.name, "r", encoding="utf-8").read()
        except UnicodeDecodeError:
            return await utils.answer(
                message, "Неверная кодировка файла")

        if not (module_name := await self.all_modules.load_module(module_source)):
            return await utils.answer(
                message, "Не удалось загрузить модуль")

        temp_file.close()
        return await utils.answer(
            message, f"Модуль \"{module_name}\" загружен")

    async def unloadmod_cmd(self, app: Client, message: types.Message, args: str):
        """Выгрузить модуль"""
        if not (module_name := await self.all_modules.unload_module(args)):
            return await utils.answer(
                message, "Неверное название модуля")

        return await utils.answer(
            message, f"Модуль \"{module_name}\" выгружен")

    async def restart_cmd(self, app: Client, message: types.Message):
        """Перезагрузка юзербота"""
        def restart():
            os.execl(sys.executable, sys.executable, "-m", "sh1t-ub")

        self.db.set("sh1t-ub.loader", "restart_msg",
                    f"{message.chat.id}:{message.message_id}")
        atexit.register(restart)

        await utils.answer(message, "Перезагрузка...")
        return sys.exit(0)

    async def update_cmd(self, app: Client, message: types.Message):
        """Обновление юзербота"""
        repo = Repo(".")
        origin = repo.remote("origin")
        origin.pull()

        return await self.restart_cmd(app, message)
