import pytest
from pymongo.errors import InvalidOperation

from mongo_thingy import Thingy
from mongo_thingy.cursor import _Proxy, _BindingProxy, _ChainingProxy, Cursor


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


def test_cursor_first(collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])

    cursor = Cursor(collection.find())

    result = cursor.first()
    assert isinstance(result, dict)
    assert result["bar"] == "baz"

    with pytest.raises(InvalidOperation):
        cursor.first()

    class Foo(Thingy):
        _collection = collection

    cursor = Cursor(collection.find(), thingy_cls=Foo)

    result = cursor.first()
    assert isinstance(result, Foo)
    assert result.bar == "baz"

    with pytest.raises(InvalidOperation):
        cursor.first()


def test_cursor_getitem(collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])

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
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])

    cursor = Cursor(collection.find())

    clone = cursor.clone()
    assert clone is not cursor
    assert clone.delegate is not cursor.delegate

    cursor.skip(1)
    assert cursor[0]["bar"] == "qux"
    assert clone[0]["bar"] == "baz"
    assert cursor.clone()[0]["bar"] == "qux"


def test_cursor_next(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    cursor = Cursor(collection.find(), thingy_cls=Foo)

    result = cursor.next()
    assert isinstance(result, Foo)
    assert result.bar == "baz"

    result = cursor.__next__()
    assert isinstance(result, Foo)
    assert result.bar == "qux"


def test_cursor_view(collection):
    class Foo(Thingy):
        _collection = collection

    Foo.add_view("empty")
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])

    for dictionnary in Cursor(collection.find(), thingy_cls=Foo, view="empty"):
        assert dictionnary == {}

    for dictionnary in Cursor(collection.find(), thingy_cls=Foo).view("empty"):
        assert dictionnary == {}

    for dictionnary in Foo.find(view="empty"):
        assert dictionnary == {}

    for dictionnary in Foo.find().view("empty"):
        assert dictionnary == {}
