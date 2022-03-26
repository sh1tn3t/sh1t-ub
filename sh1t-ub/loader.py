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

from typing import Union
from pyrogram import filters as filters_

from . import utils, database


def module(name: str, author: str = None, version: Union[int, float] = None):
    """Декоратор для обработки класса модуля"""
    def decorator(module: "Module"):
        module.name = name
        module.author = author
        module.version = version
        return module
    return decorator


@module(name="Unknown")
class Module:
    """Описание модуля"""


class Modules:
    """Класс, хранящий в себе загруженные модули"""

    def __init__(self, db: database.Database):
        self.prefix = db.get("sh1t-ub.loader", "prefixes", ["-"])
        self.commands = {}
        self.aliases = db.get(__name__, "aliases", {})
        self.watchers = []
        self.modules = []
        self.modules_path = "./sh1t-ub/modules/"
        self.db = db

        asyncio.get_event_loop().create_task(
            self.register_all())

    async def register_all(self):
        """Регистрирует все модули"""
        for module in filter(
            lambda file_name: file_name.endswith(".py") \
                and not file_name.startswith("_"), os.listdir(self.modules_path)
        ):
            module_name = f"sh1t-ub.modules.{module[:-3]}"
            file_path = os.path.join(
                os.path.abspath("."), self.modules_path, module
            )

            try:
                self.register_module(module_name, file_path)
            except Exception as error:
                logging.exception(
                    f"Ошибка при загрузке модуля {module_name}: {error}")

        for module in self.db.get(__name__, "modules", []):
            try:
                r = await utils.run_sync(requests.get, module)
                await self.load_module(r.text, r.url)
            except requests.exceptions.ConnectionError as error:
                logging.exception(
                    f"Ошибка при загрузке стороннего модуля {module}: {error}")

        return True

    def register_module(self, module_name: str, file_path: str = "", spec: ModuleSpec = None):
        """Регистрирует модуль"""
        spec = spec or spec_from_file_location(module_name, file_path)
        module = module_from_spec(spec)
        sys.modules[module.__name__] = module
        spec.loader.exec_module(module)

        instance = None
        for _, value in filter(
            lambda element: element[0].endswith("Mod") \
                and issubclass(element[1], Module), vars(module).items()
        ):
            value.db = self.db
            value.all_modules = self

            for module in filter(
                lambda module: module.__class__.__name__ == value.__name__, self.modules
            ):
                self.modules.remove(module)

            instance = value()
            instance.commands = get_commands(instance)

            for watcher in filter(
                lambda attr: attr.startswith("watcher"), dir(instance)
            ):
                self.watchers.append(getattr(instance, watcher))

            self.commands.update(instance.commands)
            self.modules.append(instance)

        return instance

    async def load_module(self, module_source: str, origin: str = "<string>"):
        """Загружает сторонний модуль"""
        module_name = "sh1t-ub.modules." + \
            "".join(random.choice(string.ascii_letters + string.digits)
                    for _ in range(10))

        try:
            spec = ModuleSpec(module_name, StringLoader(
                module_source, origin), origin=origin)
            instance = self.register_module(module_name, spec=spec)
        except Exception as error:
            return logging.exception(
                f"Ошибка при загрузке модуля {origin}: {error}")

        return instance.name

    async def unload_module(self, module_name: str):
        """Выгружает загруженный (если он загружен) модуль"""
        if not (module := self.get_module(module_name)):
            return False

        if (get_module := inspect.getmodule(module)).__spec__.origin != "<string>":
            setted_modules = set(self.db.get(__name__, "modules", []))
            self.db.set("sh1t-ub.loader", "modules",
                        list(setted_modules - {get_module.__spec__.origin}))

        self.modules.remove(module)
        for watcher in filter(
            lambda attr: attr.startswith("watcher"), dir(module)
        ):
            self.watchers.remove(getattr(module, watcher))

        for alias, command in self.aliases.copy().items():
            if command in module.commands:
                del self.aliases[alias]
                del self.commands[command]

        return module.name

    def get_module(self, name: str, by_commands_too: bool = False):
        """Ищет модуль по названию или по команде"""
        if (
            module := list(
                filter(
                    lambda module: module.name.lower(
                    ) == name.lower(), self.modules
                )
            )
        ):
            return module[0]

        elif by_commands_too and name in self.commands:
            return self.commands[name].__self__


class StringLoader(SourceLoader):
    """Загружает модуль со строки"""

    def __init__(self, data: str, origin: str):
        self.data = data.encode("utf-8")
        self.origin = origin

    def get_code(self, full_name: str):
        source = self.get_source(full_name)
        if not source:
            return None

        return compile(source, self.origin, "exec", dont_inherit=True)

    def get_filename(self, _: str):
        return self.origin

    def get_data(self, _: str):
        return self.data


def get_commands(module: Module):
    """Возвращает словарь из команд с функциями"""
    return {
        method_name[:-4].lower(): getattr(
            module, method_name
        ) for method_name in dir(module)
        if (
            callable(getattr(module, method_name))
            and method_name.endswith("_cmd")
        )
    }


def on(filters):
    """Создает фильтр для команды"""
    def decorator(func):
        func.filters = (
            filters_.create(filters)
            if filters.__module__ != "pyrogram.filters"
            else filters
        )
        return func
    return decorator
