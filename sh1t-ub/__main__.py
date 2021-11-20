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
    logging.info("Shutting down...")


if __name__ == "__main__":
    cli()