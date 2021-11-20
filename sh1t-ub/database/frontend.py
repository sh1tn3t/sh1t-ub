from lightdb import LightDB
from pyrogram import types

from typing import Union
from . import CloudDatabase



class Database(LightDB):
    def __init__(self, location: str, cloud: CloudDatabase):
        super().__init__(location)
        self.cloud = cloud

    def __repr__(self):
        return object.__repr__(self)

    def set(self, name, key, value): # skipcq: PYL-W0622
        self.setdefault(name, {})[key] = value
        return self.save()

    def get(self, name, key, default = None): # skipcq: PYL-W0622
        try:
            return self[name][key]
        except KeyError:
            return default

    def pop(self, name, key = None, default = None): # skipcq: PYL-W0622
        if not key:
            value = self.pop(name, default)
        else:
            try:
                value = self[name].pop(key, default)
            except KeyError:
                value = default

        self.save()
        return value

    async def save_data(self, message: Union[types.Message, str]):
        return await self.cloud.save_data(message)

    async def get_data(self, message_id: int):
        return await self.cloud.get_data(message_id)