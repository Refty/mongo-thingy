from collections import OrderedDict
from mongo_thingy.cursor import Cursor


def test_cursor(collection):
    collection.insert_many([{"bar": "baz"},
                            {"bar": "qux"}])
    cursor = Cursor(OrderedDict, collection)

    result = cursor[0]
    assert isinstance(result, OrderedDict)
    assert result["bar"] == "baz"

    result = cursor.next()
    assert isinstance(result, OrderedDict)
    assert result["bar"] == "baz"

    result = cursor.__next__()
    assert isinstance(result, OrderedDict)
    assert result["bar"] == "qux"
