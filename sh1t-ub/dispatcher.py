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

import logging
import inspect

from pyrogram import Client, types
from . import loader, utils


class Dispatcher:
    """Диспетчер сообщений"""

    def __init__(self, modules: loader.Modules):
        self.modules = modules

    async def handle_message(self, app: Client, message: types.Message):
        """Обработчик сообщений"""
        await self.handle_watchers(app, message)
        await self.handle_other_handlers(app, message)

        command, args = utils.get_full_command(message)
        if not (command or args):
            return

        command = self.modules.aliases.get(command, command)
        func = self.modules.commands.get(command.lower())
        if not func:
            return

        if not check_filter(func, app, message):
            return

        try:
            if (
                len(vars_ := inspect.getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(app, message, utils.get_full_command(message)[1])
            else:
                await func(app, message)
        except Exception as error:
            await message.reply(
                f"Ошибка: {error}")
            raise error

        return True

    async def handle_watchers(self, app: Client, message: types.Message):
        """Обработчик вотчеров"""
        for watcher in self.modules.watchers:
            try:
                if not check_filter(watcher, app, message):
                    continue

                await watcher(app, message)
            except Exception as error:
                logging.error(
                    f"Произошла ошибка при выполнении watcher. Ошибка: {error}")

        return True

    async def handle_other_handlers(self, app: Client, message: types.Message):
        """Обработчик других хендлеров"""
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


def check_filter(func, app: Client, message: types.Message):
    """Проверка фильтров"""
    if (filter_ := getattr(func, "filter", None)):
        if not filter_(app, message):
            return False
    else:
        if not message.outgoing:
            return False

    return True
