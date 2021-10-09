from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler

from . import loader, dispatcher


async def main(app: Client):
    await app.start()
    await (modules := loader.Modules(app)).register_all()

    dp = dispatcher.Dispatcher(modules, app)
    app.add_handler(MessageHandler(dp.handle_message, filters.me))
    app.add_handler(MessageHandler(dp.handle_watcher, filters.all))

    await idle()