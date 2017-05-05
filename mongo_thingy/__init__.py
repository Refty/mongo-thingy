from pymongo import MongoClient
from thingy import classproperty, DatabaseThingy, registry

from .cursor import Cursor


class Thingy(DatabaseThingy):
    client = None
    _collection = None

    @classproperty
    def _table(cls):
        return cls._collection

    @classproperty
    def table_name(cls):
        return cls.collection_name

    @classproperty
    def collection(cls):
        return cls.table

    @classproperty
    def collection_name(cls):
        if cls._table:
            return cls._get_table_name(cls._table)
        return cls.names[-1].lower()

    @classmethod
    def _get_database(cls, collection, name):
        if collection:
            return collection.database
        if cls.client:
            if name:
                return cls.client[name]
            return cls.client.get_default_database()
        raise AttributeError("Undefined client.")

    @classmethod
    def _get_table(cls, database, table_name):
        return database[table_name]

    @classmethod
    def _get_database_name(cls, database):
        return database.name

    @classmethod
    def _get_table_name(cls, table):
        return table.name

    @classmethod
    def add_index(cls, keys, **kwargs):
        kwargs.setdefault("background", True)
        if not hasattr(cls, "_indexes"):
            cls._indexes = []
        cls._indexes.append((keys, kwargs))

    @classmethod
    def count(cls, *args, **kwargs):
        return cls.collection.count()

    @classmethod
    def connect(cls, *args, **kwargs):
        cls.client = MongoClient(*args, **kwargs)

    @classmethod
    def create_index(cls, keys, **kwargs):
        cls.add_index(keys, **kwargs)
        cls.collection.create_index(keys, **kwargs)

    @classmethod
    def create_indexes(cls):
        if hasattr(cls, "_indexes"):
            for keys, kwargs in cls._indexes:
                cls.collection.create_index(keys, **kwargs)

    @classmethod
    def disconnect(cls, *args, **kwargs):
        cls.client = None
        cls._database = None

    @classmethod
    def distinct(cls, *args, **kwargs):
        return cls.collection.distinct(*args, **kwargs)

    @classmethod
    def find(cls, *args, **kwargs):
        return Cursor(cls, cls.collection, *args, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        result = cls.collection.find_one(*args, **kwargs)
        if result is not None:
            return cls(result)

    @property
    def id(self):
        return self.__dict__.get("id") or self._id

    @id.setter
    def id(self, value):
        if "id" in self.__dict__:
            self.__dict__["id"] = value
        else:
            self._id = value

    def save(self):
        data = self.__dict__
        if self.id:
            self.collection.update({"_id": self.id}, data, upsert=True)
        else:
            self.collection.insert(data)
        return self

    def delete(self):
        return self.collection.remove({"_id": self.id})


connect = Thingy.connect


def create_indexes():
    for cls in registry:
        if issubclass(cls, Thingy):
            cls.create_indexes()


__all__ = ["Thingy", "connect", "create_indexes"]
