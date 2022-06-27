import pytest
from pymongo import MongoClient

from mongo_thingy import Thingy
from mongo_thingy.versioned import Revision, Versioned


@pytest.fixture
def client():
    return MongoClient("mongodb://localhost/mongo_thingy_tests")


@pytest.fixture
def database(client):
    return client.get_database()


@pytest.fixture
def collection(request, database):
    collection = database[request.node.name]
    collection.delete_many({})
    return collection


@pytest.fixture
def TestThingy(collection):
    class TestThingy(Thingy):
        _collection = collection

    return TestThingy


@pytest.fixture
def TestRevision(database):
    class TestRevision(Revision):
        _database = database

    TestRevision.collection.delete_many({})
    return TestRevision


@pytest.fixture
def TestVersioned(TestRevision):
    class TestVersioned(Versioned):
        _revision_cls = TestRevision

    return TestVersioned


@pytest.fixture
def TestVersionedThingy(TestVersioned, TestThingy):
    class TestVersionedThingy(TestVersioned, TestThingy):
        pass

    return TestVersionedThingy


__all__ = ["TestThingy", "TestRevision", "TestVersioned",
           "TestVersionedThingy", "client", "database", "collection"]
