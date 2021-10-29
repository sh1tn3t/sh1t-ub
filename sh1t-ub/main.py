from lightdb import LightDB

from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler

from . import loader, dispatcher


async def main(app: Client, db: LightDB):
    await app.start()
    await (modules := loader.Modules(db)).register_all()

    dp = dispatcher.Dispatcher(modules)
    app.add_handler(MessageHandler(dp.handle_message, filters.all))

    if (restart_msg := db.get("restart_msg")):
        msg = await app.get_messages(*list(map(int, restart_msg.split(":"))))
        if not msg.empty and msg.text != (restarted_text := "Перезагрузка прошла успешно!"):
            await msg.edit(restarted_text)

        db.pop("restart_msg")

    await idle()