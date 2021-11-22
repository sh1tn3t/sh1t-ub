#    Sh1t-UB (telegram userbot by sh1tn3t)
#    Copyright (C) 2021 Sh1tN3t

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
import logging
import configparser

from pyrogram import Client

from . import main, logger, __version__


app = Client(
    "../sh1t-ub", config_file = "./config.ini",
    parse_mode = "html", app_version = f"Sh1t-UB v{__version__}"
)


def config_setup():
    config = configparser.ConfigParser()
    config["pyrogram"] = {
        "api_id": input("Введи свой API ID: "),
        "api_hash": input("Введи свой API hash: "),
    }

    with open("config.ini", "w") as file:
        config.write(file)


def cli():
    if not os.path.exists("./config.ini"):
        config_setup()

    logger.setup_logger(ignored = [
        "pyrogram.session",
        "pyrogram.connection",
        "pyrogram.methods.utilities.idle"
    ])

    app.run(main.main(app))
    logging.info("Завершение работы...")


if __name__ == "__main__":
    cli()
