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

import requests
import inspect

from importlib.abc import SourceLoader
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location, module_from_spec

from typing import Union, List, Dict
from types import FunctionType, LambdaType

from pyrogram import Client, filters
from . import dispatcher, utils, database, inline


def module(
    name: str,
    author: str = None,
    version: Union[int, float] = None
) -> FunctionType:
    """Обрабатывает класс модуля

    Параметры:
        name (``str``):
            Название модуля

        author (``str``, *optional*):
            Автор модуля

        version (``int`` | ``float``, *optional*):
            Версия модуля
    """
    def decorator(instance: "Module"):
        """Декоратор для обработки класса модуля"""
        instance.name = name
        instance.author = author
        instance.version = version
        return instance
    return decorator


@module(name="Unknown")
class Module:
    """Описание модуля"""


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


def get_command_handlers(instance: Module) -> Dict[str, FunctionType]:
    """Возвращает словарь из названий с функциями команд"""
    return {
        method_name[:-4].lower(): getattr(
            instance, method_name
        ) for method_name in dir(instance)
        if (
            callable(getattr(instance, method_name))
            and len(method_name) > 4
            and method_name.endswith("_cmd")
        )
    }


def get_watcher_handlers(instance: Module) -> List[FunctionType]:
    """Возвращает список из вотчеров"""
    return [
        getattr(instance, method_name)
        for method_name in dir(instance)
        if (
            callable(getattr(instance, method_name))
            and method_name.startswith("watcher")
        )
    ]


def get_inline_handlers(instance: Module) -> Dict[str, FunctionType]:
    """Возвращает словарь из названий с функциями инлайн-хендлеров"""
    return {
        method_name[:-15].lower(): getattr(
            instance, method_name
        ) for method_name in dir(instance)
        if (
            callable(getattr(instance, method_name))
            and len(method_name) > 15
            and method_name.endswith("_inline_handler")
        )
    }


def get_callback_handlers(instance: Module) -> Dict[str, FunctionType]:
    """Возвращает словарь из названий с функциями каллбек-хендлеров"""
    return {
        method_name[:-17].lower(): getattr(
            instance, method_name
        ) for method_name in dir(instance)
        if (
            callable(getattr(instance, method_name))
            and len(method_name) > 17
            and method_name.endswith("_callback_handler")
        )
    }


def on(custom_filters: Union[filters.Filter, LambdaType]) -> FunctionType:
    """Создает фильтр для команды

    Параметры:
        custom_filters (``pyrogram.filters.Filter`` | ``types.LambdaType``):
            Фильтры

    Пример:
        >>> @on(lambda _, app, message: message.chat.type == "supergroup")
        >>> @on(pyrogram.filters.chats("@sh1tubchat"))
        >>> async def func_cmd(self, app: Client, message: types.Message):
        >>>     ...
    """
    def decorator(func: FunctionType):
        """Декоратор для обработки команды"""
        func._filters = (
            filters.create(custom_filters)
            if custom_filters.__module__ != "pyrogram.filters"
            else custom_filters
        )
        return func
    return decorator


def on_bot(custom_filters: LambdaType) -> FunctionType:
    """Создает фильтр для команды бота

    Параметры:
        custom_filters (``types.FunctionType`` | ``types.LambdaType``):
            Фильтры.
            Функция должна принимать параметры self, app, message/inline_query/call

    Пример:
        >>> @on_bot(lambda self, app, call: call.from_user.id == self.all_modules.me.id)
        >>> async def func_cmd(self, app: Client, message: types.Message):
        >>>     ...
    """
    def decorator(func: FunctionType):
        """Декоратор для обработки команды бота"""
        func._filters = custom_filters
        return func
    return decorator


