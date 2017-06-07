from datetime import datetime

from pymongo import ASCENDING, DESCENDING

from mongo_thingy import Thingy


class Version(Thingy):

    def save(self):
        self.creation_date = datetime.utcnow()
        return super(Version, self).save()


Version.add_index([("document._id", DESCENDING), ("origin", DESCENDING)])


class Versioned(object):
    _version_cls = Version

    def get_versions(self, **kwargs):
        filter = {"document._id": self.id,
                  "origin": self.collection_name}
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
        version = self._version_cls(author=author, origin=self.collection_name,
                                    document=self.__dict__)
        version.save()
        return result


__all__ = ["Version", "Versioned"]
