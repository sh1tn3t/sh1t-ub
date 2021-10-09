from pyrogram import Client, types, filters

from .. import loader
from ..misc import app



class testMod(loader.Module):
    strings = {"name": "test"}

    async def init(self, app: Client):
        self.app = app

    @app.on_message(filters.command("test", ".") & filters.me)
    async def testcmd(app: Client, message: types.Message):
        """Описание"""
        return await message.reply("ТЕСТ СМД", )

    async def fuck_cmd(self, app: Client, message: types.Message):
        """хваъзхваыпзхфывапщзЩЗХЪЩЗыпфвапшщываршщз"""
        return await message.reply("все клево")