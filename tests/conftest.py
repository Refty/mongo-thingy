import pytest
from pymongo import MongoClient

from mongo_thingy import Thingy
from mongo_thingy.versioned import Revision, Versioned


@pytest.fixture
def client():
    return MongoClient("mongodb://localhost/mongo_thingy_tests")


@pytest.fixture
def database(client):
    database = client.get_default_database()
    yield database
    client.drop_database(database.name)


@pytest.fixture
def collection(request, database):
    return database[request.node.name]


@pytest.fixture
def TestThingy(collection):
    class TestThingy(Thingy):
        _collection = collection

    return TestThingy


@pytest.fixture
def TestRevision(database):
    class TestRevision(Revision):
        _database = database

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


__all__ = ["TestThingy", "TestRevision", "TestVersioned", "TestVersionedThingy",
           "client", "database", "collection"]
