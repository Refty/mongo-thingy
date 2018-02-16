from mongo_thingy import Thingy
from mongo_thingy.cursor import Cursor


def test_cursor_bind(collection):
    cursor = Cursor(collection)
    result = cursor.bind({"foo": "bar"})
    assert isinstance(result, dict)
    assert result["foo"] == "bar"

    class Foo(Thingy):
        _collection = collection

    cursor = Cursor(collection, thingy_cls=Foo)
    result = cursor.bind({"foo": "bar"})
    assert isinstance(result, Foo)
    assert result.foo == "bar"


def test_cursor_getitem(collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])

    cursor = Cursor(collection)

    result = cursor[0]
    assert isinstance(result, dict)
    assert result["bar"] == "baz"

    result = cursor[1]
    assert isinstance(result, dict)
    assert result["bar"] == "qux"

    class Foo(Thingy):
        _collection = collection

    cursor = Cursor(collection, thingy_cls=Foo)

    result = cursor[0]
    assert isinstance(result, Foo)
    assert result.bar == "baz"

    result = cursor[1]
    assert isinstance(result, Foo)
    assert result.bar == "qux"


def test_cursor_next(collection):
    class Foo(Thingy):
        _collection = collection

    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    cursor = Cursor(collection, thingy_cls=Foo)

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

    for dictionnary in Cursor(collection, thingy_cls=Foo, view="empty"):
        assert dictionnary == {}

    for dictionnary in Cursor(collection, thingy_cls=Foo).view("empty"):
        assert dictionnary == {}

    for dictionnary in Foo.find(view="empty"):
        assert dictionnary == {}

    for dictionnary in Foo.find().view("empty"):
        assert dictionnary == {}
