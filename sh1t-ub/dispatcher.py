import logging
import inspect

from pyrogram import Client, types
from . import loader, utils


class Dispatcher:
    def __init__(self, modules: loader.Modules):
        self.modules = modules

    async def handle_message(self, app: Client, message: types.Message):
        await self.handle_watchers(app, message)
        await self.handle_other_handlers(app, message)

        command, args = utils.get_full_command(message)
        if not (command or args):
            return

        command = self.modules.aliases.get(command, command)
        func = self.modules.commands.get(command.lower())
        if not func:
            return

        if not await check_filter(func, app, message):
            return

        try:
            if (
                len(vars_ := inspect.getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(app, message, utils.get_args(message))
            else:
                await func(app, message)
        except Exception as error:
            await message.reply(
                f"Ошибка: {error}")
            raise error

        return True

    async def handle_watchers(self, app: Client, message: types.Message):
        for watcher in self.modules.watchers:
            try:
                if not await check_filter(watcher, app, message):
                    continue

                await watcher(app, message)
            except Exception as error:
                logging.error(
                    f"Произошла ошибка при выполнении watcher. Ошибка: {error}")

        return True

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
                logging.error(
                    f"Произошла ошибка при выполнении обработчика. Ошибка: {error}")

        return True

async def check_filter(func, app: Client, message: types.Message):
    if (filter_ := getattr(func, "filter", None)):
        if not filter_(app, message):
            return False
    else:
        if not message.outgoing:
            return False

    return True