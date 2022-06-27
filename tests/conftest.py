import pytest
from pymongo import MongoClient

from mongo_thingy import Thingy
from mongo_thingy.versioned import Revision, Versioned

try:
    from mongomock import MongoClient as MongomockClient
except ImportError:
    MongomockClient = None

try:
    from montydb import MontyClient
except ImportError:
    MontyClient = None

backends = {
    "pymongo": MongoClient,
    "mongomock": MongomockClient,
    "montydb": MontyClient,
}


def pytest_addoption(parser):
    help = "Test a single backend. Choices: {}".format(", ".join(backends))
    parser.addoption("--backend", choices=backends.keys(), help=help)


def pytest_generate_tests(metafunc):
    if "backend" in metafunc.fixturenames:
        _backends = backends.keys()

        option = metafunc.config.getoption("backend")
        if option:
            _backends = [option]

        marker = metafunc.definition.get_closest_marker("ignore_backends")
        if marker:
            _backends = [b for b in _backends if b not in marker.args]

        metafunc.parametrize("backend", _backends)


@pytest.fixture
def client_cls(backend):
    client_cls = backends[backend]
    if client_cls is None:
        pytest.skip()
    Thingy.client_cls = client_cls
    return client_cls


@pytest.fixture
def client(backend, client_cls):
    if backend == "montydb":
        return client_cls(":memory:")
    return client_cls("mongodb://localhost")


@pytest.fixture
def database(client):
    return client.mongo_thingy_tests


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
