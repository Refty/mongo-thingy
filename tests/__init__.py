import asyncio
from datetime import datetime, timezone

import pytest
from bson import ObjectId

from mongo_thingy import (
    Thingy,
    ThingyList,
    connect,
    create_indexes,
    disconnect,
    registry,
)


async def test_thingy_list_distinct_thingies():
    foos = ThingyList()
    foos.append(Thingy())
    foos.append(Thingy())
    foos.append(Thingy(bar="baz"))
    foos.append(Thingy(bar="qux"))

    distinct = foos.distinct("bar")
    assert distinct.count(None) == 1
    assert distinct == [None, "baz", "qux"]


async def test_thingy_list_distinct_dicts():
    foos = ThingyList()
    foos.append({})
    foos.append({})
    foos.append({"bar": "baz"})
    foos.append({"bar": "qux"})

    distinct = foos.distinct("bar")
    assert distinct.count(None) == 1
    assert distinct == [None, "baz", "qux"]


# https://mongodb.com/docs/manual/reference/method/db.collection.distinct/#array-fields
async def test_thingy_list_distinct_array_fields():
    foos = ThingyList()
    foos.append(Thingy())
    foos.append(Thingy())
    foos.append(Thingy(bar=[1, 2]))
    foos.append(Thingy(bar=[2, 3, [3]]))

    distinct = foos.distinct("bar")
    assert distinct.count(None) == 1
    assert distinct == [None, 1, 2, 3, [3]]


async def test_thingy_list_view():
    class Foo(Thingy):
        pass

    Foo.add_view("empty")
    foos = ThingyList()
    foos.append(Foo(bar="baz"))
    foos.append(Foo(bar="qux"))

    for foo in foos.view("empty"):
        assert foo == {}

    foos.append({})
    with pytest.raises(TypeError):
        foos.view("empty")


@pytest.mark.all_backends
async def test_base_thingy_database(TestThingy, database):
    assert TestThingy.database == database


@pytest.mark.all_backends
async def test_base_thingy_client(TestThingy, client):
    assert TestThingy.client == client


@pytest.mark.all_backends
async def test_base_thingy_collection(TestThingy, collection):
    assert TestThingy.collection == collection


@pytest.mark.all_backends
async def test_base_thingy_names(thingy_cls, client):
    class FooBar(thingy_cls):
        pass

    with pytest.raises(AttributeError):
        FooBar.database

    FooBar._client = client
    assert FooBar.database == FooBar.client.foo
    assert FooBar.collection == FooBar.client.foo.bar
    assert FooBar.database_name == "foo"
    assert FooBar.collection_name == "bar"


@pytest.mark.all_backends
async def test_base_thingy_database_name(thingy_cls, client, database):
    class FooBar(thingy_cls):
        _client = client
        _database_name = "fuu"

    assert FooBar.database_name == "fuu"

    class FooBar(thingy_cls):
        _database = database

    assert FooBar.database_name == database.name


@pytest.mark.all_backends
async def test_base_thingy_collection_name(thingy_cls, client, collection):
    class FooBar(thingy_cls):
        _client = client
        _collection_name = "baz"

    assert FooBar.collection_name == "baz"

    class FooBar(thingy_cls):
        _collection = collection

    assert FooBar.collection_name == collection.name


@pytest.mark.all_backends
async def test_base_thingy_database_from_client(thingy_cls, client):
    class FooBar(thingy_cls):
        _client = client

    assert FooBar.database == client.foo


