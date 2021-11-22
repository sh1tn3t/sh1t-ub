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

from pyrogram import Client, types
from datetime import datetime

from .. import loader, utils


class TesterMod(loader.Module):
    """Тест чего-то"""

    strings = {"name": "Tester"}

    async def ping_cmd(self, app: Client, message: types.Message, args: str):
        """Пингует"""
        count = 5
        ping_msg, ping_data = [], []

        if args and args.isdigit():
            count = int(args)

        for _ in range(count):
            start = datetime.now()
            msg = await app.send_message("me", "ping?")
            ms = (datetime.now() - start).microseconds / 1000

            ping_data.append(ms)
            ping_msg.append(msg)

        ping = sum(ping_data) / len(ping_data)

        await utils.answer(message, f"[ok] {str(ping)[:5]}ms")
        for msg in ping_msg:
            await msg.delete()

        return
