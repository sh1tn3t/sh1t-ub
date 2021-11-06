from pyrogram import Client, types
from datetime import datetime

from .. import loader


class TesterMod(loader.Module):
    """Тест чего-то"""

    strings = {"name": "Tester"}

    async def ping_cmd(self, app: Client, message: types.Message):
        """Пингует"""
        args = message.get_args()
        ping_msg, ping_data = [], []

        count = 5
        if args and args.isdigit():
            count = int(args)

        for _ in range(count):
            start = datetime.now()
            msg = await app.send_message("me", "ping")
            ms = (datetime.now() - start).microseconds / 1000

            ping_data.append(ms)
            ping_msg.append(msg)

        ping = sum(ping_data) / len(ping_data)

        await message.answer(f"[ok] {str(ping)[:5]}ms")
        for msg in ping_msg:
            await msg.delete()