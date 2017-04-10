from pymongo import MongoClient

from mongo_thingy import connect, Model


def test_connect():
    assert Model.client is None
    connect()
    assert isinstance(Model.client, MongoClient)