class ModulesManager:
    """Менеджер модулей"""

    def __init__(self, db: database.Database) -> None:
        self.modules: List[Module] = []
        self.watcher_handlers: List[FunctionType] = []

        self.command_handlers: Dict[str, FunctionType] = {}
        self.inline_handlers: Dict[str, FunctionType] = {}
        self.callback_handlers: Dict[str, FunctionType] = {}

        self._local_modules_path: str = "sh1t-ub/modules/"

        self._db = db
        self.aliases = self._db.get(__name__, "aliases", {})

        self.me = None
        self.dp = None
        self.inline = None

    async def cache(self, app: Client) -> bool:
        """Кэширует"""
        self.me = await app.get_me()
        return True

    async def load(self, app: Client) -> bool:
        """Загружает менеджер модулей"""
        await self.cache(app)

        self.dp = dispatcher.DispatcherManager(app, self)
        await self.dp.load()

        self.inline = inline.BotManager(app, self._db, self)
        await self.inline.load()

        logging.info("Загрузка модулей...")

        for local_module in filter(
            lambda file_name: file_name.endswith(".py")
                and not file_name.startswith("_"), os.listdir(self._local_modules_path)
        ):
            module_name = f"sh1t-ub.modules.{local_module[:-3]}"
            file_path = os.path.join(
                os.path.abspath("."), self._local_modules_path, local_module
            )

            try:
                self.register_instance(module_name, file_path)
            except Exception as error:
                logging.exception(
                    f"Ошибка при загрузке локального модуля {module_name}: {error}")

        for custom_module in self._db.get(__name__, "modules", []):
            try:
                r = await utils.run_sync(requests.get, custom_module)
                self.load_module(r.text, r.url)
            except requests.exceptions.ConnectionError as error:
                logging.exception(
                    f"Ошибка при загрузке стороннего модуля {custom_module}: {error}")

        logging.info("Менеджер модулей загружен")
        return True

    def register_instance(
        self,
        module_name: str,
        file_path: str = "",
        spec: ModuleSpec = None
    ) -> Module:
        """Регистрирует модуль"""
        spec = spec or spec_from_file_location(module_name, file_path)
        module = module_from_spec(spec)
        sys.modules[module.__name__] = module
        spec.loader.exec_module(module)

        instance = None
        for key, value in vars(module).items():
            if key.endswith("Mod") and issubclass(value, Module):
                value: Module

                value.db = self._db
                value.all_modules = self

                for module in self.modules:
                    if module.__class__.__name__ == value.__name__:
                        self.unload_module(module, True)

                instance = value()
                instance.command_handlers = get_command_handlers(instance)
                instance.watcher_handlers = get_watcher_handlers(instance)

                instance.inline = self.inline
                instance.inline_handlers = get_inline_handlers(instance)
                instance.callback_handlers = get_callback_handlers(instance)

                self.modules.append(instance)
                self.command_handlers.update(instance.command_handlers)
                self.watcher_handlers.extend(instance.watcher_handlers)

                self.inline_handlers.update(instance.inline_handlers)
                self.callback_handlers.update(instance.callback_handlers)

        return instance

    def load_module(self, module_source: str, origin: str = "<string>") -> str:
        """Загружает сторонний модуль"""
        module_name = "sh1t-ub.modules." + (
            "".join(random.choice(string.ascii_letters + string.digits)
                    for _ in range(10))
        )

        try:
            spec = ModuleSpec(module_name, StringLoader(
                module_source, origin), origin=origin)
            instance = self.register_instance(module_name, spec=spec)
        except Exception as error:
            return logging.exception(
                f"Ошибка при загрузке модуля {origin}: {error}")

        return instance.name

    def unload_module(self, module_name: str = None, is_replace: bool = False) -> str:
        """Выгружает загруженный (если он загружен) модуль"""
        if is_replace:
            module = module_name
        else:
            if not (module := self.get_module(module_name)):
                return False

            if (get_module := inspect.getmodule(module)).__spec__.origin != "<string>":
                set_modules = set(self._db.get(__name__, "modules", []))
                self._db.set("sh1t-ub.loader", "modules",
                             list(set_modules - {get_module.__spec__.origin}))

            for alias, command in self.aliases.copy().items():
                if command in module.command_handlers:
                    del self.aliases[alias]
                    del self.command_handlers[command]

        self.modules.remove(module)
        self.command_handlers = dict(
            set(self.command_handlers.items()) ^ set(module.command_handlers.items())
        )
        self.watcher_handlers = list(
            set(self.watcher_handlers) ^ set(module.watcher_handlers)
        )

        self.inline_handlers = dict(
            set(self.inline_handlers.items()) ^ set(module.inline_handlers.items())
        )
        self.callback_handlers = dict(
            set(self.callback_handlers.items()) ^ set(module.callback_handlers.items())
        )

        return module.name

    def get_module(self, name: str, by_commands_too: bool = False) -> Union[Module, None]:
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

        if by_commands_too and name in self.command_handlers:
            return self.command_handlers[name].__self__

        return None
