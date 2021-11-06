import asyncio
import functools

from pyrogram.types import Message as Message_
from typing import Any, List, Literal, Tuple, Union

from .__main__ import db


class Message(Message_):
    """Кастомный класс Message"""

    def get_full_command(self) -> Union[Tuple[Literal[""], Literal[""]], Tuple[str, str]]:
        self.text = str(self.text or self.caption)
        prefixes = db.get("sh1t-ub.loader", "prefixes", ["-"])

        if not (
            self.text and self.text[0] in prefixes
            and len(self.text) > 1
        ):
            return "", ""

        command, *args = self.text[1:].split(maxsplit = 1)
        return command.lower(), args[-1] if args else ""

    def get_args(self) -> str:
        return self.get_full_command()[1]

    async def answer(self, response: Union[str, Any], doc: bool = False, **kwargs) -> List[Message_]:
        """
        response - либо строка либо что-то другое
        doc - если True, то ответ будет отправлен в виде документа (если response не строка)
        kwards - параметры для отправки сообщения
        """
        messages = []

        if isinstance(response, str) and not doc:
            outputs = [
                response[i: i + 4096]
                for i in range(0, len(response), 4096)
            ]

            messages.append(
                await (self.edit if self.outgoing else self.reply)(outputs[0], **kwargs)
            )
            for output in outputs[1:]:
                messages.append(
                    await self.reply(output, **kwargs)
                )

        else:
            messages.append(
                await self.reply_document(response, **kwargs)
            )

        return messages


def run_sync(func, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(None, functools.partial(func, *args, **kwargs))