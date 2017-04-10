import mongomock

from mongo_thingy import Model


def test_collection():
    collection = mongomock.MongoClient().database.collection

    class Foo(Model):
        _collection = collection

    assert Foo.collection == collection


def test_get_database_from_table():
    collection = mongomock.MongoClient().database.collection

    class Foo(Model):
        _collection = collection

    assert isinstance(Foo.database, mongomock.Database)


def test_get_table_from_database():
    database = mongomock.MongoClient().database

    class Foo(Model):
        _database = database

    assert Foo.collection_name == "foo"
