from pyrogram import Client, types

from .. import loader, utils



class HelpMod(loader.Module):
    """Помощь по командам юзербота"""
    strings = {"name": "Help"}

    async def init(self, app: Client):
        self.app = app

    async def help_cmd(self, app: Client, message: types.Message):
        """Список всех модулей"""
        args = utils.get_args(message.text)

        if not args:
            msg = "\n".join(
                f"{count}) <code>{command}</code>" for count, command in enumerate(self.allmodules.commands, start = 1)
            )
            return await message.edit(
                f"Доступные команды:\n\n{msg}")

        if not (description := self.allmodules.commands.get(args)):
            return await message.edit(
                "Такой команды нет")

        return await message.edit(
            f"Описание для команды {args}:\n<code>{description.__doc__}</code>")