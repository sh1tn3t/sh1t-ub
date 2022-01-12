import sys
import asyncio

import logging
import configparser

from datetime import datetime

from getpass import getpass
from pyrogram import Client, errors

from . import __version__


def colored_input(prompt: str = "", hide: bool = False):
    frame = sys._getframe(1)
    return (input if not hide else getpass)(
        "\x1b[32m{time:%Y-%m-%d %H:%M:%S}\x1b[0m | "
        "\x1b[1m{level: <8}\x1b[0m | "
        "\x1b[36m{name}\x1b[0m:\x1b[36m{function}\x1b[0m:\x1b[36m{line}\x1b[0m - \x1b[1m{prompt}\x1b[0m".format(
            time=datetime.now(), level="INPUT", name=frame.f_globals["__name__"],
            function=frame.f_code.co_name, line=frame.f_lineno, prompt=prompt
        )
    )


class Auth:
    """Авторизация в аккаунт"""

    def __init__(self, session_name: str = "../sh1t-ub"):  # ".." чтобы не сессия была вне папки sh1t-ub/sh1t-ub
        self.check_api_tokens()
        self.app = Client(
            session_name, config_file="./config.ini",
            app_version=f"Sh1t-UB v{__version__}"
        )

    def check_api_tokens(self):
        """Проверят установлены ли токен, если нет, то начинает установку"""
        config = configparser.ConfigParser()
        if not config.read("./config.ini"):
            config["pyrogram"] = {
                "api_id": colored_input("Введи API ID: "),
                "api_hash": colored_input("Введи API hash: "),
            }
        
            with open("./config.ini", "w") as file:
                config.write(file)

        pyro_config = config["pyrogram"]
        return pyro_config["api_id"], pyro_config["api_hash"]

    async def send_code(self):
        """Отправить код подтверждения"""
        while True:
            try:
                phone = colored_input("Введи номер телефона: ")
                return phone, (await self.app.send_code(phone)).phone_code_hash
            except errors.BadRequest:
                logging.error("Неверный номер телефона, попробуй ещё раз")

    async def enter_code(self, phone: str, phone_code_hash: str):
        """Ввести код подтверждения"""
        try:
            code = colored_input("Введи код подтверждения: ")
            return await self.app.sign_in(phone, phone_code_hash, code)
        except errors.SessionPasswordNeeded:
            return False

    async def enter_2fa(self):
        """Ввести код двухфакторной аутентификации"""
        while True:
            try:
                passwd = colored_input("Введи пароль двухфакторной аутентификации: ", True)
                return await self.app.check_password(passwd)
            except errors.BadRequest:
                logging.error("Неверный пароль, попробуй снова")

    async def authorize(self):
        """Авторизирует в аккаунт"""
        await self.app.connect()

        try:
            await self.app.get_me()
        except errors.AuthKeyUnregistered:
            phone, phone_code_hash = await self.send_code()
            logged = await self.enter_code(phone, phone_code_hash)
            if not logged:
                await self.enter_2fa()
        except errors.SessionRevoked:
            logging.error("Сессия была сброшена, введи rm sh1t-ub.session и заново введи команду запуска")
            await self.app.disconnect()
            return sys.exit(0)

        return self.app
