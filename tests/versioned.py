import pytest

from mongo_thingy.cursor import Cursor


def test_version_save(TestRevision):
    version = TestRevision().save()
    assert version.creation_date


def test_version_indexes(TestRevision):
    TestRevision.create_indexes()
    indexes = TestRevision.collection.index_information()
    assert "document_id_-1_document_type_-1" in indexes


def test_versioned_get_revisions(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    cursor = thingy.get_revisions()
    assert isinstance(cursor, Cursor)

    version = cursor[0]
    assert version.document == thingy.__dict__
    assert version.document_type == "TestVersionedThingy"


def test_versioned_author(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    assert thingy.revisions[0].author is None
    assert "author" not in thingy.revisions[0].__dict__

    thingy.bar = "qux"
    thingy.save(author={"name": "foo"})
    assert thingy.revisions[1].author == {"name": "foo"}


def test_versioned_version(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"})
    assert thingy.version == 0
    thingy.save()
    assert thingy.version == 1


def test_versioned_revisions(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    thingy.bar = "qux"
    thingy.save()

    assert thingy.revisions[0].document.get("bar") == "baz"
    assert thingy.revisions[1].document.get("bar") == "qux"

    assert thingy.revisions[-1].id == thingy.revisions[1].id
    assert thingy.revisions[-2].id == thingy.revisions[0].id

    with pytest.raises(IndexError):
        thingy.revisions[-3]


def test_versioned_revisions_operation(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    assert thingy.revisions[0].operation == "create"

    thingy.bar = "qux"
    thingy.save()
    assert thingy.revisions[1].operation == "update"

    thingy.delete()
    assert thingy.revisions[2].operation == "delete"


def test_versioned_versioned(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"})
    assert thingy.versioned is False

    thingy.bar = "qux"
    assert thingy.versioned is False

    thingy.save()
    assert thingy.versioned is True


def test_versioned_revert(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    assert thingy.version == 1

    thingy.revert()
    assert thingy.version == 2
    assert thingy.bar is None

    thingy.revert()
    assert thingy.version == 3
    assert thingy.bar == "baz"
