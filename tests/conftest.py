import pytest
from pymongo import MongoClient


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


__all__ = ["client", "database", "collection"]
