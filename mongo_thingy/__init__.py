import asyncio
import warnings
from collections.abc import Mapping

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ConfigurationError
from thingy import DatabaseThingy, classproperty, registry

from mongo_thingy.cursor import AsyncCursor, Cursor

try:
    from motor.motor_tornado import MotorClient
except ImportError:  # pragma: no cover
    MotorClient = None

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:  # pragma: no cover
    AsyncIOMotorClient = None


class BaseThingy(DatabaseThingy):
    """Represents a document in a collection"""

    _client = None
    _client_cls = None
    _collection = None
    _collection_name = None
    _cursor_cls = None

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
        return cls.get_client()

    @classmethod
    def _get_client(cls, database):
        return database.client

    @classmethod
    def _get_database(cls, collection, name):
        if collection is not None:
            return collection.database
        if cls._client and name:
            return cls._client[name]
        raise AttributeError("Undefined database.")

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
    def get_client(cls):
        if cls._client:
            return cls._client
        return cls._get_client(cls.database)

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
    def count_documents(cls, filter=None, *args, **kwargs):
        if filter is None:
            filter = {}
        return cls.collection.count_documents(filter, *args, **kwargs)

    @classmethod
    def count(cls, filter=None, *args, **kwargs):
        warnings.warn(
            "count is deprecated. Use count_documents instead.", DeprecationWarning
        )
        return cls.count_documents(filter=filter, *args, **kwargs)

    @classmethod
    def connect(cls, *args, client_cls=None, **kwargs):
        if not client_cls:
            client_cls = cls._client_cls

        cls._client = client_cls(*args, **kwargs)
        try:
            cls._database = cls._client.get_database()
        except (ConfigurationError, TypeError):
            cls._database = cls._client["test"]

    @classmethod
    def disconnect(cls, *args, **kwargs):
        if cls._client:
            cls._client.close()
        cls._client = None
        cls._database = None

    @classmethod
    def distinct(cls, *args, **kwargs):
        return cls.collection.distinct(*args, **kwargs)

    @classmethod
    def find(cls, *args, view=None, **kwargs):
        delegate = cls.collection.find(*args, **kwargs)
        return cls._cursor_cls(delegate, thingy_cls=cls, view=view)

    @classmethod
    def find_one(cls, filter=None, *args, **kwargs):
        if filter is not None and not isinstance(filter, Mapping):
            filter = {"_id": filter}

        cursor = cls.find(filter, *args, **kwargs)
        return cursor.first()

    @property
    def id(self):
        return self.__dict__.get("id") or self._id

    @id.setter
    def id(self, value):
        if "id" in self.__dict__:
            self.__dict__["id"] = value
        else:
            self._id = value

    def delete(self):
        return self.get_collection().delete_one({"_id": self.id})


class Thingy(BaseThingy):
    _client_cls = MongoClient
    _cursor_cls = Cursor

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
    def find_one_and_replace(cls, *args, **kwargs):
        kwargs.setdefault("return_document", ReturnDocument.AFTER)
        result = cls.collection.find_one_and_replace(*args, **kwargs)
        if result is not None:
            return cls(result)

    def save(self, force_insert=False):
        data = self.__dict__
        if self.id is not None and not force_insert:
            filter = {"_id": self.id}
            self.get_collection().replace_one(filter, data, upsert=True)
        else:
            self.get_collection().insert_one(data)
        return self


class AsyncThingy(BaseThingy):
    _client_cls = MotorClient or AsyncIOMotorClient
    _cursor_cls = AsyncCursor

    @classmethod
    async def create_index(cls, keys, **kwargs):
        cls.add_index(keys, **kwargs)
        await cls.collection.create_index(keys, **kwargs)

    @classmethod
    async def create_indexes(cls):
        if hasattr(cls, "_indexes"):
            for keys, kwargs in cls._indexes:
                await cls.collection.create_index(keys, **kwargs)

    @classmethod
    async def find_one_and_replace(cls, *args, **kwargs):
        kwargs.setdefault("return_document", ReturnDocument.AFTER)
        result = await cls.collection.find_one_and_replace(*args, **kwargs)
        if result is not None:
            return cls(result)

    async def save(self, force_insert=False):
        data = self.__dict__
        if self.id is not None and not force_insert:
            filter = {"_id": self.id}
            await self.get_collection().replace_one(filter, data, upsert=True)
        else:
            await self.get_collection().insert_one(data)
        return self


def connect(*args, **kwargs):
    if AsyncThingy._client_cls is not None:
        AsyncThingy.connect(*args, **kwargs)
    Thingy.connect(*args, **kwargs)


def disconnect(*args, **kwargs):
    Thingy.disconnect(*args, **kwargs)
    AsyncThingy.disconnect(*args, **kwargs)


def create_indexes():
    """Create indexes registered on all :class:`Thingy`"""
    for cls in registry:
        if issubclass(cls, Thingy):
            cls.create_indexes()
        if issubclass(cls, AsyncThingy):
            coroutine = cls.create_indexes()
            asyncio.create_task(coroutine)


__all__ = ["AsyncThingy", "Thingy", "connect", "create_indexes"]
