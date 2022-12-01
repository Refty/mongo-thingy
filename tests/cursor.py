import pytest

from mongo_thingy import Thingy, ThingyList
from mongo_thingy.cursor import (
    AsyncCursor,
    Cursor,
    _BindingProxy,
    _ChainingProxy,
    _Proxy,
)


def test_proxy():
    class Delegate:
        def __init__(self, value):
            self.value = value

        def foo(self, value=1):
            self.value += value
            return self.value

    class FooCursor(Cursor):
        foo = _Proxy("foo")

    delegate = Delegate(10)
    cursor = FooCursor(delegate)

    assert cursor.foo() == 11
    assert cursor.foo(4) == 15
    assert cursor.delegate.value == 15


def test_chaining_proxy():
    class Delegate:
        def __init__(self, value):
            self.value = value

        def foo(self, value=1):
            self.value += value
            return self.value

    class FooCursor(Cursor):
        foo = _ChainingProxy("foo")

    delegate = Delegate(10)
    cursor = FooCursor(delegate)

    assert cursor.foo().foo(4) is cursor
    assert cursor.delegate.value == 15


def test_binding_proxy():
    class Delegate:
        def __init__(self):
            self.document = {}

        def foo(self, key, value):
            self.document[key] = value
            return self.document

    class FooCursor(Cursor):
        foo = _BindingProxy("foo")

    cursor = FooCursor(Delegate(), thingy_cls=Thingy)
    foo = cursor.foo("bar", "baz")

    assert isinstance(foo, Thingy)
    assert foo.bar == "baz"


def test_cursor_result_cls():
    cursor = Cursor(None)
    assert cursor.result_cls == list

    class Foo(Thingy):
        pass

    cursor = Cursor(None, thingy_cls=Foo)
    assert cursor.result_cls == ThingyList

    class Foo(Thingy):
        _result_cls = set

    cursor = Cursor(None, thingy_cls=Foo)
    assert cursor.result_cls == set


def test_cursor_bind():
    cursor = Cursor(None)
    result = cursor.bind({"foo": "bar"})
    assert isinstance(result, dict)
    assert result["foo"] == "bar"

    class Foo(Thingy):
        pass

    cursor = Cursor(None, thingy_cls=Foo)
    result = cursor.bind({"foo": "bar"})
    assert isinstance(result, Foo)
    assert result.foo == "bar"


def test_cursor_first(thingy_cls, collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])

    cursor = Cursor(collection.find())

    result = cursor.first()
    assert isinstance(result, dict)
    assert result["bar"] == "baz"

    class Foo(thingy_cls):
        _collection = collection

    cursor = Cursor(collection.find(), thingy_cls=Foo).sort("_id", -1)

    result = cursor.first()
    assert isinstance(result, Foo)
    assert result.bar == "qux"

    collection.insert_one({})
    assert cursor.first() is not result

    cursor = Cursor(collection.find({"impossible": True}))
    assert cursor.first() is None


async def test_async_cursor_first(thingy_cls, collection):
    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])

    cursor = AsyncCursor(collection.find())

    result = await cursor.first()
    assert isinstance(result, dict)
    assert result["bar"] == "baz"

    class Foo(thingy_cls):
        _collection = collection

    cursor = AsyncCursor(collection.find(), thingy_cls=Foo).sort("_id", -1)

    result = await cursor.first()
    assert isinstance(result, Foo)
    assert result.bar == "qux"

    await collection.insert_one({})
    assert await cursor.first() is not result

    cursor = AsyncCursor(collection.find({"impossible": True}))
    assert await cursor.first() is None


def test_cursor_getitem(collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])

    cursor = Cursor(collection.find())

    result = cursor[0]
    assert isinstance(result, dict)
    assert result["bar"] == "baz"

    result = cursor[1]
    assert isinstance(result, dict)
    assert result["bar"] == "qux"

    class Foo(Thingy):
        _collection = collection

    cursor = Cursor(collection.find(), thingy_cls=Foo)

    result = cursor[0]
    assert isinstance(result, Foo)
    assert result.bar == "baz"

    result = cursor[1]
    assert isinstance(result, Foo)
    assert result.bar == "qux"


