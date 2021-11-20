import os
import sys

import logging
import string
import random

import asyncio
import requests
import inspect

from importlib.abc import SourceLoader
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location, module_from_spec

from pyrogram import filters
from . import utils, database, __version__


class StringLoader(SourceLoader):
    """Загружает модуль/файл со строки"""

    def __init__(self, data: str, origin: str):
        self.data = data.encode("utf-8")
        self.origin = origin

    def get_code(self, full_name: str):
        source = self.get_source(full_name)
        if not source:
            return None

        return compile(source, self.origin, "exec", dont_inherit = True)

    def get_filename(self, _: str):
        return self.origin

    def get_data(self, _: str):
        return self.data


class Module:
    """Описание модуля"""

    strings = {"name": "Unknown"}

    async def init(self, db: database.Database):
        """Отсылает данные модулю"""


class Modules:
    def __init__(self, db: database.Database):
        self.commands = {}
        self.aliases = db.get(__name__, "aliases", {})
        self.watchers = []
        self.modules = []
        self.modules_path = "sh1t-ub/modules/"
        self.db = db

    async def register_all(self):
        local_modules = filter(
            lambda file_name: (file_name.endswith(".py") and not file_name.startswith("_")), os.listdir(self.modules_path)
        )

        for module in local_modules:
            module_name = f"sh1t-ub.modules.{module[:-3]}"
            file_path = os.path.join(
                os.path.abspath("."), self.modules_path, module
            )

            try:
                self.register_module(module_name, file_path)
            except Exception as error:
                logging.error(
                    f"Ошибка при загрузке модуля {module_name}: {error}")

        await self.send_init()

        for module in self.db.get(__name__, "modules", []):
            try:
                r = await utils.run_sync(requests.get, module)
                module_name = await self.load_module(r.text, r.url)
            except requests.exceptions.ConnectionError as error:
                logging.error(
                    f"Ошибка при загрузке модуля {module}: {error}")

    def register_module(self, module_name: str, file_path: str = None, spec: ModuleSpec = None):
        spec = spec or spec_from_file_location(module_name, file_path)
        module = module_from_spec(spec)
        sys.modules[module.__name__] = module
        spec.loader.exec_module(module)

        instance = None
        for key, value in vars(module).items():
            if key.endswith("Mod") and issubclass(value, Module):
                instance = value()
                for module in self.modules:
                    if module.__class__.__name__ == instance.__class__.__name__:
                        self.modules.remove(module)

                self.modules.append(instance)

        return instance

    async def load_module(self, module_source: str, origin = "<string>"):
        module_name = "sh1t-ub.modules." + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

        try:
            spec = ModuleSpec(module_name, StringLoader(module_source, origin), origin = origin)
            instance = self.register_module(module_name, spec = spec)
            await self.send_init_one(instance)
        except Exception as error:
            logging.error(
                f"Ошибка при загрузке модуля {origin}: {error}")
            return False

        return instance.strings["name"]

    async def send_init(self):
        try:
            await asyncio.gather(
                *[self.send_init_one(module) for module in self.modules]
            )
        except Exception as error:
            logging.error(
                f"Произошла ошибки при отправки init в модуль. Ошибка: {error}")

        return True

    async def send_init_one(self, module: Module):
        await module.init(self.db)

        module.sh1t_version = __version__
        module.all_modules = self
        module.commands = get_commands(module)

        self.commands.update(module.commands)
        if hasattr(module, "watcher"):
            self.watchers.append(module.watcher)

        return True

    async def unload_module(self, module_name: str):
        if not (
            module := list(
                filter(
                    lambda module: module.strings["name"].lower() == module_name.lower(), self.modules
                )
            )
        ):
            return False

        module = module[0]
        if (get_module := inspect.getmodule(module)).__spec__.origin != "<string>":
            self.db.set("sh1t-ub.loader", "modules", list(set(self.db.get(__name__, "modules", [])) - set([get_module.__spec__.origin])))

        self.modules.remove(module)
        if hasattr(module, "watcher"):
            self.watchers.remove(module.watcher)

        for alias, command in self.aliases.copy().items():
            if command in module.commands:
                del self.aliases[alias]
                del self.commands[command]

        return module.strings["name"]


def get_commands(module: Module):
    return {
        method_name[:-4].lower(): getattr(module, method_name) for method_name in dir(module)
        if callable(getattr(module, method_name)) and method_name[-4:] == "_cmd"
    }

def on(filter_func):
    def decorator(func):
        func.filter = (
            filters.create(filter_func)
            if filter_func.__module__ != "pyrogram.filters"
            else filter_func
        )
        return func

    return decorator