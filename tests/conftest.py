import importlib

import pytest

from mongo_thingy import Thingy
from mongo_thingy.versioned import Revision, Versioned

backends = ("pymongo", "mongomock")

for backend in backends:
    try:
        module = importlib.import_module(backend)
    except ImportError:
        module = None
    globals()[backend] = module


def pytest_addoption(parser):
    help = "Test a single backend. Choices: {}".format(", ".join(backends))
    parser.addoption("--backend", choices=backends, help=help)


def pytest_generate_tests(metafunc):
    if "backend" in metafunc.fixturenames:
        _backends = backends

        option = metafunc.config.getoption("backend")
        if option:
            _backends = [option]

        marker = metafunc.definition.get_closest_marker("ignore_backends")
        if marker:
            _backends = [b for b in _backends if b not in marker.args]

        metafunc.parametrize("backend", _backends)


@pytest.fixture
def client_cls(backend):
    try:
        if backend == "pymongo":
            Thingy.client_cls = pymongo.MongoClient
        if backend == "mongomock":
            Thingy.client_cls = mongomock.MongoClient
    except AttributeError:
        pytest.skip()

    return Thingy.client_cls


@pytest.fixture
def client(client_cls):
    return client_cls("mongodb://localhost/mongo_thingy_tests")


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
