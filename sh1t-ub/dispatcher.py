import logging

from pyrogram import Client, types

from .loader import Modules
from .utils import get_full_command


class Dispatcher:
    def __init__(self, modules: Modules, app: Client):
        self.modules = modules
        self.app = app

    async def handle_message(self, app: Client, message: types.Message):
        command, args = get_full_command(message.text)
        if not (command or args):
            return

        if not (func_cmd := self.modules.commands.get(command.lower())):
            return

        try:
            await func_cmd(app, message)
        except Exception as error:
            try:
                await message.reply(f"Ошибка: {error}")
            finally:
                raise error

    async def handle_watcher(self, app: Client, message: types.Message):
        for watcher in self.modules.watchers:
            try:
                await watcher(app, message)
            except Exception as error:
                logging.error(f"Произошла ошибка при выполнении watcher. Ошибка: {error}")