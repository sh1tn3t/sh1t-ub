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

import configparser

import psutil
import platform

from aiogram.types import (
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from pyrogram import Client, types
from .. import loader, utils, inline, __version__


INFO_MARKUP = InlineKeyboardMarkup().add(
    InlineKeyboardButton("◀️ Назад", callback_data="info")
)

INFO_SERVER_MARKUP = InlineKeyboardMarkup().add(
    InlineKeyboardButton("ℹ️ Информация о сервере", callback_data="info_server")
)


def humanize(num: float, suffix: str = "B") -> str:
    for unit in ["B", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0

    return "%.1f%s%s" % (num, "Yi", suffix)


def get_info_message(me: types.User):
    mention = f"<a href=\"tg://user?id={me.id}\">{utils.get_display_name(me)}</a>"
    return (
        f"😎 <b>Sh1tN3t UserBot</b>\n\n"
        f"🔢 <b>Версия</b>: v{__version__}\n"
        f"👤 <b>Владелец</b>: {mention}"
    )


def get_other_info():
    if platform.system() == "Linux":
        content = "[linux]\n" + open("/etc/os-release", "r").read()

        config = configparser.ConfigParser()
        config.read_string(content)

        os = platform.system()
        distro = config["linux"]["PRETTY_NAME"].strip('"')
        kernel = platform.release()
        arch = " ".join(platform.architecture())

        return (
            f"    - ОС: <b>{os}</b>\n"
            f"    - Дистрибутив: <b>{distro}</b>\n"
            f"    - Ядро: <b>{kernel}</b>\n"
            f"    - Архитектура: <b>{arch}</b>"
        )


def get_cpu_info():
    return (
        f"    - Использование: <b>{int(psutil.cpu_percent())}</b>%\n"
        f"    - Ядра: <b>{psutil.cpu_count()}</b>"
    )


def get_ram_info():
    ram = psutil.virtual_memory()
    return (
        f"    - Занято: <b>{humanize(ram.used)}</b> (<b>{int(ram.percent)}</b>%)\n"
        f"    - Всего: <b>{humanize(ram.total)}</b>"
    )


def get_disk_info():
    disk = psutil.disk_usage("/")
    return (
        f"    - Занято: <b>{humanize(disk.used)}</b> (<b>{int(disk.percent)}</b>%)\n"
        f"    - Всего: <b>{humanize(disk.total)}</b>"
    )


@loader.module("Information", "sh1tn3t")
class InformationMod(loader.Module):
    """Информация о юзерботе"""

    @loader.on_bot(lambda self, app, call: True)
    async def info_inline_handler(self, app: Client, inline_query: InlineQuery):
        """Информация о юзерботе. Использование: @bot info"""
        message = InputTextMessageContent(
            get_info_message(self.all_modules.me))

        return await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=inline.result_id(),
                    title="Информация",
                    input_message_content=message,
                    reply_markup=INFO_SERVER_MARKUP,
                    thumb_url="https://api.fl1yd.su/emoji/2139-fe0f.png",
                )
            ], cache_time=0
        )

    @loader.on_bot(lambda self, app, call: call.data == "info")
    async def info_callback_handler(self, app: Client, call: CallbackQuery):
        """Информация о юзерботе"""
        if call.from_user.id != self.all_modules.me.id:
            return await call.answer(
                "❗ А эта кнопочка не для тебя!")

        await call.answer()

        return await self.inline.bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text=get_info_message(self.all_modules.me),
            reply_markup=INFO_SERVER_MARKUP
        )

    @loader.on_bot(lambda self, app, call: call.data == "info_server")
    async def info_server_callback_handler(self, app: Client, call: CallbackQuery):
        """Информация о сервере"""
        if call.from_user.id != self.all_modules.me.id:
            return await call.answer(
                "❗ А эта кнопочка не для тебя!")

        await call.answer()

        message = (
            f"<b>ℹ️ Информация о системе</b>:\n"
            f"---------------\n\n"
            f"🧠 <b>Процессор</b>:\n"
            f"{get_cpu_info()}\n\n"
            f"🗄️ <b>ОЗУ</b>:\n"
            f"{get_ram_info()}\n\n"
            f"💿 <b>Физ. память</b>:\n"
            f"{get_disk_info()}\n\n"
            f"🗃 <b>Прочее</b>:\n"
            f"{get_other_info()}"
        )
        return await self.inline.bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text=message,
            reply_markup=INFO_MARKUP
        )
