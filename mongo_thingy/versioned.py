from datetime import datetime

from pymongo import ASCENDING, DESCENDING

from mongo_thingy import Thingy


class Version(Thingy):

    def save(self):
        self.creation_date = datetime.utcnow()
        return super(Version, self).save()


Version.add_index([("document._id", DESCENDING), ("document_type", DESCENDING)])


class Versioned(object):
    _version_cls = Version

    def get_versions(self, **kwargs):
        filter = {"document._id": self.id,
                  "document_type": type(self).__name__}
        filter.update(kwargs)
        return self._version_cls.find(filter)

    @property
    def version(self):
        return self.get_versions().count()

    @property
    def versions(self):
        return self.get_versions().sort("_id", ASCENDING)

    def rollback(self):
        version = self.version
        if version <= 1:
            previous_version = {"_id": self.id}
        else:
            previous_version = self.versions[self.version - 2].document
        self.__dict__ = previous_version
        return self.save()

    def save(self, author=None):
        result = super(Versioned, self).save()
        version = self._version_cls(document_type=type(self).__name__,
                                    document=self.__dict__)
        if author:
            version.author = author
        version.save()
        return result


__all__ = ["Version", "Versioned"]
