from pymongo import MongoClient
from thingy import classproperty, DatabaseThingy


class Thingy(DatabaseThingy):
    client = None
    _collection = None

    @classproperty
    def _table(cls):
        return cls._collection

    @classproperty
    def collection(cls):
        return cls.table

    @classproperty
    def collection_name(cls):
        return cls.table_name

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
    def connect(cls, *args, **kwargs):
        cls.client = MongoClient(*args, **kwargs)

    @classmethod
    def disconnect(cls, *args, **kwargs):
        cls.client = None
        cls._database = None


connect = Thingy.connect

__all__ = ["Thingy", "connect"]
