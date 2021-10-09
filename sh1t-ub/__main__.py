import logging
from . import main, logger
from .misc import app



def cli():
    logger.setup_logger(ignored = [
        "pyrogram.session",
        "pyrogram.connection",
        "pyrogram.methods.utilities.idle"
    ])
    logging.info("Started successful")

    app.run(main.main(app))
    logging.info("Shutting down...")


if __name__ == "__main__":
    cli()