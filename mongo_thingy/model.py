from thingy import classproperty, DatabaseThingy


class Model(DatabaseThingy):
    client = None
    _collection = None

    @classproperty
    def collection(cls):
        return cls._collection or cls.table

    @classproperty
    def collection_name(cls):
        return cls.collection.name

    @classproperty
    def _table(cls):
        return cls._collection

    @classmethod
    def _get_database_from_table(cls, collection):
        return collection.database

    @classmethod
    def _get_table_from_database(cls, database):
        return getattr(database, cls.table_name)
