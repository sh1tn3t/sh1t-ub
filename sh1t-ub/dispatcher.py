import logging

from pyrogram import Client, types, errors

from .loader import Modules
from .utils import get_full_command



class Dispatcher:
    def __init__(self, modules: Modules):
        self.modules = modules

    async def handle_message(self, app: Client, message: types.Message):
        await self.handle_watcher(app, message)

        if not message.outgoing:
            return

        command, args = get_full_command(message)
        if not (command or args):
            return

        aliases = self.modules.db.get("aliases", {})
        command = aliases.get(command, command)

        func_cmd = self.modules.commands.get(command.lower())
        if not func_cmd:
            return

        try:
            await func_cmd(app, message)
        except errors.RPCError as error:
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