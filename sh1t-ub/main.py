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

from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.session.session import Session
from pyrogram.methods.utilities.idle import idle

from . import auth, database, loader, dispatcher

Session.notice_displayed = True
db: database.Database = None


async def main():
    """Основной цикл юзербота"""
    app = await auth.Auth().authorize()
    await app.initialize()

    global db

    db = database.Database("./db.json", app)
    modules = loader.Modules(db)
    dp = dispatcher.Dispatcher(modules)

    app.add_handler(
        MessageHandler(
            dp.handle_message, filters.all)
    )

    if (restart_msg := db.get("sh1t-ub.loader", "restart_msg")):
        msg = await app.get_messages(*map(int, restart_msg.split(":")))
        if (
            not msg.empty
            and msg.text != (
                restarted_text := "Перезагрузка прошла успешно!")
        ):
            await msg.edit(restarted_text)

        db.pop("sh1t-ub.loader", "restart_msg")

    prefixes = db.get("sh1t-ub.loader", "prefixes", ["-"])
    logging.info(
        f"Стартовал для [ID: {(await app.get_me()).id}] успешно, введи {prefixes[0]}help в чате для получения списка команд"
    )

    await idle()

    logging.info("Завершение работы...")
    return True
