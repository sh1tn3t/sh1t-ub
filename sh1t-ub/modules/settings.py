from pyrogram import Client, types

from .. import loader, utils, database


class SettingsMod(loader.Module):
    """Настройки бота"""

    strings = {"name": "Settings"}

    async def init(self, db: database.Database):
        self.db = db

    async def setprefix_cmd(self, app: Client, message: types.Message, args: str):
        """Изменить префикс, можно несколько штук"""
        args = list(message.get_args())
        if not args:
            return await utils.answer(
                message, "На какой префикс нужно изменить?")

        self.db.set("sh1t-ub.loader", "prefixes", args)
        prefixes = ", ".join(f"<code>{prefix}</code>" for prefix in args)
        return await utils.answer(
            message, f"Префикс был изменен на {prefixes}")

    async def addalias_cmd(self, app: Client, message: types.Message, args: str):
        """Добавить алиас. Использование: addalias <новый алиас> <команда>"""
        args = message.get_args().lower().split(maxsplit = 1)
        if not args:
            return await utils.answer(
                message, "Какой алиас нужно добавить?")

        if len(args) != 2:
            return await utils.answer(
                message, "Неверно указаны аргументы. Правильно: addalias <новый алиас> <команда>")

        aliases = self.db.get("sh1t-ub.loader", "aliases", {})
        if args[0] in aliases:
            return await utils.answer(
                message, "Такой алиас уже существует")

        if not self.all_modules.commands.get(args[1]):
            return await utils.answer(
                message, "Такой команды нет")

        aliases[args[0]] = args[1]
        self.db.set("sh1t-ub.loader", "aliases", aliases)

        return await utils.answer(
            message, f"Алиас {args[0]} для команды {args[1]} был добавлен")

    async def delalias_cmd(self, app: Client, message: types.Message):
        """Удалить алиас. Использование: delalias <алиас>"""
        args = message.get_args().lower()
        if not args:
            return await utils.answer(
                message, "Какой алиас нужно удалить?")

        aliases = self.db.get("sh1t-ub.loader", "aliases", {})
        if args not in aliases:
            return await utils.answer(
                message, "Такого алиаса нет")

        del aliases[args]
        self.db.set("sh1t-ub.loader", "aliases", aliases)

        return await utils.answer(
            message, f"Алиас {args} был удален")

    async def aliases_cmd(self, app: Client, message: types.Message):
        """Показать все алиасы"""
        aliases = self.db.get("sh1t-ub.loader", "aliases", {})
        if not aliases:
            return await utils.answer(
                message, "Алиасов нет")

        return await utils.answer(
            message, "Список всех алиасов:\n" + "\n".join(
                f"• <code>{alias}</code> ➜ {command}"
                for alias, command in aliases.items()
            )
        )