from pyrogram import Client, types

from .. import loader


class HelpMod(loader.Module):
    """Помощь по командам юзербота"""

    strings = {"name": "Help"}

    async def help_cmd(self, app: Client, message: types.Message):
        """Список всех модулей"""
        args = message.get_args()

        if not args:
            msg = "\n".join(
                f"• <b>{module.strings['name']}</b> ➜ {'<b>,</b> '.join(f'<code>{command}</code>' for command in module.commands)}"
                for module in self.all_modules.modules
            )
            return await message.answer(
                f"Доступные команды Sh1t-UB:\n\n{msg}")

        module = list(
            filter(
                lambda m: m.strings["name"].lower() == args.lower(), self.all_modules.modules
            )
        )

        if not module:
            return await message.answer(
                "Такого модуля нет")

        module = module[0]
        msg = "\n".join(
            f"➜ <code>{command}</code>\n"
            f"    ╰ {module.commands[command].__doc__ or 'Нет описания для команды'}"
            for command in module.commands
        )

        return await message.answer(
            f"Описание модуля <u>{module.strings['name']}</u>:\n\n"
            f"• {module.__doc__ or 'Нет описания для модуля'}\n"
            f"{msg}"
        )