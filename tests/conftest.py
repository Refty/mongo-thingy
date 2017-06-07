import pytest
from pymongo import MongoClient

from mongo_thingy import Thingy
from mongo_thingy.versioned import Version, Versioned


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
def TestVersion(database):
    class TestVersion(Version):
        _database = database

    return TestVersion


@pytest.fixture
def TestVersioned(TestVersion):
    class TestVersioned(Versioned):
        _version_cls = TestVersion

    return TestVersioned


@pytest.fixture
def TestVersionedThingy(TestVersioned, TestThingy):
    class TestVersionedThingy(TestVersioned, TestThingy):
        pass

    return TestVersionedThingy


__all__ = ["TestThingy", "TestVersion", "TestVersioned", "TestVersionedThingy",
           "client", "database", "collection"]
