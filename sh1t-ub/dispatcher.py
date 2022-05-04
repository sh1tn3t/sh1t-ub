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

import logging

from inspect import getfullargspec, iscoroutine

from pyrogram import Client, types
from . import loader, utils


async def check_filters(func, app: Client, message: types.Message) -> bool:
    """Проверка фильтров"""
    if (filters := getattr(func, "filters", None)):
        coro = filters(app, message)
        if iscoroutine(coro):
            coro = await coro

        if not coro:
            return False
    else:
        if not message.outgoing:
            return False

    return True


class Dispatcher:
    """Диспетчер сообщений"""

    def __init__(self, modules: loader.Modules) -> None:
        self._modules = modules

    async def _handle_message(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик сообщений"""
        await self._handle_watchers(app, message)
        await self._handle_other_handlers(app, message)

        prefix, command, args = utils.get_full_command(message)
        if not (command or args):
            return

        command = self._modules._aliases.get(command, command)
        func = self._modules.commands.get(command.lower())
        if not func:
            return

        if not await check_filters(func, app, message):
            return

        try:
            if (
                len(vars_ := getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(app, message, utils.get_full_command(message)[2])
            else:
                await func(app, message)
        except Exception as error:
            logging.exception(error)
            await utils.answer(
                message, f"❌ Произошла ошибка при выполнении команды.\n"
                         f"Запрос был: <code>{message.text}</code>\n"
                         f"Подробности можно найти в <code>{prefix}logs</code>"
            )

        return message

    async def _handle_watchers(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик вотчеров"""
        for watcher in self._modules.watchers:
            try:
                if not await check_filters(watcher, app, message):
                    continue

                await watcher(app, message)
            except Exception as error:
                logging.exception(error)

        return message

    async def _handle_other_handlers(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик других хендлеров"""
        for handler in app.dispatcher.groups[0]:
            if getattr(handler.callback, "__func__", None) == Dispatcher._handle_message:
                continue

            coro = handler.filters(app, message)
            if iscoroutine(coro):
                coro = await coro

            if not coro:
                continue

            try:
                handler = handler.callback(app, message)
                if iscoroutine(handler):
                    await handler
            except Exception as error:
                logging.exception(error)

        return message
