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

import sys

if sys.version_info < (3, 8, 0):
    print("Требуется Python 3.8 или выше")
    sys.exit(1)


import asyncio
import argparse

from . import main, logger


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="sh1t-ub", description="Телеграм юзербот разработанный sh1tn3t'ом",
        epilog="Канал: @sh1tub", add_help=False
    )
    parser.add_argument("--help", "-h", action="help",
                        help="Показать это сообщение")
    parser.add_argument("--log-level", "-lvl", dest="logLevel", default="INFO",
                        help="Установить уровень логирования. Доступно: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL или число от 0 до 50")

    return parser.parse_args()


if __name__ == "__main__":
    logger.setup_logger(parse_arguments().logLevel)
    asyncio.run(main.main())
