import pytest
from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database

from mongo_thingy import Thingy, connect, create_indexes, disconnect, registry


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


def test_thingy_collection_name(client):
    class FooBar(Thingy):
        collection_name = "baz"

    FooBar.client = client
    assert FooBar.collection == FooBar.client.foo.baz
    assert FooBar.collection_name == "baz"


def test_thingy_get_table_from_database(database):
    class Foo(Thingy):
        _database = database

    assert Foo.collection_name == "foo"


def test_thingy_get_from_name(client):
    class Bar(Thingy):
        _database = client["foo"]

    assert Bar.collection == Bar.database.bar


def test_thingy_add_index(collection):
    class Foo(Thingy):
        _collection = collection

    Foo.add_index("foo", unique=True)
    assert Foo._indexes == [("foo", {"unique": True, "background": True})]

    Foo._indexes = []
    Foo.add_index("foo", unique=True, background=False)
    assert Foo._indexes == [("foo", {"unique": True, "background": False})]


def test_thingy_count(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert({"bar": "baz"})
    assert Foo.count() == 1

    collection.remove()
    assert Foo.count() == 0


@pytest.mark.parametrize("connect", [connect, Thingy.connect])
@pytest.mark.parametrize("disconnect", [disconnect, Thingy.disconnect])
def test_thingy_connect_disconnect(connect, disconnect):
    assert Thingy.client is None

    connect()
    assert isinstance(Thingy.client, MongoClient)
    assert Thingy._database is None

    disconnect()
    assert Thingy.client is None

    connect("mongodb://hostname/database")
    assert isinstance(Thingy.client, MongoClient)
    assert Thingy.database
    assert Thingy.database.name == "database"
    disconnect()

    assert Thingy.client is None
    assert Thingy._database is None
    with pytest.raises(AttributeError):
        Thingy.database


def test_thingy_create_index(collection):
    class Foo(Thingy):
        _collection = collection

    Foo.create_index("foo", unique=True)
    assert Foo._indexes == [("foo", {"unique": True, "background": True})]

    indexes = collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


def test_thingy_create_indexes(collection):
    class Foo(Thingy):
        _collection = collection
        _indexes = [("foo", {"unique": True, "background": True})]

    Foo.create_indexes()
    indexes = collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


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

    foo = Foo.find_one({"bar": "qux"})
    assert isinstance(foo, Foo)
    assert foo.bar == "qux"

    foo = Foo.find_one({"bar": "quux"})
    assert foo is None


def test_thingy_find_one_and_replace(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    foo = Foo.find_one_and_replace({"bar": "baz"}, {"bar": "baaz"})
    assert isinstance(foo, Foo)
    assert foo.bar == "baaz"


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


def test_create_indexes(database):
    del registry[:]

    class Foo(Thingy):
        _database = database
        _indexes = [("foo", {})]

    class Bar(Thingy):
        _database = database
        _indexes = [("bar", {"unique": True}),
                    ("baz", {"sparse": True})]

    create_indexes()
    assert len(Foo.collection.index_information()) == 2
    assert len(Bar.collection.index_information()) == 3
