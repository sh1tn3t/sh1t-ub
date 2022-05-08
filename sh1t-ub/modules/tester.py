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

import io
import logging

from datetime import datetime
from pyrogram import Client, types

from .. import loader, utils, logger


@loader.module(name="Tester", author="sh1tn3t")
class TesterMod(loader.Module):
    """Тест чего-то"""

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

    async def logs_cmd(self, app: Client, message: types.Message, args: str):
        """Отправляет логи. Использование: logs <уровень>"""
        lvl = 40  # ERROR

        if args and not (lvl := logger.get_valid_level(args)):
            return await utils.answer(
                message, "❌ Неверный уровень логов")

        handler = logging.getLogger().handlers[0]
        logs = ("\n".join(handler.dumps(lvl))).encode("utf-8")
        if not logs:
            return await utils.answer(
                message, f"❕ Нет логов на уровне {lvl} ({logging.getLevelName(lvl)})")

        logs = io.BytesIO(logs)
        logs.name = "sh1t-ub.log"

        await message.delete()
        return await utils.answer(
            message, logs, doc=True, quote=False,
            caption=f"📤 Sh1t-UB Логи с {lvl} ({logging.getLevelName(lvl)}) уровнем"
        )