@pytest.mark.all_backends
async def test_base_thingy_database_from_collection(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    assert Foo.database == collection.database


@pytest.mark.all_backends
async def test_base_thingy_client_from_database(thingy_cls, database):
    class Foo(thingy_cls):
        _database = database

    assert Foo.client == database.client


@pytest.mark.all_backends
async def test_base_thingy_collection_from_database(thingy_cls, database):
    class Foo(thingy_cls):
        _database = database

    assert Foo.collection == database.foo


@pytest.mark.all_backends
async def test_base_thingy_database_from_name(thingy_cls, client):
    class FooBar(thingy_cls):
        _client = client

    assert FooBar.database == client.foo


@pytest.mark.all_backends
async def test_base_thingy_collection_from_name(thingy_cls, database):
    class Bar(thingy_cls):
        _database = database

    assert Bar.collection == database.bar


@pytest.mark.all_backends
async def test_base_thingy_add_index(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    Foo.add_index("foo", unique=True)
    assert Foo._indexes == [("foo", {"unique": True, "background": True})]

    Foo._indexes = []
    Foo.add_index("foo", unique=True, background=False)
    assert Foo._indexes == [("foo", {"unique": True, "background": False})]


def test_thingy_count_documents(TestThingy, collection):
    collection.insert_one({"bar": "baz"})
    collection.insert_one({"foo": "bar"})

    with pytest.deprecated_call():
        TestThingy.count()

    assert TestThingy.count_documents() == 2
    assert TestThingy.count_documents({"foo": "bar"}) == 1


async def test_async_thingy_count_documents(TestThingy, collection):
    await collection.insert_one({"bar": "baz"})
    await collection.insert_one({"foo": "bar"})

    with pytest.deprecated_call():
        await TestThingy.count()

    assert await TestThingy.count_documents() == 2
    assert await TestThingy.count_documents({"foo": "bar"}) == 1


@pytest.mark.ignore_backends("montydb")
def test_connect_disconnect(thingy_cls, client_cls):
    connect(client_cls=client_cls)
    assert isinstance(thingy_cls.client, client_cls)
    assert thingy_cls._database.name == "test"
    disconnect()

    connect(client_cls=client_cls, database_name="database")
    assert isinstance(thingy_cls.client, client_cls)
    assert thingy_cls._database.name == "database"
    disconnect()

    thingy_cls._client_cls = client_cls
    connect()
    assert isinstance(thingy_cls.client, client_cls)
    disconnect()

    connect("mongodb://hostname/database")
    assert thingy_cls.database is not None
    assert thingy_cls.database.name == "database"
    disconnect()

    assert thingy_cls._client is None
    with pytest.raises(AttributeError):
        thingy_cls.client

    assert thingy_cls._database is None
    with pytest.raises(AttributeError):
        thingy_cls.database


@pytest.mark.ignore_backends("montydb")
def test_thingy_create_index(TestThingy, collection):
    TestThingy.create_index("foo", unique=True)

    indexes = collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


async def test_async_thingy_create_index(TestThingy, collection):
    await TestThingy.create_index("foo", unique=True)

    indexes = await collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


@pytest.mark.ignore_backends("montydb")
def test_thingy_create_indexes(TestThingy, collection):
    class Foo(TestThingy):
        _indexes = [("foo", {"unique": True, "background": True})]

    Foo.create_indexes()
    indexes = collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


async def test_async_thingy_create_indexes(TestThingy, collection):
    class Foo(TestThingy):
        _indexes = [("foo", {"unique": True, "background": True})]

    await Foo.create_indexes()
    indexes = await collection.index_information()
    assert "_id_" in indexes
    assert "foo_1" in indexes
    assert len(indexes) == 2


def test_thingy_distinct(TestThingy, collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    assert set(TestThingy.distinct("bar")) == {"baz", "qux"}

    collection.insert_one({"bar": None})
    assert None in TestThingy.distinct("bar")


async def test_async_thingy_distinct(TestThingy, collection):
    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    assert set(await TestThingy.distinct("bar")) == {"baz", "qux"}

    await collection.insert_one({"bar": None})
    assert None in await TestThingy.distinct("bar")


def test_thingy_find(TestThingy, collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    cursor = TestThingy.find()
    assert len(list(cursor.clone())) == 2

    thingy = cursor.next()
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baz"


async def test_async_thingy_find(TestThingy, collection):
    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    cursor = TestThingy.find()
    assert len(await cursor.clone().to_list(length=10)) == 2

    thingy = await cursor.next()
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baz"


def test_thingy_find_one(TestThingy, collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
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


def test_thingy_delete_many(TestThingy, collection):
    collection.insert_many(
        [{"foo": "bar"}, {"bar": "qux"}, {"bar": "baz"}, {"bar": "baz"}]
    )
    TestThingy.delete_many({"foo": "bar"})
    assert TestThingy.find_one({"foo": "bar"}) is None

    assert TestThingy.find_one({"bar": "qux"})

    TestThingy.delete_many({"bar": "baz"})
    assert TestThingy.find_one({"bar": "baz"}) is None


def test_thingy_delete_one(TestThingy, collection):
    collection.insert_many(
        [{"foo": "bar"}, {"bar": "qux"}, {"bar": "baz"}, {"bar": "baz"}]
    )
    TestThingy.delete_one({"foo": "bar"})
    assert TestThingy.find_one({"foo": "bar"}) is None

    qux = TestThingy.find_one({"bar": "qux"})

    TestThingy.delete_one(qux.id)
    assert TestThingy.find_one({"bar": "qux"}) is None

    TestThingy.delete_one(qux.id)
    assert TestThingy.find_one({"bar": "qux"}) is None

    TestThingy.delete_one({"bar": "baz"})
    assert TestThingy.find_one({"bar": "baz"}) is not None
    TestThingy.delete_one({"bar": "baz"})
    assert TestThingy.find_one({"bar": "baz"}) is None


def test_thingy_update_many(TestThingy, collection):
    collection.insert_many(
        [{"foo": "bar"}, {"bar": "qux"}, {"bar": "baz"}, {"bar": "baz"}]
    )
    updated = TestThingy.update_many({"bar": "baz"}, {"$set": {"bar": "baaz"}})
    assert updated.acknowledged
    assert updated.matched_count == 2
    assert updated.modified_count == 2
    assert TestThingy.find_one({"bar": "baz"}) is None

    updated = TestThingy.update_many(
        {"new": "new"}, {"$set": {"bar": "baaz"}}, upsert=False
    )
    assert updated.acknowledged
    assert updated.matched_count == 0
    assert updated.modified_count == 0
    assert TestThingy.find_one({"new": "new"}) is None

    updated = TestThingy.update_many(
        {"new": "new"}, {"$set": {"bar": "baaz"}}, upsert=True
    )
    assert updated.acknowledged
    assert updated.matched_count == 0
    assert updated.modified_count == 0
    assert TestThingy.find_one({"new": "new"}).bar == "baaz"

    updated = TestThingy.update_many(
        {"new": "new"}, {"$set": {"already": "exists"}}, upsert=True
    )
    assert updated.acknowledged
    assert updated.matched_count == 1
    assert updated.modified_count == 1
    new = TestThingy.find_one({"new": "new"})
    assert new.already == "exists"
    assert new.bar == "baaz"


def test_thingy_update_one(TestThingy, collection):
    collection.insert_many(
        [{"foo": "bar"}, {"bar": "qux"}, {"bar": "baz"}, {"bar": "baz"}]
    )
    updated = TestThingy.update_one({"bar": "baz"}, {"$set": {"bar": "baaz"}})
    assert updated.acknowledged
    assert updated.matched_count == 1
    assert updated.modified_count == 1
    assert TestThingy.find_one({"bar": "baz"}) is not None

    updated = TestThingy.update_one({"bar": "baz"}, {"$set": {"bar": "baaz"}})
    assert updated.acknowledged
    assert updated.matched_count == 1
    assert updated.modified_count == 1
    assert TestThingy.find_one({"bar": "baz"}) is None

    foo = TestThingy.find_one({"foo": "bar"})
    TestThingy.update_one(foo.id, {"$set": {"new_field": "foo"}})
    assert updated.acknowledged
    assert updated.matched_count == 1
    assert updated.modified_count == 1
    thingy = TestThingy.find_one({"foo": "bar"})
    assert thingy.foo == "bar"
    assert thingy.new_field == "foo"

    updated = TestThingy.update_one(
        {"new": "new"}, {"$set": {"bar": "baaz"}}, upsert=False
    )
    assert updated.acknowledged
    assert updated.matched_count == 0
    assert updated.modified_count == 0
    assert TestThingy.find_one({"new": "new"}) is None

    updated = TestThingy.update_one(
        {"new": "new"}, {"$set": {"bar": "baaz"}}, upsert=True
    )
    assert updated.acknowledged
    assert updated.matched_count == 0
    assert updated.modified_count == 0
    assert TestThingy.find_one({"new": "new"}).bar == "baaz"

    updated = TestThingy.update_one(
        {"new": "new"}, {"$set": {"already": "exists"}}, upsert=True
    )
    assert updated.acknowledged
    assert updated.matched_count == 1
    assert updated.modified_count == 1
    new = TestThingy.find_one({"new": "new"})
    assert new.already == "exists"
    assert new.bar == "baaz"


@pytest.mark.ignore_backends("montydb")
def test_thingy_find_one_and_replace(TestThingy, collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    thingy = TestThingy.find_one_and_replace({"bar": "baz"}, {"bar": "baaz"})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaz"

    thingy = TestThingy.find_one_and_replace(thingy.id, {"bar": "baaaz"})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaaz"


async def test_async_thingy_find_one_and_replace(TestThingy, collection):
    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    thingy = await TestThingy.find_one_and_replace({"bar": "baz"}, {"bar": "baaz"})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaz"

    thingy = await TestThingy.find_one_and_replace(thingy.id, {"bar": "baaaz"})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaaz"


@pytest.mark.ignore_backends("montydb")
def test_thingy_find_one_and_update(TestThingy, collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    thingy = TestThingy.find_one_and_update({"bar": "baz"}, {"$set": {"bar": "baaz"}})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaz"

    thingy = TestThingy.find_one_and_update(thingy.id, {"$set": {"bar": "baaaz"}})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaaz"


async def test_async_thingy_find_one_and_update(TestThingy, collection):
    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    thingy = await TestThingy.find_one_and_update(
        {"bar": "baz"}, {"$set": {"bar": "baaz"}}
    )
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaz"

    thingy = await TestThingy.find_one_and_update(thingy.id, {"$set": {"bar": "baaaz"}})
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "baaaz"


@pytest.mark.all_backends
async def test_base_thingy_id(thingy_cls, collection):
    thingy = thingy_cls({"_id": "foo"})
    assert thingy._id == thingy.id == "foo"

    thingy.id = "bar"
    assert thingy._id == thingy.id == "bar"

    thingy = thingy_cls({"id": "foo"})
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
    assert TestThingy.count_documents() == 0
    thingy.save()
    assert TestThingy.count_documents() == 1
    assert isinstance(thingy._id, ObjectId)

    thingy = TestThingy(id="bar", bar="qux").save()
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "qux"
    assert thingy._id == "bar"


@pytest.mark.only_backends("pymongo")
def test_thingy_save_refresh(TestThingy):
    created_at = datetime.now(timezone.utc)

    thingy = TestThingy(created_at=created_at).save()
    assert thingy.created_at == created_at

    thingy = thingy.save(refresh=True)
    assert thingy.created_at != created_at

    approx = created_at.replace(microsecond=0, tzinfo=None)
    saved_approx = thingy.created_at.replace(microsecond=0, tzinfo=None)
    assert approx == saved_approx

    assert TestThingy.find_one().created_at != created_at
    assert TestThingy.find_one().created_at == thingy.created_at


async def test_async_thingy_save(TestThingy, collection):
    thingy = TestThingy(bar="baz")
    assert await TestThingy.count_documents() == 0
    await thingy.save()
    assert await TestThingy.count_documents() == 1
    assert isinstance(thingy._id, ObjectId)

    thingy = await TestThingy(id="bar", bar="qux").save()
    assert isinstance(thingy, TestThingy)
    assert thingy.bar == "qux"
    assert thingy._id == "bar"


@pytest.mark.only_backends("motor_asyncio", "motor_tornado")
async def test_async_thingy_save_refresh(TestThingy):
    created_at = datetime.now(timezone.utc)

    thingy = await TestThingy(created_at=created_at).save()
    assert thingy.created_at == created_at

    thingy = await thingy.save(refresh=True)
    assert thingy.created_at != created_at

    approx = created_at.replace(microsecond=0, tzinfo=None)
    saved_approx = thingy.created_at.replace(microsecond=0, tzinfo=None)
    assert approx == saved_approx

    assert (await TestThingy.find_one()).created_at != created_at
    assert (await TestThingy.find_one()).created_at == thingy.created_at


def test_thingy_save_force_insert(TestThingy, collection):
    thingy = TestThingy().save(force_insert=True)

    with pytest.raises(Exception, match="[dD]uplicate [kK]ey [eE]rror"):
        TestThingy(_id=thingy._id, bar="qux").save(force_insert=True)

    assert TestThingy.count_documents() == 1


async def test_async_thingy_save_force_insert(TestThingy, collection):
    thingy = await TestThingy().save(force_insert=True)

    with pytest.raises(Exception, match="[dD]uplicate [kK]ey [eE]rror"):
        await TestThingy(_id=thingy._id, bar="qux").save(force_insert=True)

    assert await TestThingy.count_documents() == 1


def test_versioned_thingy_save_force_insert(TestVersionedThingy, collection):
    thingy = TestVersionedThingy().save(force_insert=True)

    with pytest.raises(Exception, match="[dD]uplicate [kK]ey [eE]rror"):
        TestVersionedThingy(_id=thingy._id, bar="qux").save(force_insert=True)

    assert TestVersionedThingy.count_documents() == 1


async def test_async_versioned_thingy_save_force_insert(
    TestVersionedThingy, collection
):
    thingy = await TestVersionedThingy().save(force_insert=True)

    with pytest.raises(Exception, match="[dD]uplicate [kK]ey [eE]rror"):
        await TestVersionedThingy(_id=thingy._id, bar="qux").save(force_insert=True)

    assert await TestVersionedThingy.count_documents() == 1


def test_thingy_delete(TestThingy, collection):
    thingy = TestThingy(bar="baz").save()
    assert TestThingy.count_documents() == 1
    thingy.delete()
    assert TestThingy.count_documents() == 0


async def test_async_thingy_delete(TestThingy, collection):
    thingy = await TestThingy(bar="baz").save()
    assert await TestThingy.count_documents() == 1
    await thingy.delete()
    assert await TestThingy.count_documents() == 0


@pytest.mark.ignore_backends("montydb")
@pytest.mark.all_backends
async def test_create_indexes(is_async, thingy_cls, database):
    del registry[:]

    class Foo(thingy_cls):
        _database = database
        _indexes = [("foo", {})]

    class Bar(thingy_cls):
        _database = database
        _indexes = [("bar", {"unique": True}), ("baz", {"sparse": True})]

    create_indexes()
    if is_async:
        await asyncio.sleep(0.1)
        assert len(await Foo.collection.index_information()) == 2
        assert len(await Bar.collection.index_information()) == 3
    else:
        assert len(Foo.collection.index_information()) == 2
        assert len(Bar.collection.index_information()) == 3


@pytest.mark.all_backends
def test_github_issue_6(thingy_cls, client):
    class SynchronisedSwimming(thingy_cls):
        _client = client

    assert SynchronisedSwimming.database.name == "synchronised"
    assert SynchronisedSwimming.collection.name == "swimming"

    SynchronisedSwimming._database_name = "sport"
    assert SynchronisedSwimming.database.name == "sport"
    assert SynchronisedSwimming.collection.name == "synchronised_swimming"
