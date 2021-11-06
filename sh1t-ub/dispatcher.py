import logging

from pyrogram import Client, types
from . import loader, utils


class Dispatcher:
    def __init__(self, modules: loader.Modules):
        self.modules = modules

    async def handle_message(self, app: Client, message: types.Message):
        m = message.__dict__ # Кто найдет альтернативу тот молодец
        m["client"] = m.pop("_client")
        message = utils.Message(**m)

        await self.handle_watchers(app, message)
        await self.handle_other_handlers(app, message)

        command, args = message.get_full_command()
        if not (command or args):
            return

        command = self.modules.aliases.get(command, command)
        func = self.modules.commands.get(command.lower())
        if not func:
            return

        if not check_filter(func, app, message):
            return

        try:
            await func(app, message)
        except Exception as error:
            await message.reply(
                f"Ошибка: {error}")
            raise error

    async def handle_watchers(self, app: Client, message: utils.Message):
        for watcher in self.modules.watchers:
            try:
                if not check_filter(watcher, app, message):
                    continue

                await watcher(app, message)
            except Exception as error:
                logging.error(
                    f"Произошла ошибка при выполнении watcher. Ошибка: {error}")

    async def handle_other_handlers(self, app: Client, message: utils.Message):
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


def check_filter(func, app: Client, message: utils.Message):
    filter = getattr(func, "filter", None)
    if filter:
        if not filter(app, message):
            return False
    else:
        if not message.outgoing:
            return False

    return True