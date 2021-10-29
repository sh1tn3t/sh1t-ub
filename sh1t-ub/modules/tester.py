from pyrogram import Client, types
from datetime import datetime

from .. import loader, utils



class TesterMod(loader.Module):
    """Тест чего-то"""

    strings = {"name": "Tester"}

    async def ping_cmd(self, app: Client, message: types.Message):
        """Пинг!"""
        start = datetime.now()
        await utils.answer(message, "[ok]")
        ms = (datetime.now() - start).microseconds / 1000
        return await utils.answer(
                message, f"[ok] {ms} ms.")