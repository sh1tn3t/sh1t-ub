from typing import List
from .misc import db



def get_full_command(message_text: str, prefixes: List[str] = db.get("prefixes", [","])):
    if not (message_text and message_text[0] in prefixes):
        return None, None

    command, *args = message_text[1:].split(maxsplit = 1) # [1:] для того, чтобы не брать префикс
    args = args[-1] if args else ""
    return command, args


def get_args(message_text: str):
    return get_full_command(str(message_text))[1]