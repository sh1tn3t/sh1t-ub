from lightdb import LightDB

from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler

from . import loader, dispatcher


async def main(app: Client, db: LightDB):
    await app.start()
    await (modules := loader.Modules(db)).register_all()

    dp = dispatcher.Dispatcher(modules)
    app.add_handler(MessageHandler(dp.handle_message, filters.all))

    await idle()