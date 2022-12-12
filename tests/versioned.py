import pytest

from mongo_thingy.cursor import AsyncCursor, Cursor


def test_revision_save(TestRevision):
    revision = TestRevision().save()
    assert revision.creation_date


async def test_async_revision_save(TestRevision):
    revision = await TestRevision().save()
    assert revision.creation_date


@pytest.mark.ignore_backends("montydb")
def test_revision_indexes(TestRevision):
    TestRevision.create_indexes()
    indexes = TestRevision.collection.index_information()
    assert "document_id_-1_document_type_-1" in indexes


async def test_async_revision_indexes(TestRevision):
    await TestRevision.create_indexes()
    indexes = await TestRevision.collection.index_information()
    assert "document_id_-1_document_type_-1" in indexes


def test_versioned_get_revisions(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    cursor = thingy.get_revisions()
    assert isinstance(cursor, Cursor)

    revision = cursor[0]
    assert revision.document == thingy.__dict__
    assert revision.document_type == "TestVersionedThingy"


async def test_async_versioned_get_revisions(TestVersionedThingy):
    thingy = await TestVersionedThingy({"bar": "baz"}).save()
    cursor = thingy.get_revisions()
    assert isinstance(cursor, AsyncCursor)

    revision = await cursor.first()
    assert revision.document == thingy.__dict__
    assert revision.document_type == "TestVersionedThingy"


def test_versioned_author(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()

    revisions = thingy.get_revisions()
    assert revisions[0].author is None
    assert "author" not in revisions[0].__dict__

    thingy.bar = "qux"
    thingy.save(author={"name": "foo"})
    revisions = thingy.get_revisions()
    assert revisions[1].author == {"name": "foo"}


async def test_async_versioned_author(TestVersionedThingy):
    thingy = await TestVersionedThingy({"bar": "baz"}).save()

    revisions = await thingy.get_revisions().to_list(length=10)
    assert revisions[0].author is None
    assert "author" not in revisions[0].__dict__

    thingy.bar = "qux"
    await thingy.save(author={"name": "foo"})

    revisions = await thingy.get_revisions().to_list(length=10)
    assert revisions[1].author == {"name": "foo"}


def test_versioned_version(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"})
    with pytest.deprecated_call():
        thingy.version
    assert thingy.count_revisions() == 0

    thingy.save()
    assert thingy.count_revisions() == 1


async def test_async_versioned_version(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"})
    assert await thingy.count_revisions() == 0

    await thingy.save()
    assert await thingy.count_revisions() == 1


def test_versioned_revisions(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    thingy.bar = "qux"
    thingy.save()

    with pytest.deprecated_call():
        thingy.revisions

    revisions = thingy.get_revisions()
    assert revisions[0].document.get("bar") == "baz"
    assert revisions[1].document.get("bar") == "qux"

    assert revisions[-1].id == revisions[1].id
    assert revisions[-2].id == revisions[0].id

    with pytest.raises(IndexError):
        revisions[-3]


async def test_async_versioned_revisions(TestVersionedThingy):
    thingy = await TestVersionedThingy({"bar": "baz"}).save()
    thingy.bar = "qux"
    await thingy.save()

    revisions = await thingy.get_revisions().to_list(length=10)
    assert revisions[0].document.get("bar") == "baz"
    assert revisions[1].document.get("bar") == "qux"

    assert revisions[-1].id == revisions[1].id
    assert revisions[-2].id == revisions[0].id

    with pytest.raises(IndexError):
        revisions[-3]


def test_versioned_revisions_operation(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    revisions = thingy.get_revisions()
    assert revisions[0].operation == "create"

    thingy.bar = "qux"
    thingy.save()
    revisions = thingy.get_revisions()
    assert revisions[1].operation == "update"

    thingy.delete()
    revisions = thingy.get_revisions()
    assert revisions[2].operation == "delete"


async def test_async_versioned_revisions_operation(TestVersionedThingy):
    thingy = await TestVersionedThingy({"bar": "baz"}).save()
    revisions = await thingy.get_revisions().to_list(length=10)
    assert revisions[0].operation == "create"

    thingy.bar = "qux"
    await thingy.save()
    revisions = await thingy.get_revisions().to_list(length=10)
    assert revisions[1].operation == "update"

    await thingy.delete()
    revisions = await thingy.get_revisions().to_list(length=10)
    assert revisions[2].operation == "delete"


def test_versioned_versioned(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"})
    with pytest.deprecated_call():
        thingy.versioned
    assert thingy.is_versioned() is False

    thingy.bar = "qux"
    assert thingy.is_versioned() is False

    thingy.save()
    assert thingy.is_versioned() is True


async def test_async_versioned_versioned(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"})
    assert await thingy.is_versioned() is False

    thingy.bar = "qux"
    assert await thingy.is_versioned() is False

    await thingy.save()
    assert await thingy.is_versioned() is True


def test_versioned_revert(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    assert thingy.count_revisions() == 1

    thingy.revert()
    assert thingy.count_revisions() == 2
    assert thingy.bar is None

    thingy.revert()
    assert thingy.count_revisions() == 3
    assert thingy.bar == "baz"


async def test_async_versioned_revert(TestVersionedThingy):
    thingy = await TestVersionedThingy({"bar": "baz"}).save()
    assert await thingy.count_revisions() == 1

    await thingy.revert()
    assert await thingy.count_revisions() == 2
    assert thingy.bar is None

    await thingy.revert()
    assert await thingy.count_revisions() == 3
    assert thingy.bar == "baz"
