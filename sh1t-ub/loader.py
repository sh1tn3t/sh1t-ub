import os
import sys
import asyncio

import importlib
import importlib.util

from pyrogram import Client



class Module:
    strings = {"name": "Unknown"}

    async def init(self, app: Client): # TODO db: db
        """Какая-то локальная фигня, я не могу это описать, но я сам понимаю зывазхщвапазхвпщ"""


class Modules:
    def __init__(self, app: Client):
        self.commands = {}
        self.watchers = []
        self.modules = []
        self.modules_path = "sh1t-ub/handlers/"
        self.app = app
        # self.db = db  : from .misc import db

    async def register_all(self):
        modules = filter(
            lambda file_name: (file_name.endswith(".py") and file_name[0] != "_"), os.listdir(self.modules_path)
        )

        for module in modules:
            module_name = f"sh1t-ub.handlers.{module[:-3]}"
            file_path = os.path.join(
                os.path.abspath("."), self.modules_path, module
            )

            self.register_module(module_name, file_path)

        await self.send_init()

    def register_module(self, module_name: str, file_path: str):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module.__name__] = module
        spec.loader.exec_module(module)

        for key, value in vars(module).items():
            if key.endswith("Mod") and issubclass(value, Module):
                self.modules.append(value())

    async def send_init(self):
        try:
            await asyncio.gather(
                *[self.send_init_one(module) for module in self.modules]
            )
        except Exception as error:
            print(f"Произошла ошибки при отправки init в модуль. Ошибка: {error}")

        return True

    async def send_init_one(self, module: Module):
        await module.init(self.app)

        module.allmodules = self
        module.commands = self.get_commands(module)
        if hasattr(module, "watcher"):
            self.watchers.append(module.watcher)

        self.commands.update(
            {
                command.lower(): module.commands[command]
                for command in module.commands
            }
        )

        return True

    def get_commands(self, module: Module):
        return {
            method_name[:-4]: getattr(module, method_name) for method_name in dir(module)
            if callable(getattr(module, method_name)) and method_name[-4:] == "_cmd"
        }

    async def restart(self):
        await self.register_all()