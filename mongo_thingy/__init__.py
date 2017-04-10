from pymongo import MongoClient

from .model import Model


def connect(*args, **kwargs):
    client = MongoClient(*args, **kwargs)
    Model.client = client
    return client
