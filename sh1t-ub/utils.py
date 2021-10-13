from pyrogram.types import Message

from .misc import db



def get_full_command(message: Message):
    message.text = str(message.text)
    prefixes = db.get("prefixes", [","])

    if not (message.text and message.text[0] in prefixes):
        return "", ""

    command, *args = message.text[1:].split(maxsplit = 1) # [1:] для того, чтобы не брать префикс
    args = args[-1] if args else ""
    return command, args


def get_args(message: Message):
    return get_full_command(message)[1]