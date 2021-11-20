import traceback
import html

from pyrogram import Client, types
from meval import meval

from .. import loader, utils, database


class EvaluatorMod(loader.Module):
    """Выполняет python-код"""

    strings = {"name": "Evaluator"}

    async def init(self, db: database.Database):
        self.db = db

    async def exec_cmd(self, app: Client, message: types.Message, args: str):
        """Выполнить python-код"""
        return await self.execute(app, message, args)

    async def eval_cmd(self, app: Client, message: types.Message, args: str):
        """Выполнить python-код и возвратить результат"""
        return await self.execute(app, message, args, True)

    async def execute(self, app: Client, message: types.Message, args: str, return_it: bool = False):
        try:
            result = html.escape(
                str(
                    await meval(args, globals(), **await self.getattrs(app, message)))
            )
        except Exception:
            return await utils.answer(
                message, f"<b>[{'eval' if return_it else 'exec'}] Не удалось выполнить выражение:</b>\n"
                         f"<code>{args}</code>\n\n"
                         f"<b>Ошибка:</b>\n"
                         f"<code>{html.escape(traceback.format_exc(0, True))}</code>"
            )

        if return_it:
            output = (
                f"<b>[eval] Выполненное выражение:</b>\n"
                f"<code>{args}</code>\n\n"
                f"<b>Возвращено:</b>\n"
                f"<code>{result}"
            )
            outputs = [output[i: i + 4083] for i in range(0, len(output), 4083)]

            await utils.answer(message, f"{outputs[0]}</code>")
            for output in outputs[1:]:
                await message.reply(f"<code>{output}</code>")

    async def getattrs(self, app: Client, message: types.Message):
        return {
            "self": self,
            "db": self.db,
            "app": app,
            "message": message,
            "chat": message.chat,
            "user": message.from_user,
            "reply": message.reply_to_message,
            "ruser": message.reply_to_message.from_user if message.reply_to_message else None
        }