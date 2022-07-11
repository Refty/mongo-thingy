import warnings
from datetime import datetime

from pymongo import ASCENDING, DESCENDING

from mongo_thingy import AsyncThingy, BaseThingy, Thingy
from mongo_thingy.cursor import AsyncCursor, BaseCursor, Cursor


class BaseRevisionCursor(BaseCursor):
    def __init__(self, *args, **kwargs):
        super(BaseRevisionCursor, self).__init__(*args, **kwargs)


class RevisionCursor(Cursor, BaseRevisionCursor):
    def __getitem__(self, index):
        if index < 0 and self.thingy:
            version = self.thingy.count_revisions()
            index = version + index
        return super(RevisionCursor, self).__getitem__(index)


class AsyncRevisionCursor(AsyncCursor, BaseRevisionCursor):
    pass


class BaseRevision(BaseThingy):
    """Revision of a document"""

    _collection_name = "revision"
    _cursor_cls = None

    @classmethod
    def from_thingy(cls, thingy, author=None, operation="update"):
        version = cls(
            document_id=thingy.id,
            document_type=type(thingy).__name__,
            operation=operation,
        )
        if operation != "delete":
            version.document = thingy.__dict__
        if author:
            version.author = author
        return version

    def _prev(self):
        return self.find_one(
            {"document_id": self.document_id, "document_type": self.document_type}
        )


BaseRevision.add_index([("document_id", DESCENDING), ("document_type", DESCENDING)])


class Revision(Thingy, BaseRevision):
    _cursor_cls = RevisionCursor

    def save(self):
        self.creation_date = datetime.utcnow()
        if not self._prev():
            self.operation = "create"
        return super(Revision, self).save()


class AsyncRevision(AsyncThingy, BaseRevision):
    _cursor_cls = AsyncRevisionCursor

    async def save(self):
        self.creation_date = datetime.utcnow()
        if not await self._prev():
            self.operation = "create"
        return await super(AsyncRevision, self).save()


class BaseVersioned:
    """Mixin to versionate changes in a collection"""

    _revisions_cls = None

    def get_revisions(self, **kwargs):
        filter = {"document_id": self.id, "document_type": type(self).__name__}
        filter.update(kwargs)

        cursor = self._revision_cls.find(filter)
        cursor.thingy = self
        return cursor.sort("_id", ASCENDING)

    def count_revisions(self, **kwargs):
        filter = {"document_id": self.id, "document_type": type(self).__name__}
        return self._revision_cls.count_documents(filter, **kwargs)


class Versioned(BaseVersioned):
    def is_versioned(self):
        return bool(self.count_revisions(limit=1))

    @property
    def version(self):
        warnings.warn(
            "version is deprecated. Use count_revisions() instead.", DeprecationWarning
        )
        return self.count_revisions()

    @property
    def versioned(self):
        warnings.warn(
            "versioned is deprecated. Use is_versioned() instead.", DeprecationWarning
        )
        return bool(self.count_revisions(limit=1))

    @property
    def revisions(self):
        warnings.warn(
            "revisions is deprecated. Use get_revisions() instead.", DeprecationWarning
        )
        return self.get_revisions()

    def revert(self):
        revisions = list(self.get_revisions().limit(3))
        try:
            self.__dict__ = revisions[-2].document
        except IndexError:
            self.__dict__ = {"_id": self.id}
        return self.save()

    def save(self, author=None, **kwargs):
        result = super(Versioned, self).save(**kwargs)
        version = self._revision_cls.from_thingy(self, author=author)
        version.save()
        return result

    def delete(self, author=None):
        result = super(Versioned, self).delete()
        version = self._revision_cls.from_thingy(
            self, author=author, operation="delete"
        )
        version.save()
        return result


class AsyncVersioned(BaseVersioned):
    async def is_versioned(self):
        return bool(await self.count_revisions(limit=1))

    async def revert(self):
        revisions = await self.get_revisions().limit(3).to_list(length=3)
        try:
            self.__dict__ = revisions[-2].document
        except IndexError:
            self.__dict__ = {"_id": self.id}
        return await self.save()

    async def save(self, author=None, **kwargs):
        result = await super(AsyncVersioned, self).save(**kwargs)
        version = self._revision_cls.from_thingy(self, author=author)
        await version.save()
        return result

    async def delete(self, author=None):
        result = await super(AsyncVersioned, self).delete()
        version = self._revision_cls.from_thingy(
            self, author=author, operation="delete"
        )
        await version.save()
        return result


__all__ = ["AsyncRevision", "AsyncVersioned", "Revision", "Versioned"]
