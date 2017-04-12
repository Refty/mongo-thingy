import pytest
from bson import ObjectId
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


def test_thingy_count(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert({"bar": "baz"})
    assert Foo.count() == 1

    collection.remove()
    assert Foo.count() == 0


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


def test_thingy_distinct(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    assert Foo.distinct("bar") == ["baz", "qux"]

    collection.insert({"bar": None})
    assert None in Foo.distinct("bar")


def test_thingy_find(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    cursor = Foo.find()
    assert cursor.count() == 2

    foo = cursor.next()
    assert isinstance(foo, Foo)
    assert foo.bar == "baz"


def test_thingy_find_one(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    foo = Foo.find_one()
    assert isinstance(foo, Foo)
    assert foo.bar == "baz"


def test_thingy_repr():
    thingy = eval(repr(Thingy(bar="baz")))
    assert isinstance(thingy, Thingy)
    assert thingy.bar == "baz"


def test_thingy_id(collection):
    thingy = Thingy({"_id": "foo"})
    assert thingy._id == thingy.id == "foo"

    thingy.id = "bar"
    assert thingy._id == thingy.id == "bar"

    thingy = Thingy({"id": "foo"})
    assert thingy.id == "foo"
    assert thingy._id is None

    thingy.id = "bar"
    assert thingy.id == "bar"
    assert thingy._id is None

    thingy._id = "qux"
    assert thingy.id == "bar"
    assert thingy._id == "qux"


def test_thingy_save(collection):
    class Foo(Thingy):
        _collection = collection

    foo = Foo(bar="baz")
    assert Foo.count() == 0
    foo.save()
    assert Foo.count() == 1
    assert isinstance(foo._id, ObjectId)

    foo = Foo(id="bar", bar="qux").save()
    assert isinstance(foo, Foo)
    assert foo.bar == "qux"
    assert foo._id == "bar"


def test_thingy_delete(collection):
    class Foo(Thingy):
        _collection = collection

    foo = Foo(bar="baz").save()
    assert Foo.count() == 1
    foo.delete()
    assert Foo.count() == 0
