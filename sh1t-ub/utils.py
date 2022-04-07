#    Sh1t-UB (telegram userbot by sh1tn3t)
#    Copyright (C) 2021-2022 Sh1tN3t

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import functools

from pyrogram.types import Message, User, Chat
from pyrogram.file_id import FileId, PHOTO_TYPES

from types import FunctionType
from typing import Any, List, Literal, Tuple, Union


def get_full_command(message: Message) -> Union[
    Tuple[Literal[""], Literal[""]], Tuple[str, str]
]:
    """Вывести кортеж из команды и аргументов

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    from .main import db

    message.text = str(message.text or message.caption)
    prefixes = db.get("sh1t-ub.loader", "prefixes", ["-"])

    for prefix in prefixes:
        if (
            message.text
            and len(message.text) > len(prefix)
            and message.text.startswith(prefix)
        ):
            break
    else:
        return "", "", ""

    command, *args = message.text[len(prefix):].split(maxsplit=1)
    return prefixes[0], command.lower(), args[-1] if args else ""


async def answer(
    message: Union[Message, List[Message]],
    response: Union[str, Any],
    doc: bool = False,
    photo: bool = False,
    **kwargs
) -> List[Message]:
    """В основном это обычный message.edit, но:
        - Если содержание сообщения будет больше лимита (4096 символов),
            то отправится несколько разделённых сообщений
        - Работает message.reply, если команду вызвал не владелец аккаунта

    Параметры:
        message (``pyrogram.types.Message`` | ``typing.List[pyrogram.types.Message]``):
            Сообщение

        response (``str`` | ``typing.Any``):
            Текст или объект которое нужно отправить

        doc/photo (``bool``, *optional*):
            Если ``True``, сообщение будет отправлено как документ/фото или по ссылке

        kwargs (``dict``, *optional*):
            Параметры отправки сообщения
    """
    messages = []

    if isinstance(message, list):
        message = message[0]

    if isinstance(response, str) and all(not arg for arg in [doc, photo]):
        outputs = [
            response[i: i + 4096]
            for i in range(0, len(response), 4096)
        ]

        messages.append(
            await (
                message.edit if message.outgoing
                else message.reply
            )(outputs[0], **kwargs)
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


def run_sync(func: FunctionType, *args, **kwargs):
    """Запускает асинхронно любую нон-асинк функцию

    Параметры:
        func (``types.FunctionType``):
            Функция для запуска

        args (``str``):
            Аргументы к функции

        kwargs (``dict``):
            Параметры к функции
    """
    return asyncio.get_event_loop().run_in_executor(
        None, functools.partial(
            func, *args, **kwargs)
    )


def get_message_media(message: Message):
    """Получить медиа с сообщения, если есть

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    return getattr(message, message.media or "", None)


def get_media_ext(message: Message):
    """Получить расширение файла

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    if not message.media:
        raise ValueError("В сообщении нет медиа")

    media = get_message_media(message)
    media_mime_type = getattr(media, "mime_type", "")
    extension = message._client.mimetypes \
        .guess_extension(media_mime_type)

    if not extension:
        extension = ".unknown"
        file_type = FileId.decode(
            media.file_id).file_type

        if file_type in PHOTO_TYPES:
            extension = ".jpg"

    return extension


def get_display_name(entity: Union[User, Chat]):
    """Получить отображаемое имя

    Параметры:
        entity (``pyrogram.types.User`` | ``pyrogram.types.Chat``):
            Сущность, для которой нужно получить отображаемое имя
    """
    if isinstance(entity, User):
        return entity.first_name + (
            " " + entity.last_name
            if entity.last_name else ""
        )

    elif isinstance(entity, Chat):
        return entity.title
