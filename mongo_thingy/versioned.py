from datetime import datetime

from pymongo import ASCENDING, DESCENDING

from mongo_thingy import Thingy
from mongo_thingy.cursor import Cursor


class VersionCursor(Cursor):

    def __init__(self, *args, **kwargs):
        self.thingy = kwargs.pop("thingy", None)
        super(VersionCursor, self).__init__(*args, **kwargs)

    def __getitem__(self, index):
        if index < 0 and self.thingy:
            index = self.thingy.version + index
        return super(VersionCursor, self).__getitem__(index)


class Version(Thingy):
    _cursor_cls = VersionCursor

    def save(self):
        self.creation_date = datetime.utcnow()
        return super(Version, self).save()


Version.add_index([("document_id", DESCENDING), ("document_type", DESCENDING)])


class Versioned(object):
    _version_cls = Version

    def get_versions(self, **kwargs):
        filter = {"document_id": self.id,
                  "document_type": type(self).__name__}
        filter.update(kwargs)
        return self._version_cls.find(filter, thingy=self)

    @property
    def version(self):
        return self.get_versions().count()

    @property
    def versioned(self):
        return bool(self.get_versions().limit(1).count(with_limit_and_skip=True))

    @property
    def versions(self):
        return self.get_versions().sort("_id", ASCENDING)

    def rollback(self):
        version = self.version
        if version <= 1:
            previous_version = {"_id": self.id}
        else:
            previous_version = self.versions[-2].document
        self.__dict__ = previous_version
        return self.save()

    def save(self, author=None):
        result = super(Versioned, self).save()
        version = self._version_cls(document_id=self.id,
                                    document_type=type(self).__name__,
                                    document=self.__dict__)
        if author:
            version.author = author
        version.save()
        return result


__all__ = ["Version", "Versioned"]
