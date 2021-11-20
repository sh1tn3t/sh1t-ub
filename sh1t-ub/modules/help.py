from pyrogram import Client, types

from .. import loader, utils


class HelpMod(loader.Module):
    """Помощь по командам юзербота"""

    strings = {"name": "Help"}

    async def help_cmd(self, app: Client, message: types.Message, args: str):
        """Список всех модулей"""
        if not args:
            msg = "\n".join(
                f"• <b>{module.strings['name']}</b> ➜ {'<b>,</b> '.join(f'<code>{command}</code>' for command in module.commands)}"
                for module in self.all_modules.modules
            )
            return await utils.answer(
                message, f"Доступные команды SUB(sh1tn3t userbot):\n\n{msg}")

        module = list(
            filter(
                lambda m: m.strings["name"].lower() == args.lower(), self.all_modules.modules
            )
        )

        if not module:
            return await utils.answer(
                message, "Такого модуля нет")

        module = module[0]
        msg = "\n".join(
            f"➜ <code>{command}</code>\n"
            f"    ╰ {module.commands[command].__doc__ or 'Нет описания для команды'}"
            for command in module.commands
        )

        return await utils.answer(
            message, f"Описание модуля <u>{module.strings['name']}</u>:\n\n"
                     f"• {module.__doc__ or 'Нет описания для модуля'}\n"
                     f"{msg}"
        )

    async def source_cmd(self, app: Client, message: types.Message):
        """Сурсы юзербота sh1t-ub"""
        sh1tn3t_link = "https://github.com/sh1tn3t"

        return await utils.answer(
            message, f"Крутой юзербот sh1t-ub (sh1tn3t userbot)\n"
                     f"Авторы: @sh1tn3t, <a href=\"{sh1tn3t_link}\">github</a>\n\n"
                     f"Смотри исходный код тут:\n{sh1tn3t_link}/sh1t-ub"
        )