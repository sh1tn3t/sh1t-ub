import os
import logging
import configparser

from . import main, logger
from .misc import app, db



def config_setup():
    config = configparser.ConfigParser()
    config["pyrogram"] = {
        "api_id": input("Введи свой API ID: "),
        "api_hash": input("Введи свой API hash: "),
    }

    with open("config.ini", "w") as file:
        config.write(file)


def cli():
    if not os.path.exists("config.ini"):
        config_setup()

    logger.setup_logger(ignored = [
        "pyrogram.session",
        "pyrogram.connection",
        "pyrogram.methods.utilities.idle"
    ])

    logging.info("Started successful")
    app.run(main.main(app, db))
    logging.info("Shutting down...")


if __name__ == "__main__":
    cli()