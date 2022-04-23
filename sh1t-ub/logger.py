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

import logging

from typing import Union
from datetime import datetime

from loguru._better_exceptions import ExceptionFormatter
from loguru._colorizer import Colorizer
from loguru import logger

FORMAT_FOR_FILES = (
    "{time:%Y-%m-%d %H:%M:%S} | "
    "{level: <8} | "
    "{name}:{function}:{line} - {message}"
)


def get_valid_level(level: Union[str, int]):
    return (
        int(level) if level.isdigit()
        else getattr(logging, level.upper(), None)
    )


class StreamHandler(logging.Handler):
    """Обработчик логирования в поток"""

    def __init__(self, lvl: int = logging.INFO):
        super().__init__(lvl)

    def format(self, record: logging.LogRecord):
        """Форматирует логи под нужный формат"""
        exception_lines = ""
        stripped_formatter = Colorizer.prepare_format(
            FORMAT_FOR_FILES + "{exception}"
        ).strip()

        if record.exc_info:
            exception_formatter = ExceptionFormatter(
                encoding="utf8", backtrace=True, prefix="\n",
                hidden_frames_filename=logger.catch.__code__.co_filename
            )

            type_, value, tb = record.exc_info
            exception_list = exception_formatter.format_exception(type_, value, tb)
            exception_lines = "".join(exception_list)

        return stripped_formatter.format(
            time=datetime.fromtimestamp(record.created), level=record.levelname,
            name=record.name, function=record.funcName, message=record.msg,
            line=record.lineno, exception=exception_lines
        )


class MemoryHandler(logging.Handler):
    """Обработчик логирования в память"""

    def __init__(self, lvl: int = logging.INFO):
        super().__init__(0)
        self.target = StreamHandler(lvl)
        self.lvl = lvl

        self.capacity = 500
        self.buffer = []
        self.handled_buffer = []

    def dumps(self, lvl: int):
        """Возвращает список всех входящих логов по минимальному уровню"""
        sorted_logs = list(
            filter(
                lambda record: record.levelno >= lvl, self.handled_buffer)
        )
        self.handled_buffer = list(set(self.handled_buffer) ^ set(sorted_logs))
        return map(self.target.format, sorted_logs)

    def emit(self, record: logging.LogRecord):
        """Логирует"""
        if len(self.buffer + self.handled_buffer) >= self.capacity:
            if self.handled_buffer:
                del self.handled_buffer[0]
            else:
                del self.buffer[0]

        self.buffer.append(record)
        if record.levelno >= self.lvl >= 0:
            self.acquire()
            try:
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno

                frame, depth = logging.currentframe(), 2
                while frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1

                logger.opt(depth=depth, exception=record.exc_info).log(
                    level, record.getMessage())

                self.handled_buffer = self.handled_buffer[-(self.capacity - len(self.buffer)):] + self.buffer
                self.buffer = []
            finally:
                self.release()


def setup_logger(level: Union[str, int]):
    """Установка логирования"""
    level = get_valid_level(level) or 20
    handler = MemoryHandler(level)
    logging.basicConfig(handlers=[handler], level=level)

    for ignore in [
        "pyrogram.session",
        "pyrogram.connection",
        "pyrogram.methods.utilities.idle"
    ]:
        logger.disable(ignore)
