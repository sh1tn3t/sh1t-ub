from pyrogram import Client, types

from .. import loader, utils



class HelpMod(loader.Module):
    """Помощь по командам юзербота"""
    strings = {"name": "Help"}

    async def help_cmd(self, app: Client, message: types.Message):
        """Список всех модулей"""
        args = utils.get_args(message)

        if not args:
            msg = "\n".join(
                f"• <b>{module.strings['name']}</b> ➜ {'<b>,</b> '.join(f'<code>{command}</code>' for command in module.commands)}"
                for module in self.allmodules.modules
            )
            return await message.edit(
                f"Доступные команды Sh1t-UB:\n\n{msg}")

        module = [
            module for module in self.allmodules.modules
            if module.strings["name"].lower() == args.lower()
        ]

        if not module:
            return await message.edit(
                "Такого модуля нет")

        [module] = module
        msg = "\n".join(
            f"➜ <code>{command}</code>\n"
            f"    ╰ {module.commands[command].__doc__ or 'Нет описания для команды'}"
            for command in module.commands
        )

        return await message.edit(
            f"Описание модуля <u>{module.strings['name']}</u>:\n\n"
            f"• {module.__doc__ or 'Нет описания для модуля'}\n"
            f"{msg}"
        )