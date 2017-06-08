import pytest
from pymongo import MongoClient

from mongo_thingy import Thingy


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


__all__ = ["TestThingy", "client", "database", "collection"]
