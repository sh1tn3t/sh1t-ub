from pyrogram import Client, types
from lightdb import LightDB

from .. import loader, utils



class SettingsMod(loader.Module):
    """Настройки бота"""

    strings = {"name": "Settings"}

    async def init(self, db: LightDB):
        self.db = db

    async def setprefix_cmd(self, app: Client, message: types.Message):
        """Изменить префикс, можно несколько штук"""

        args = list(utils.get_args(message))
        if not args:
            return await utils.answer(
                message, "На какой префикс нужно изменить?")

        self.db.set("prefixes", args)
        return await utils.answer(
            message, f"Префикс был изменен на {', '.join(f'<code>{prefix}</code>' for prefix in args)}")

    async def addalias_cmd(self, app: Client, message: types.Message):
        """Добавить алиас. Использование: addalias <новый алиас> <команда>"""

        args = utils.get_args(message).lower().split(maxsplit = 1)
        if not args:
            return await utils.answer(
                message, "Какой алиас нужно добавить?")

        aliases = self.db.get("aliases", {})
        if args[0] in aliases:
            return await utils.answer(
                message, "Такой алиас уже существует")

        if not self.all_modules.commands.get(args[1]):
            return await utils.answer(
                message, "Такой команды нет")

        aliases[args[0]] = args[1]
        self.db.set("aliases", aliases)

        return await utils.answer(
            message, f"Алиас {args[0]} для команды {args[1]} был добавлен")

    async def delalias_cmd(self, app: Client, message: types.Message):
        """Удалить алиас. Использование: delalias <алиас>"""

        args = utils.get_args(message).lower()
        if not args:
            return await utils.answer(
                message, "Какой алиас нужно удалить?")

        aliases = self.db.get("aliases", {})
        if args not in aliases:
            return await utils.answer(
                message, "Такого алиаса нет")

        del aliases[args]
        self.db.set("aliases", aliases)

        return await utils.answer(
            message, f"Алиас {args} был удален")

    async def aliases_cmd(self, app: Client, message: types.Message):
        """Показать все алиасы"""

        aliases = self.db.get("aliases", {})
        if not aliases:
            return await utils.answer(
                message, "Алиасов нет")

        return await utils.answer(
            message, "Список всех алиасов:\n" + "\n".join(
                f"• <code>{alias}</code> ➜ {command}"
                for alias, command in aliases.items()
            )
        )