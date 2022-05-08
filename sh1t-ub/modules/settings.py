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

from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="Settings", author="sh1tn3t")
class SettingsMod(loader.Module):
    """Настройки бота"""

    async def setprefix_cmd(self, app: Client, message: types.Message, args: str):
        """Изменить префикс, можно несколько штук разделённые пробелом. Использование: setprefix <префикс> [префикс, ...]"""
        if not (args := args.split()):
            return await utils.answer(
                message, "❔ На какой префикс нужно изменить?")

        self.db.set("sh1t-ub.loader", "prefixes", list(set(args)))
        prefixes = ", ".join(f"<code>{prefix}</code>" for prefix in args)
        return await utils.answer(
            message, f"✅ Префикс был изменен на {prefixes}")

    async def addalias_cmd(self, app: Client, message: types.Message, args: str):
        """Добавить алиас. Использование: addalias <новый алиас> <команда>"""
        if not (args := args.lower().split(maxsplit=1)):
            return await utils.answer(
                message, "❔ Какой алиас нужно добавить?")

        if len(args) != 2:
            return await utils.answer(
                message, "❌ Неверно указаны аргументы."
                         "✅ Правильно: addalias <новый алиас> <команда>"
            )

        aliases = self.all_modules.aliases
        if args[0] in aliases:
            return await utils.answer(
                message, "❌ Такой алиас уже существует")

        if not self.all_modules.command_handlers.get(args[1]):
            return await utils.answer(
                message, "❌ Такой команды нет")

        aliases[args[0]] = args[1]
        self.db.set("sh1t-ub.loader", "aliases", aliases)

        return await utils.answer(
            message, f"✅ Алиас <code>{args[0]}</code> для команды <code>{args[1]}</code> был добавлен")

    async def delalias_cmd(self, app: Client, message: types.Message, args: str):
        """Удалить алиас. Использование: delalias <алиас>"""
        if not (args := args.lower()):
            return await utils.answer(
                message, "❔ Какой алиас нужно удалить?")

        aliases = self.all_modules.aliases
        if args not in aliases:
            return await utils.answer(
                message, "❌ Такого алиаса нет")

        del aliases[args]
        self.db.set("sh1t-ub.loader", "aliases", aliases)

        return await utils.answer(
            message, f"✅ Алиас <code>{args}</code> был удален")

    async def aliases_cmd(self, app: Client, message: types.Message):
        """Показать все алиасы"""
        aliases = self.all_modules.aliases
        if not aliases:
            return await utils.answer(
                message, "Алиасов нет")

        return await utils.answer(
            message, "🗄 Список всех алиасов:\n" + "\n".join(
                f"• <code>{alias}</code> ➜ {command}"
                for alias, command in aliases.items()
            )
        )
