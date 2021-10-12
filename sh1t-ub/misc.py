from lightdb import LightDB
from pyrogram import Client


db = LightDB("./db.json")
app = Client(
    "../sh1t-ub", parse_mode = "html", config_file = "./config.ini"
)