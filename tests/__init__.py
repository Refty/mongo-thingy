import mongomock
import pytest
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


def test_thingy_names():
    class FooBar(Thingy):
        pass

    with pytest.raises(AttributeError):
        FooBar.database

    class FooBar(Thingy):
        client = mongomock.MongoClient()

    assert FooBar.database == FooBar.client.foo
    assert FooBar.collection == FooBar.client.foo.bar
    assert FooBar.database_name == "foo"
    assert FooBar.collection_name == "bar"


def test_thingy_get_table_from_database():
    database = mongomock.MongoClient().database

    class Foo(Thingy):
        _database = database

    assert Foo.collection_name == "foo"


def test_thingy_get_from_name():
    class Bar(Thingy):
        _database = mongomock.MongoClient()["foo"]

    assert Bar.collection == Bar.database.bar


def test_connect():
    assert Thingy.client is None
    connect()
    assert isinstance(Thingy.client, MongoClient)
