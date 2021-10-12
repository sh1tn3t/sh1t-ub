from pyrogram import Client, types, filters

from ..dispatcher import Dispatcher

from .. import loader
from ..misc import app



class testMod(loader.Module):
    strings = {"name": "test"}

    # @app.on_message(filters.command("test", ".") & filters.me)
    async def test_cmd(self, app: Client, message: types.Message):
        """Описание"""
        return await message.reply("ТЕСТ СМД", )

    async def r_cmd(self, app: Client, message: types.Message):
        """хваъзхваыпзхфывапщзЩЗХЪЩЗыпфвапшщываршщз"""
        return await message.reply("все клево")
    
    async def watcher(self, app: Client, message: types.Message):
        """Проверка на приветствие"""
        if message.text == "Привет хуй":
            await app.send_message(message.chat.id, "Привет как дела", reply_to_message_id=message.message_id)
            # await message.reply("Привет, мой друг!")

    async def restart_cmd(self, app: Client, message: types.Message):
        """хвзкхаа"""
        await message.edit("Перезагрузка...")
        await self.allmodules.restart()
        return await message.edit("Все модули были перезагружены успешно!")