from pyrogram import Client, types
from typing import Union


class CloudDatabase:
    def __init__(self, app: Client):
        self.app = app
        self.me = None
        self.data_chat = None

    async def find_data_chat(self):
        self.me = await self.app.get_me()
        if not self.data_chat:
            chat = [
                dialog.chat async for dialog in self.app.iter_dialogs()
                if dialog.chat.title == f"sh1t-{self.me.id}-data" and dialog.chat.type == "supergroup"
            ]

            if not chat:
                self.data_chat = await self.app.create_supergroup(f"sh1t-{self.me.id}-data")
            else:
                self.data_chat = chat[0]

        return self.data_chat

    async def save_data(self, message: Union[types.Message, str]):
        return (
            await self.app.send_message(
                self.data_chat.id, message
            )
            if isinstance(message, str)
            else await message.copy(self.data_chat.id)
           )

    async def get_data(self, message_id: int):
        return await self.app.get_messages(
            self.data_chat.id, message_id
        )