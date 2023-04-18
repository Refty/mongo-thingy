import re

from mongo_thingy import BaseThingy

CAMELIZE_RE = re.compile(r"(?!^)_([a-zA-Z])")
UNCAMELIZE_RE = re.compile(r"(?<!^)(?<![A-Z])[A-Z]")


def camelize(string):
    if string.startswith("__") or "_" not in string:
        return string
    return re.sub(CAMELIZE_RE, lambda m: m.group(1).upper(), string)


def uncamelize(string):
    if string.startswith("__") or "_" in string:
        return string
    return re.sub(UNCAMELIZE_RE, r"_\g<0>", string).lower()


class CamelCase:
    def __setattr__(self, attr, value):
        return BaseThingy.__setattr__(self, camelize(attr), value)

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, camelize(attr))
        except AttributeError:
            return BaseThingy.__getattribute__(self, uncamelize(attr))
