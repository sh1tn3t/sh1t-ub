import traceback
import html

from pyrogram import Client, types
from meval import meval

from .. import loader, utils



class EvaluatorMod(loader.Module):
    """
    Выполняет python-код
    """
    strings = {"name": "Evaluator"}

    async def init(self, app: Client):
        self.app = app

    async def x_cmd(self, app: Client, message: types.Message):
        """Выполнить python-код"""
        return await self.execute(message)

    async def e_cmd(self, app: Client, message: types.Message):
        """Выполнить python-код и возвратить результат"""
        return await self.execute(message, True)

    async def execute(self, message: types.Message, return_it: bool = False):
        try:
            args = utils.get_args(message.text)
            result = html.escape(
                str(
                    await meval(args, globals(), **await self.getattrs(message)))
            )
            output = (
                f"<b>Выполненное выражение:</b>\n"
                f"<code>{args}</code>\n\n"
                f"<b>Возвращено:</b>\n"
                f"<code>{result}"
            )
            out = [output[i: i + 4083] for i in range(0, len(output), 4083)]
        except Exception:
            return await message.edit(
                f"<b>Не удалось выполнить:</b>\n"
                f"<code>{args}</code>\n\n"
                f"<b>Ошибка:</b>\n"
                f"<code>{traceback.format_exc(0, True)}</code>"
            )

        if return_it:
            await message.edit(
                f"{out[0]}</code>")
            for part in out[1:]:
                await message.reply(
                    f"<code>{part}</code>")

    async def getattrs(self, message: types.Message):
        return {
            "self": self,
            "reply": message.reply_to_message,
            "message": message,
            "app": self.app,
            "chat": message.chat,
            "user": message.from_user,
            "ruser": message.reply_to_message.from_user if message.reply_to_message else None
        }