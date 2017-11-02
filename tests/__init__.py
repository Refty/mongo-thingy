import pytest
from bson import ObjectId
from pymongo import MongoClient

from mongo_thingy import Thingy, connect, create_indexes, disconnect, registry


def test_thingy_database(TestThingy, database):
    assert TestThingy.database == database


def test_thingy_collection(TestThingy, collection):
    assert TestThingy.collection == collection


def test_thingy_names(client):
    class FooBar(Thingy):
        pass

    with pytest.raises(AttributeError):
        FooBar.database

    FooBar._client = client
    assert FooBar.database == FooBar.client.foo
    assert FooBar.collection == FooBar.client.foo.bar
    assert FooBar.database_name == "foo"
    assert FooBar.collection_name == "bar"


def test_thingy_database_name(client, database):
    class FooBar(Thingy):
        _client = client
        _database_name = "fuu"

    assert FooBar.database_name == "fuu"

    class FooBar(Thingy):
        _database = database

    assert FooBar.database_name == database.name


def test_thingy_collection_name(client, collection):
    class FooBar(Thingy):
        _client = client
        _collection_name = "baz"

    assert FooBar.collection_name == "baz"

    class FooBar(Thingy):
        _collection = collection

    assert FooBar.collection_name == collection.name


def test_thingy_database_from_collection(collection):
    class Foo(Thingy):
        _collection = collection

    assert Foo.database == collection.database


def test_thingy_collection_from_database(database):
    class Foo(Thingy):
        _database = database

    assert Foo.collection == database.foo


def test_thingy_database_from_name(client):
    class FooBar(Thingy):
        _client = client

    assert FooBar.database == client.foo


def test_thingy_collection_from_name(database):
    class Bar(Thingy):
        _database = database

    assert Bar.collection == database.bar


def test_thingy_add_index(collection):
    class Foo(Thingy):
        _collection = collection

    Foo.add_index("foo", unique=True)
    assert Foo._indexes == [("foo", {"unique": True, "background": True})]

    Foo._indexes = []
    Foo.add_index("foo", unique=True, background=False)
    assert Foo._indexes == [("foo", {"unique": True, "background": False})]


def test_thingy_count(TestThingy, collection):
    collection.insert({"bar": "baz"})
    assert TestThingy.count() == 1

    collection.remove()
    assert TestThingy.count() == 0


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


def test_thingy_create_index(TestThingy, collection):
    TestThingy.create_index("foo", unique=True)
    assert TestThingy._indexes == [
        ("foo", {"unique": True, "background": True})
    ]

    indexes = collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


def test_thingy_create_indexes(TestThingy, collection):
    class Foo(TestThingy):
        _indexes = [("foo", {"unique": True, "background": True})]

    Foo.create_indexes()
    indexes = collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


def test_thingy_distinct(TestThingy, collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    assert TestThingy.distinct("bar") == ["baz", "qux"]

    collection.insert({"bar": None})
    assert None in TestThingy.distinct("bar")


def test_thingy_find(TestThingy, collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    cursor = TestThingy.find()
    assert cursor.count() == 2

    thingy = cursor.next()
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baz"


def test_thingy_find_one(TestThingy, collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    thingy = TestThingy.find_one()
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baz"

    thingy = TestThingy.find_one(max_time_ms=10)
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baz"

    thingy = TestThingy.find_one(thingy.id)
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baz"

    thingy = TestThingy.find_one({"bar": "qux"})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "qux"

    thingy = TestThingy.find_one({"bar": "quux"})
    assert thingy is None


def test_thingy_find_one_and_replace(TestThingy, collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    thingy = TestThingy.find_one_and_replace({"bar": "baz"}, {"bar": "baaz"})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaz"


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


def test_thingy_save(TestThingy, collection):
    thingy = TestThingy(bar="baz")
    assert TestThingy.count() == 0
    thingy.save()
    assert TestThingy.count() == 1
    assert isinstance(thingy._id, ObjectId)

    thingy = TestThingy(id="bar", bar="qux").save()
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "qux"
    assert thingy._id == "bar"


def test_thingy_delete(TestThingy, collection):
    thingy = TestThingy(bar="baz").save()
    assert TestThingy.count() == 1
    thingy.delete()
    assert TestThingy.count() == 0


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


def test_github_issue_6(client):
    class SynchronisedSwimming(Thingy):
        _client = client

    assert SynchronisedSwimming.database.name == "synchronised"
    assert SynchronisedSwimming.collection.name == "swimming"

    SynchronisedSwimming._database_name = "sport"
    assert SynchronisedSwimming.database.name == "sport"
    assert SynchronisedSwimming.collection.name == "synchronised_swimming"
