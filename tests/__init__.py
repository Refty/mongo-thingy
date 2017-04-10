import mongomock
from pymongo import MongoClient

from mongo_thingy import connect, Thingy


def test_thingy_collection():
    collection = mongomock.MongoClient().database.collection

    class Foo(Thingy):
        _collection = collection

    assert Foo.collection == collection


def test_thingy_get_database_from_table():
    collection = mongomock.MongoClient().database.collection

    class Foo(Thingy):
        _collection = collection

    assert isinstance(Foo.database, mongomock.Database)


def test_thingy_get_table_from_database():
    database = mongomock.MongoClient().database

    class Foo(Thingy):
        _database = database

    assert Foo.collection_name == "foo"


def test_connect():
    assert Thingy.client is None
    connect()
    assert isinstance(Thingy.client, MongoClient)
