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

        command, args = get_full_command(str(message.text)) # Потому что сука нахуя делать https://my.fl1yd.su/pics/ZCO1j.png,
                                                            # pyrogram/types/messages_and_media/message.py, 54-55 строка
                                                            # из-за этого ошибки UnicodeDecodeError
        if not (command or args):
            return

        if not (func_cmd := self.modules.commands.get(command.lower())):
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