import os

from pymongo import MongoClient


def take_uri_from_env(var="MONGO_URI", exit_if_missing=False, **kwargs):
    def wrapper(model):
        uri = os.environ.get(var)
        if uri is None and exit_if_missing:
            exit("Missing ${} environment variable".format(var))
        db = MongoClient(uri).get_default_database()
        model._database = db
        return model
    return wrapper
