import asyncio
import functools

from pyrogram.types import Message
from pyrogram.file_id import FileId, PHOTO_TYPES
from pyrogram.mime_types import mime_types

from io import StringIO
from mimetypes import MimeTypes
from typing import Any, List, Literal, Tuple, Union


def get_full_command(message: Message) -> Union[Tuple[Literal[""], Literal[""]], Tuple[str, str]]:
    from .main import db

    message.text = str(message.text or message.caption)
    prefixes = db.get("sh1t-ub.loader", "prefixes", ["-"])

    if not (
        message.text and message.text[0] in prefixes
        and len(message.text) > 1
    ):
        return "", ""

    command, *args = message.text[1:].split(maxsplit = 1)
    return command.lower(), args[-1] if args else ""


def get_args(message: Message) -> str:
    return get_full_command(message)[1]


async def answer(message: Message, response: Union[str, Any], doc: bool = False, photo: bool = False, **kwargs) -> List[Message]:
    """
    response - либо строка либо что-то другое
    doc - если True, то ответ будет отправлен в виде документа (если response не строка)
    kwards - параметры для отправки сообщения
    """
    messages = []

    if isinstance(message, list):
        message = message[0]

    if isinstance(response, str) and all(not el for el in [doc, photo]):
        outputs = [
            response[i: i + 4096]
            for i in range(0, len(response), 4096)
        ]

        messages.append(
            await (message.edit if message.outgoing else message.reply)(outputs[0], **kwargs)
        )
        for output in outputs[1:]:
            messages.append(
                await message.reply(output, **kwargs)
            )

    elif doc:
        messages.append(
            await message.reply_document(response, **kwargs)
        )

    elif photo:
        messages.append(
            await message.reply_photo(response, **kwargs)
        )

    return messages


def run_sync(func, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(None, functools.partial(func, *args, **kwargs))


def get_message_media(message: Union[Message, Any]):
    available_media = (
        "audio", "document", "photo", "sticker",
        "animation", "video", "voice", "video_note",
        "new_chat_photo", "web_page"
    )

    if isinstance(message, Message):
        for kind in available_media:
            media = getattr(message, kind, None)
            if media:
                break
        else:
            raise ValueError("Ты еблан это не медиа")
    else:
        media = message

    return media


def get_media_ext(message: Message):
    mime_type = MimeTypes() 
    mime_type.readfp(StringIO(mime_types))

    if not message.media:
        raise ValueError("В сообщении нет медиа")

    media = get_message_media(message)
    media_mime_type = getattr(media, "mime_type", "")

    extension = mime_type.guess_extension(media_mime_type)
    file_type = FileId.decode(media.file_id)

    if not extension:
        extension = ".unknown"
        if file_type in PHOTO_TYPES:
            extension = ".jpg"

    return extension




