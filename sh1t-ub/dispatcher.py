import logging

from pyrogram import Client, filters, types

from .loader import Modules
from .utils import get_full_command



class Dispatcher:
    def __init__(self, modules: Modules):
        self.modules = modules

    async def handle_message(self, app: Client, message: types.Message):
        await self.handle_watcher(app, message)
        await self.handle_other_handlers(app, message)

        if not message.outgoing:
            return

        command, args = get_full_command(message)
        if not (command or args):
            return

        aliases = self.modules.db.get("aliases", {})
        command = aliases.get(command, command)

        func = self.modules.commands.get(command.lower())
        if not func:
            return

        try:
            await func(app, message)
        except Exception as error:
            await message.reply(f"Ошибка: {error}")
            raise error

    async def handle_watcher(self, app: Client, message: types.Message):
        for watcher in self.modules.watchers:
            try:
                await watcher(app, message)
            except Exception as error:
                logging.error(f"Произошла ошибка при выполнении watcher. Ошибка: {error}")

    async def handle_other_handlers(self, app: Client, message: types.Message):
        for handler in app.dispatcher.groups[0]:
            if (
                getattr(handler.callback, "__func__", None) == Dispatcher.handle_message
                or not await handler.filters(app, message)
            ):
                continue

            try:
                await handler.callback(app, message)
            except Exception as error:
                logging.error(f"Произошла ошибка при выполнении обработчика. Ошибка: {error}")