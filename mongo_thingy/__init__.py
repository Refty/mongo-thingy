import collections

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ConfigurationError
from thingy import classproperty, DatabaseThingy, registry

from mongo_thingy.cursor import Cursor


class Thingy(DatabaseThingy):
    _client = None
    _collection = None
    _collection_name = None
    _cursor_cls = Cursor

    @classproperty
    def _table(cls):
        return cls._collection

    @classproperty
    def _table_name(cls):
        return cls._collection_name

    @classproperty
    def table_name(cls):
        return cls.collection_name

    @classproperty
    def collection(cls):
        return cls.get_collection()

    @classproperty
    def collection_name(cls):
        return cls.get_table_name()

    @classproperty
    def client(cls):
        return cls._client

    @classmethod
    def _get_database(cls, collection, name):
        if collection:
            return collection.database
        if cls.client and name:
            return cls.client[name]
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
    def get_collection(cls):
        return cls.get_table()

    @classmethod
    def add_index(cls, keys, **kwargs):
        kwargs.setdefault("background", True)
        if not hasattr(cls, "_indexes"):
            cls._indexes = []
        cls._indexes.append((keys, kwargs))

    @classmethod
    def count(cls, *args, **kwargs):
        return cls.collection.count(*args, **kwargs)

    @classmethod
    def connect(cls, *args, **kwargs):
        cls._client = MongoClient(*args, **kwargs)
        try:
            cls._database = cls._client.get_default_database()
        except ConfigurationError:
            pass

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
        cls.client.close()
        cls._client = None
        cls._database = None

    @classmethod
    def distinct(cls, *args, **kwargs):
        return cls.collection.distinct(*args, **kwargs)

    @classmethod
    def find(cls, *args, **kwargs):
        return cls._cursor_cls(cls, cls.collection, *args, **kwargs)

    @classmethod
    def find_one(cls, filter=None, *args, **kwargs):
        if filter is not None and not isinstance(filter, collections.Mapping):
            filter = {"_id": filter}

        max_time_ms = kwargs.pop("max_time_ms", None)
        cursor = cls.find(filter, *args, **kwargs).max_time_ms(max_time_ms)

        for result in cursor.limit(-1):
            return result
        return None

    @classmethod
    def find_one_and_replace(cls, *args, **kwargs):
        kwargs.setdefault("return_document", ReturnDocument.AFTER)
        result = cls.collection.find_one_and_replace(*args, **kwargs)
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

    def save(self, force_insert=False):
        data = self.__dict__
        if self.id is not None and not force_insert:
            self.get_collection().update({"_id": self.id}, data, upsert=True)
        else:
            self.get_collection().insert(data)
        return self

    def delete(self):
        return self.get_collection().remove({"_id": self.id})


connect = Thingy.connect
disconnect = Thingy.disconnect


def create_indexes():
    for cls in registry:
        if issubclass(cls, Thingy):
            cls.create_indexes()


__all__ = ["Thingy", "connect", "create_indexes"]
