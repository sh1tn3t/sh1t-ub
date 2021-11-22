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
import asyncio

from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler

from . import loader, dispatcher, database


async def main(app: Client):
    global db

    await app.start()
    await (cloud_db := database.CloudDatabase(app)).find_data_chat()

    db = database.Database("./db.json", cloud_db)
    await (modules := loader.Modules(db)).register_all()
    dp = dispatcher.Dispatcher(modules)

    app.add_handler(
        MessageHandler(
            dp.handle_message, filters.all)
    )

    if (restart_msg := db.get("sh1t-ub.loader", "restart_msg", None)):
        msg = await app.get_messages(*list(map(int, restart_msg.split(":"))))
        if (
            not msg.empty
            and msg.text != (
                restarted_text := "Перезагрузка прошла успешно!")
        ):
            await msg.edit(restarted_text)

        db.pop("sh1t-ub.loader", "restart_msg")

    prefixes = db.get("sh1t-ub.loader", "prefixes", ["-"])
    logging.info(
        f"Стартовал для {(await app.get_me()).id} успешно! Введи {prefixes[0]}help в чате")

    await idle()