def test_cursor_clone(collection):
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])

    cursor = Cursor(collection.find())

    clone = cursor.clone()
    assert clone is not cursor
    assert clone.delegate is not cursor.delegate

    cursor.skip(1)
    assert cursor.first()["bar"] == "qux"
    assert clone.first()["bar"] == "baz"
    assert cursor.clone().first()["bar"] == "qux"


async def test_async_cursor_clone(collection):
    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])

    cursor = AsyncCursor(collection.find())

    clone = cursor.clone()
    assert clone is not cursor
    assert clone.delegate is not cursor.delegate

    cursor.skip(1)
    assert (await cursor.first())["bar"] == "qux"
    assert (await clone.first())["bar"] == "baz"
    assert (await cursor.clone().first())["bar"] == "qux"


def test_cursor_next(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    cursor = Cursor(collection.find(), thingy_cls=Foo)

    result = cursor.next()
    assert isinstance(result, Foo)
    assert result.bar == "baz"

    result = cursor.__next__()
    assert isinstance(result, Foo)
    assert result.bar == "qux"


async def test_async_cursor_next(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    cursor = AsyncCursor(collection.find(), thingy_cls=Foo)

    result = await cursor.next()
    assert isinstance(result, Foo)
    assert result.bar == "baz"

    result = await cursor.__anext__()
    assert isinstance(result, Foo)
    assert result.bar == "qux"


def test_cursor_to_list(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    cursor = Cursor(collection.find(), thingy_cls=Foo)

    results = cursor.to_list(length=10)
    assert isinstance(results, ThingyList)

    assert isinstance(results[0], Foo)
    assert results[0].bar == "baz"

    assert isinstance(results[1], Foo)
    assert results[1].bar == "qux"


async def test_async_cursor_to_list(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    cursor = AsyncCursor(collection.find(), thingy_cls=Foo)

    results = await cursor.to_list(length=10)
    assert isinstance(results, ThingyList)

    assert isinstance(results[0], Foo)
    assert results[0].bar == "baz"

    assert isinstance(results[1], Foo)
    assert results[1].bar == "qux"


def test_cursor_view(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    Foo.add_view("empty")
    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])

    for dictionnary in Cursor(collection.find(), thingy_cls=Foo, view="empty"):
        assert dictionnary == {}

    for dictionnary in Cursor(collection.find(), thingy_cls=Foo).view("empty"):
        assert dictionnary == {}

    for dictionnary in Foo.find(view="empty"):
        assert dictionnary == {}

    for dictionnary in Foo.find().view("empty"):
        assert dictionnary == {}


async def test_async_cursor_view(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    Foo.add_view("empty")
    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])

    async for dictionnary in AsyncCursor(
        collection.find(), thingy_cls=Foo, view="empty"
    ):
        assert dictionnary == {}

    async for dictionnary in AsyncCursor(collection.find(), thingy_cls=Foo).view(
        "empty"
    ):
        assert dictionnary == {}

    async for dictionnary in Foo.find(view="empty"):
        assert dictionnary == {}

    async for dictionnary in Foo.find().view("empty"):
        assert dictionnary == {}


@pytest.mark.ignore_backends("montydb")
def test_cursor_delete(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    Foo.find().delete()
    assert collection.count_documents({}) == 0

    collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    Foo.find({"bar": "baz"}).delete()
    assert collection.count_documents({}) == 1
    assert Foo.find_one().bar == "qux"


async def test_async_cursor_delete(thingy_cls, collection):
    class Foo(thingy_cls):
        _collection = collection

    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    await Foo.find().delete()
    assert await collection.count_documents({}) == 0

    await collection.insert_many([{"bar": "baz"}, {"bar": "qux"}])
    await Foo.find({"bar": "baz"}).delete()
    assert await collection.count_documents({}) == 1
    assert (await Foo.find_one()).bar == "qux"
