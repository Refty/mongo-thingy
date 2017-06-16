from mongo_thingy.cursor import Cursor


def test_version_save(TestVersion):
    version = TestVersion().save()
    assert version.creation_date


def test_version_indexes(TestVersion):
    TestVersion.create_indexes()
    indexes = TestVersion.collection.index_information()
    assert "document._id_-1_document_type_-1" in indexes


def test_versioned_get_versions(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    cursor = thingy.get_versions()
    assert isinstance(cursor, Cursor)

    version = cursor[0]
    assert version.document == thingy.__dict__
    assert version.document_type == "TestVersionedThingy"


def test_versioned_version(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"})
    assert thingy.version == 0
    thingy.save()
    assert thingy.version == 1


def test_versioned_versions(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    thingy.bar = "qux"
    thingy.save()

    assert thingy.versions[0].document.get("bar") == "baz"
    assert thingy.versions[1].document.get("bar") == "qux"


def test_versioned_rollback(TestVersionedThingy):
    thingy = TestVersionedThingy({"bar": "baz"}).save()
    assert thingy.version == 1

    thingy.rollback()
    assert thingy.version == 2
    assert thingy.bar is None

    thingy.rollback()
    assert thingy.version == 3
    assert thingy.bar == "baz"
