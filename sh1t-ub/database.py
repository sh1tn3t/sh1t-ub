from lightdb import LightDB


class Database(LightDB):
    def init(self):
        self.update(**self.db)
        return self.save()

    def __repr__(self):
        return object.__repr__(self)

    def set(self, name, key, value):
        self.setdefault(name, {})[key] = value
        return self.init()

    def get(self, name, key, default = None):
        try:
            return self.db[name][key]
        except KeyError:
            return default

    def pop(self, name, key = None, default = None):
        if not key:
            value = self.db.pop(name, default)
        else:
            try:
                value = self.db[name].pop(key, default)
            except KeyError:
                value = default

        self.init()
        return value