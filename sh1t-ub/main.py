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
        f"Started for {(await app.get_me()).id} successful! Type {prefixes[0]}help in chat")

    await idle()