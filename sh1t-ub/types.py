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

from types import FunctionType
from typing import Union, List, Dict, Any

from . import database


class Module:
    """Описание модуля"""
    name: str
    author: str
    version: Union[int, float]

    async def on_load(self, app: Client) -> Any:
        """Вызывается при загрузке модуля"""


class ModulesManager:
    """Менеджер модулей"""

    def __init__(self) -> None:
        self.modules: List[Module]
        self.watcher_handlers: List[FunctionType]

        self.command_handlers: Dict[str, FunctionType]
        self.message_handlers: Dict[str, FunctionType]
        self.inline_handlers: Dict[str, FunctionType]
        self.callback_handlers: Dict[str, FunctionType]

        self._local_modules_path: str

        self.me: types.User
        self._db: database.Database

        self.aliases: Dict[str, str]

        self.dp
        self.bot_manager
