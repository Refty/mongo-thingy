from datetime import datetime

from pymongo import ASCENDING, DESCENDING

from mongo_thingy import Thingy
from mongo_thingy.cursor import Cursor


class RevisionCursor(Cursor):

    def __init__(self, *args, **kwargs):
        self.thingy = kwargs.pop("thingy", None)
        super(RevisionCursor, self).__init__(*args, **kwargs)

    def __getitem__(self, index):
        if index < 0 and self.thingy:
            index = self.thingy.version + index
        return super(RevisionCursor, self).__getitem__(index)


class Revision(Thingy):
    _cursor_cls = RevisionCursor

    @classmethod
    def from_thingy(cls, thingy, author=None, operation="update"):
        if not thingy.versioned:
            operation = "create"

        version = cls(document_id=thingy.id,
                      document_type=type(thingy).__name__,
                      operation=operation)
        if operation != "delete":
            version.document = thingy.__dict__
        if author:
            version.author = author
        return version

    def save(self):
        self.creation_date = datetime.utcnow()
        return super(Revision, self).save()


Revision.add_index([("document_id", DESCENDING),
                    ("document_type", DESCENDING)])


class Versioned(object):
    _revision_cls = Revision

    def get_revisions(self, **kwargs):
        filter = {"document_id": self.id,
                  "document_type": type(self).__name__}
        filter.update(kwargs)
        return self._revision_cls.find(filter, thingy=self)

    @property
    def version(self):
        return self.get_revisions().count()

    @property
    def versioned(self):
        count = self.get_revisions().limit(1).count(with_limit_and_skip=True)
        return bool(count)

    @property
    def revisions(self):
        return self.get_revisions().sort("_id", ASCENDING)

    def revert(self):
        version = self.version
        if version <= 1:
            previous_version = {"_id": self.id}
        else:
            previous_version = self.revisions[-2].document
        self.__dict__ = previous_version
        return self.save()

    def save(self, author=None, **kwargs):
        result = super(Versioned, self).save(**kwargs)
        version = self._revision_cls.from_thingy(self, author=author)
        version.save()
        return result

    def delete(self, author=None):
        result = super(Versioned, self).delete()
        version = self._revision_cls.from_thingy(self, author=author,
                                                 operation="delete")
        version.save()
        return result


__all__ = ["Revision", "Versioned"]
