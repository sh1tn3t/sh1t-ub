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

import os
import re
import sys

import atexit
import tempfile

import requests

from typing import List

from git import Repo
from git.exc import GitCommandError

from pyrogram import Client, types
from .. import loader, utils


async def get_git_raw_link(repo_url: str):
    """Получить raw ссылку на репозиторий"""
    GIT_REGEX = re.compile(
        r"^https?://github\.com((?:/[a-z0-9-]+){2})(?:/tree/([a-z0-9-]+)((?:/[a-z0-9-]+)*))?/?$",
        flags=re.IGNORECASE,
    )
    match = GIT_REGEX.search(repo_url)
    if not match:
        return False

    repo_path = match.group(1)
    branch = match.group(2)
    path = match.group(3)

    r = await utils.run_sync(requests.get, f"https://api.github.com/repos{repo_path}")
    if r.status_code != 200:
        return False

    branch = branch or r.json()["default_branch"]

    return f"https://raw.githubusercontent.com{repo_path}/{branch}{path or ''}/"


@loader.module(name="Loader", author="sh1tn3t")
class LoaderMod(loader.Module):
    """Загрузчик модулей"""

    async def dlmod_cmd(self, app: Client, message: types.Message, args: str):
        """Загрузить модуль по ссылке. Использование: dlmod <ссылка>"""
        modules_repo = self.db.get(
            "sh1t-ub.loader", "repo",
            "https://github.com/sh1tn3t/sub-modules"
        )
        api_result = await get_git_raw_link(modules_repo)
        if not api_result:
            return await utils.answer(
                message, "❌ Неверная ссылка на репозиторий. Поменяйте её с помощью: dlrepo <ссылка на репозиторий или reset>")

        raw_link = api_result
        modules = await utils.run_sync(requests.get, raw_link + "all.txt")
        if modules.status_code != 200:
            return await utils.answer(
                message, (
                    f"❌ В <a href=\"{modules_repo}\">репозитории</a> не найден файл all.txt\n"
                    f"Пример: https://github.com/sh1tn3t/sub-modules/blob/main/all.txt"
                ), disable_web_page_preview=True
            )

        modules: List[str] = modules.text.splitlines()

        if not args:
            text = (
                f"📥 Список доступных модулей с <a href=\"{modules_repo}\">репозитория</a>:\n\n" + "\n".join(
                    map("<code>{}</code>".format, modules))
            )
            return await utils.answer(
                message, text, disable_web_page_preview=True)

        error_text: str = None
        try:
            if args in modules:
                args = raw_link + args + ".py"

            r = await utils.run_sync(requests.get, args)
            if r.status_code != 200:
                raise requests.exceptions.ConnectionError

            if not (module_name := await self.all_modules.load_module(r.text, r.url)):
                error_text = "❌ Не удалось загрузить модуль. Подробности смотри в логах"
        except requests.exceptions.MissingSchema:
            error_text = "❌ Ссылка указана неверно"
        except requests.exceptions.ConnectionError:
            error_text = "❌ Модуль недоступен по ссылке"

        if error_text:
            return await utils.answer(message, error_text)

        self.db.set("sh1t-ub.loader", "modules",
                    list(set(self.db.get("sh1t-ub.loader", "modules", []) + [args])))
        return await utils.answer(
            message, f"✅ Модуль \"{module_name}\" загружен")

    async def loadmod_cmd(self, app: Client, message: types.Message):
        """Загрузить модуль по файлу. Использование: <реплай на файл>"""
        reply = message.reply_to_message
        file = (
            message
            if message.document
            else reply
            if reply and reply.document
            else None
        )

        if not file:
            return await utils.answer(
                message, "❌ Нет реплая на файл")

        temp_file = tempfile.NamedTemporaryFile("w")
        await file.download(temp_file.name)

        try:
            with open(temp_file.name, "r", encoding="utf-8") as file:
                module_source = file.read()
        except UnicodeDecodeError:
            temp_file.close()
            return await utils.answer(
                message, "❌ Неверная кодировка файла")

        if not (module_name := await self.all_modules.load_module(module_source)):
            return await utils.answer(
                message, "❌ Не удалось загрузить модуль. Подробности смотри в логах")

        temp_file.close()
        return await utils.answer(
            message, f"✅ Модуль \"{module_name}\" загружен")

    async def unloadmod_cmd(self, app: Client, message: types.Message, args: str):
        """Выгрузить модуль. Использование: unloadmod <название модуля>"""
        if not (module_name := await self.all_modules.unload_module(args)):
            return await utils.answer(
                message, "❌ Неверное название модуля")

        return await utils.answer(
            message, f"✅ Модуль \"{module_name}\" выгружен")

    async def restart_cmd(self, app: Client, message: types.Message):
        """Перезагрузка юзербота"""
        def restart():
            """Запускает загрузку юзербота"""
            os.execl(sys.executable, sys.executable, "-m", "sh1t-ub")

        self.db.set("sh1t-ub.loader", "restart_msg",
                    f"{message.chat.id}:{message.message_id}")
        atexit.register(restart)

        await utils.answer(message, "🔁 Перезагрузка...")
        return sys.exit(0)

    async def update_cmd(self, app: Client, message: types.Message):
        """Обновление юзербота"""
        await utils.answer(message, "🔃 Обновление...")

        repo = Repo(".")
        origin = repo.remote("origin")

        try:
            origin.pull()
        except GitCommandError:
            repo.git.reset("--hard")
            return await self.update_cmd(app, message)

        return await self.restart_cmd(app, message)

    async def dlrepo_cmd(self, app: Client, message: types.Message, args: str):
        """Установить репозиторий с модулями. Использование: dlrepo <ссылка на репозиторий или reset>"""
        if not args:
            return await utils.answer(
                message, "❌ Нет аргументов")

        if args == "reset":
            self.db.set(
                "sh1t-ub.loader", "repo",
                "https://github.com/sh1tn3t/sub-modules"
            )
            return await utils.answer(
                message, "✅ Ссылка на репозиторий была сброшена")

        if not await get_git_raw_link(args):
            return await utils.answer(
                message, "❌ Ссылка указана неверно")

        self.db.set("sh1t-ub.loader", "repo", args)
        return await utils.answer(
            message, "✅ Ссылка на репозиторий установлена")
