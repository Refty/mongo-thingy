from datetime import datetime, timezone

import pytest

from mongo_thingy.camelcase import CamelCase, camelize, uncamelize


def test_camelize():
    assert camelize("_id") == "_id"
    assert camelize("__dict__") == "__dict__"
    assert camelize("foo") == "foo"
    assert camelize("foo_bar") == "fooBar"
    assert camelize("foo_bar_baz") == "fooBarBaz"
    assert camelize("fooBar") == "fooBar"


def test_uncamelize():
    assert uncamelize("_id") == "_id"
    assert uncamelize("__dict__") == "__dict__"
    assert uncamelize("foo") == "foo"
    assert uncamelize("fooBar") == "foo_bar"
    assert uncamelize("fooBAR") == "foo_bar"
    assert uncamelize("fooBarBaz") == "foo_bar_baz"
    assert uncamelize("foo_bar") == "foo_bar"


def test_camelcase(TestThingy):
    class TestCamelCaseThingy(CamelCase, TestThingy):
        pass

    thingy = TestCamelCaseThingy()
    thingy.foo_bar = 1
    assert thingy.foo_bar == 1
    assert thingy.view() == {"fooBar": 1}

    thingy.save()
    assert TestCamelCaseThingy.collection.find_one(thingy.id) == {
        "_id": thingy.id,
        "fooBar": 1,
    }

    thingy = TestCamelCaseThingy({"fooBar": 1})
    assert thingy.foo_bar == 1

    thingy.save()
    assert TestCamelCaseThingy.collection.find_one(thingy.id) == {
        "_id": thingy.id,
        "fooBar": 1,
    }


def test_camelcase_property(TestThingy):
    class TestCamelCaseThingy(CamelCase, TestThingy):
        @property
        def foo_bar(self):
            return self.foo + self.bar

    TestCamelCaseThingy.add_view("properties", include="fooBar")

    thingy = TestCamelCaseThingy(foo=1, bar=1)
    assert thingy.foo_bar == 2
    assert thingy.view("properties") == {"fooBar": 2}

    thingy.save()
    assert TestCamelCaseThingy.collection.find_one(thingy.id) == {
        "_id": thingy.id,
        "foo": 1,
        "bar": 1,
    }


@pytest.mark.only_backends("pymongo")
def test_camelcase_save_refresh(TestThingy):
    class TestCamelCaseThingy(CamelCase, TestThingy):
        pass

    created_at = datetime.now(timezone.utc)

    thingy = TestCamelCaseThingy(created_at=created_at).save()
    assert thingy.created_at == created_at

    thingy = thingy.save(refresh=True)
    assert thingy.created_at != created_at

    approx = created_at.replace(microsecond=0, tzinfo=None)
    saved_approx = thingy.created_at.replace(microsecond=0, tzinfo=None)
    assert approx == saved_approx

    assert TestCamelCaseThingy.find_one().created_at != created_at
    assert TestCamelCaseThingy.find_one().created_at == thingy.created_at
