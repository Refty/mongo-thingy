import pytest
from pymongo import MongoClient
from pymongo.database import Database

from mongo_thingy import connect, Thingy


def test_thingy_collection(collection):
    class Foo(Thingy):
        _collection = collection

    assert Foo.collection == collection


def test_thingy_get_database_from_table(collection):
    class Foo(Thingy):
        _collection = collection

    assert isinstance(Foo.database, Database)


def test_thingy_names(client):
    class FooBar(Thingy):
        pass

    with pytest.raises(AttributeError):
        FooBar.database

    FooBar.client = client
    assert FooBar.database == FooBar.client.foo
    assert FooBar.collection == FooBar.client.foo.bar
    assert FooBar.database_name == "foo"
    assert FooBar.collection_name == "bar"


def test_thingy_get_table_from_database(database):
    class Foo(Thingy):
        _database = database

    assert Foo.collection_name == "foo"


def test_thingy_get_from_name(client):
    class Bar(Thingy):
        _database = client["foo"]

    assert Bar.collection == Bar.database.bar


@pytest.mark.parametrize("connect", [connect, Thingy.connect])
def test_thingy_connect_disconnect(connect):
    assert Thingy.client is None

    connect()
    assert isinstance(Thingy.client, MongoClient)
    assert Thingy._database is None

    Thingy.disconnect()
    assert Thingy.client is None

    connect("mongodb://hostname/database")
    assert isinstance(Thingy.client, MongoClient)
    assert Thingy.database
    assert Thingy.database.name == "database"
    Thingy.disconnect()

    assert Thingy.client is None
    assert Thingy._database is None
    with pytest.raises(AttributeError):
        Thingy.database
