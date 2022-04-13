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
from .. import loader, utils, __version__


@loader.module(name="Help", author="sh1tn3t")
class HelpMod(loader.Module):
    """Помощь по командам юзербота"""

    async def help_cmd(self, app: Client, message: types.Message, args: str):
        """Список всех модулей"""
        if not args:
            msg = "\n".join(
                f"• <b>{module.name}</b> ➜ " + \
                    " <b>|</b> ".join(
                        f"<code>{command}</code>" for command in module.commands
                    )
                for module in self.all_modules.modules
            )
            return await utils.answer(
                message, f"🗄 Доступные модули Sh1tN3t-UserBot: <b>{len(self.all_modules.modules)}</b>\n\n"
                         f"{msg}"
            )

        if not (module := self.all_modules.get_module(args)):
            return await utils.answer(
                message, "❌ Такого модуля нет")

        prefix = self.db.get("sh1t-ub.loader", "prefixes", ["-"])[0]
        description = "\n".join(
            f"👉 <code>{prefix + command}</code>\n"
            f"    ╰ {module.commands[command].__doc__ or 'Нет описания для команды'}"
            for command in module.commands
        )

        header = (
            f"🖥 Модуль: <b>{module.name}</b>\n" + (
                f"👨🏿‍💻 Автор: <b>{module.author}</b>\n" if module.author else ""
            ) + (
                f"🔢 Версия: <b>{module.version}</b>\n" if module.version else ""
            ) + (
                f"\n📄 Описание:\n"
                f"    ╰ {module.__doc__ or 'Нет описания для модуля'}\n\n"
            )
        )

        return await utils.answer(
            message, header + description
        )

    async def source_cmd(self, app: Client, message: types.Message):
        """Сурсы юзербота sh1t-ub"""
        sh1tn3t_link = "https://github.com/sh1tn3t"

        return await utils.answer(
            message, (
                f"😎 Керемет пайдаланушы роботы sh1t-ub. Нұсқасы: <b>{__version__}</b>\n"
                f"Авторлары: @sh1tn3t, <a href=\"{sh1tn3t_link}\">github</a>\n\n"
                f"Бастапқы кодты <a href=\"{sh1tn3t_link}/sh1t-ub\"><b>мына жерден</b></a> қараңыз"
            ), disable_web_page_preview=True
        )
