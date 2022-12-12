import inspect

import pytest
from _pytest.compat import get_real_func
from pymongo import MongoClient

from mongo_thingy import AsyncThingy, BaseThingy, Thingy
from mongo_thingy.versioned import AsyncRevision, AsyncVersioned, Revision, Versioned

try:
    from mongomock import MongoClient as MongomockClient
except ImportError:
    MongomockClient = None

try:
    from montydb import MontyClient
except ImportError:
    MontyClient = None

try:
    from motor.motor_tornado import MotorClient
except ImportError:
    MotorClient = None

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    AsyncIOMotorClient = None

try:
    from mongomock_motor import AsyncMongoMockClient
except ImportError:
    AsyncMongoMockClient = None

sync_backends = {
    "pymongo": MongoClient,
    "mongomock": MongomockClient,
    "montydb": MontyClient,
}

async_backends = {
    "motor_tornado": MotorClient,
    "motor_asyncio": AsyncIOMotorClient,
    "mongomock_motor": AsyncMongoMockClient,
}

backends = {**sync_backends, **async_backends}


def pytest_addoption(parser):
    help = "Test a single backend. Choices: {}".format(", ".join(backends))
    parser.addoption("--backend", choices=backends.keys(), help=help)


def pytest_generate_tests(metafunc):
    if "backend" in metafunc.fixturenames:
        if metafunc.definition.get_closest_marker("all_backends"):
            _backends = backends.keys()
        elif inspect.iscoroutinefunction(get_real_func(metafunc.function)):
            _backends = async_backends.keys()
        else:
            _backends = sync_backends.keys()

        option = metafunc.config.getoption("backend")
        if option:
            _backends = [b for b in _backends if b == option]

        marker = metafunc.definition.get_closest_marker("only_backends")
        if marker:
            _backends = [b for b in _backends if b in marker.args]

        marker = metafunc.definition.get_closest_marker("ignore_backends")
        if marker:
            _backends = [b for b in _backends if b not in marker.args]

        metafunc.parametrize("backend", _backends)


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--backend"):
        return items

    selected_items = []
    deselected_items = []

    for item in items:
        if (
            "backend" in item.fixturenames
            and item.callspec.getparam("backend") not in backends
        ):
            deselected_items.append(item)
        else:
            selected_items.append(item)

    config.hook.pytest_deselected(items=deselected_items)
    items[:] = selected_items


@pytest.fixture
def client_cls(backend):
    client_cls = backends[backend]
    if client_cls is None:
        pytest.skip()
    BaseThingy.client_cls = client_cls
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
def is_async(backend):
    return backend in async_backends


@pytest.fixture
async def collection(request, is_async, database):
    collection = database[request.node.name]
    if is_async:
        await collection.delete_many({})
    else:
        collection.delete_many({})
    return collection


@pytest.fixture
def thingy_cls(is_async):
    if is_async:
        return AsyncThingy
    return Thingy


@pytest.fixture
def TestThingy(thingy_cls, collection):
    class TestThingy(thingy_cls):
        _collection = collection

    return TestThingy


@pytest.fixture
def revision_cls(is_async):
    if is_async:
        return AsyncRevision
    return Revision


@pytest.fixture
async def TestRevision(is_async, revision_cls, database):
    class TestRevision(revision_cls):
        _database = database

    if is_async:
        await TestRevision.collection.delete_many({})
    else:
        TestRevision.collection.delete_many({})
    return TestRevision


@pytest.fixture
def versioned_cls(is_async):
    if is_async:
        return AsyncVersioned
    return Versioned


@pytest.fixture
def TestVersioned(versioned_cls, TestRevision):
    class TestVersioned(versioned_cls):
        _revision_cls = TestRevision

    return TestVersioned


@pytest.fixture
def TestVersionedThingy(TestVersioned, TestThingy):
    class TestVersionedThingy(TestVersioned, TestThingy):
        pass

    return TestVersionedThingy


__all__ = [
    "TestThingy",
    "TestRevision",
    "TestVersioned",
    "TestVersionedThingy",
    "client",
    "database",
    "collection",
]
