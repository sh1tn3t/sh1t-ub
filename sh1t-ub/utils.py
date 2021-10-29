import asyncio
import functools

from pyrogram.types import Message
from typing import Any, List, Literal, Tuple, Union

from .misc import db



def get_full_command(message: Message) -> Union[Tuple[Literal[""], Literal[""]], Tuple[str, str]]:
    message.text = str(message.text or message.caption)
    prefixes = db.get("prefixes", [","])

    if not (
            message.text and message.text[0] in prefixes
            and len(message.text) > 1
    ):
        return "", ""

    command, *args = message.text[1:].split(maxsplit = 1)
    args = args[-1] if args else ""
    return command.lower(), args


def get_args(message: Message) -> str:
    return get_full_command(message)[1]


def run_sync(func, *args, **kwargs):
	return asyncio.get_event_loop().run_in_executor(None, functools.partial(func, *args, **kwargs))


async def answer(message: Message, response: Union[str, Any], **kwargs) -> List[Message]:
    messages = []

    if isinstance(response, str):
        outputs = [
            response[i: i + 4096]
            for i in range(0, len(response), 4096)
        ]

        msg = await (message.edit if message.outgoing else message.reply)(outputs[0], **kwargs)
        messages.append(msg)
        for output in outputs[1:]:
            msg = await message.reply(output, **kwargs)
            messages.append(msg)

    else:
        msg = await message.reply_document(response, **kwargs)
        messages.append(msg)

    return messages