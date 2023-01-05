import re

from mongo_thingy import BaseThingy


def camelize(string):
    if string.startswith("__"):
        return string
    return re.sub(r"(?!^)_([a-zA-Z])", lambda m: m.group(1).upper(), string)


def uncamelize(string):
    if string.startswith("__"):
        return string
    return re.sub(r"(?<!^)(?<![A-Z])[A-Z]", r"_\g<0>", string).lower()


class CamelCase:
    def __setattr__(self, attr, value):
        return BaseThingy.__setattr__(self, camelize(attr), value)

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, camelize(attr))
        except AttributeError:
            return BaseThingy.__getattribute__(self, uncamelize(attr))
