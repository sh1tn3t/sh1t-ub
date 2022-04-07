<p align="center">
    <img src="https://my.fl1yd.su/sh1t-ub_nobg.png">
    <br>
    <b>Sh1tN3t UserBot (sh1t-ub)</b> — крутой юзербот, написанный на <a href="https://github.com/pyrogram/pyrogram">Pyrogram</a>
    <br>
    <a href="https://t.me/sh1tub">Канал с обновлениями</a>
    •
    <a href="https://t.me/sh1tubchat">Чат поддержки</a>
</p>


<h1>Описание</h1>

sh1tub — это ваш интерактивный многофункциональный помощник в Телеграме  
Многофункциональный и расширяемый юзербот позволит создавать любые модули, нужна лишь фантазия

Подключение к аккаунту происходит посредством создании новой (!) сессии

Наши преимущества:
<ul>
    <li>Удобство и простота в использовании</li>
    <li>Низкая ресурсозатраность</li>
    <li>Большой ассортимент готовых модулей</li>
    <li>Грамотное построение структуры каждого модуля</li>
    <li>Асинхронное выполнение каждой задачи</li>
    <li>Удобная загрузка и выгрузка модулей</li>
</ul>


<h1>Установка</h1>

Для начала нужно установить компоненты:

<pre lang="bash">
apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
</pre>

После этого клонировать репозиторий и установить зависимости:

<pre lang="bash">
git clone https://github.com/sh1tn3t/sh1t-ub && cd sh1t-ub
pip3 install -r requirements.txt
</pre>


<h1>Запуск</h1>

> При первом запуске потребуется ввести api_id и api_hash. Их можно получить на <a href="https://my.telegram.org">my.telegram.org</a>

<pre lang="bash">
python3 -m sh1t-ub
</pre>

вы также можете:

<pre lang="bash">
$ python3 -m sh1t-ub --help
usage: sh1t-ub [--help] [--log-level LOGLEVEL]

Телеграм юзербот разработанный sh1tn3t‘ом

optional arguments:
  --help, -h            Показать это сообщение
  --log-level LOGLEVEL, -lvl LOGLEVEL
                        Установить уровень логирования. Доступно: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL или число от 0 до 50

Канал: @sh1tub
</pre>

<h1>Пример модуля</h1>

> Больше примеров функций и полное описание смотри в файле <a href="./sh1t-ub/modules/_example.py">_example.py</a>

<pre lang="python">
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="Example")
class ExampleMod(loader.Module):
    """Описание модуля"""

    async def example_cmd(self, app: Client, message: types.Message):
        """Описание команды"""
        return await utils.answer(
            message, "Пример команды")

    @loader.on(lambda _, __, m: m and m.text == "Привет, это проверка вотчера щит-юб")
    async def watcher(self, app: Client, message: types.Message):
        return await message.reply(
            "Привет, все работает отлично")
</pre>
