import os
import sys

import atexit
import requests
import tempfile

from git import Repo
from pyrogram import Client, types
from lightdb import LightDB

from .. import loader, utils


class LoaderMod(loader.Module):
    """Загрузчик модулей"""

    strings = {"name": "Loader"}

    async def init(self, db: LightDB):
        self.db = db

    async def dlmod_cmd(self, app: Client, message: types.Message):
        """Загрузить модуль по ссылке"""
        args = message.get_args()
        if not args:
            return await message.answer(
                "Нет ссылки на модуль")

        try:
            r = await utils.run_sync(requests.get, args)
            if not (module_name := await self.all_modules.load_module(r.text, r.url)):
                return await message.answer(
                    "Не удалось загрузить модуль")
        except requests.exceptions.ConnectionError:
            return await message.answer(
                "Модуль недоступен по ссылке")

        self.db.set("sh1t-ub.loader", "modules", list(set(self.db.get("sh1t-ub.loader", "modules", []) + [args])))
        return await message.answer(
            f"Модуль \"{module_name}\" загружен")

    async def loadmod_cmd(self, app: Client, message: types.Message):
        """Загрузить модуль по файлу"""
        if not (file := message if message.document else message.reply_to_message):
            return await message.answer(
                "Нет реплая на файл")

        temp_file = tempfile.NamedTemporaryFile("w", delete = True)
        await file.download(temp_file.name)

        try:
            module_source = open(temp_file.name, "r", encoding = "utf-8").read()
        except UnicodeDecodeError:
            return await message.answer(
                "Неверная кодировка файла")

        if not (module_name := await self.all_modules.load_module(module_source)):
            return await message.answer(
                "Не удалось загрузить модуль")

        temp_file.close()
        return await message.answer(
            f"Модуль \"{module_name}\" загружен")

    async def unloadmod_cmd(self, app: Client, message: types.Message):
        """Выгрузить модуль"""
        args = message.get_args()
        if not (module_name := await self.all_modules.unload_module(args)):
            return await message.answer(
                "Неверное название модуля")

        return await message.answer(
            f"Модуль \"{module_name}\" выгружен")

    async def restart_cmd(self, app: Client, message: types.Message):
        """Перезагрузка юзербота"""
        def restart():
            os.execl(sys.executable, sys.executable, "-m", "sh1t-ub")

        self.db.set("sh1t-ub.loader", "restart_msg", f"{message.chat.id}:{message.message_id}")
        atexit.register(restart)

        await message.answer("Перезагрузка...")
        return sys.exit(0)

    async def update_cmd(self, app: Client, message: types.Message):
        """Обновление юзербота"""
        repo = Repo(".")
        origin = repo.remote("origin")
        origin.pull()

        return await self.restart_cmd(app, message)