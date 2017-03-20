from thingy import classproperty, DatabaseThingy


class Model(DatabaseThingy):
    _collection = None

    @classproperty
    def collection(cls):
        return cls._collection or cls._table

    @classproperty
    def _table(cls):
        return cls._collection

    @classmethod
    def _get_database_from_table(cls, collection):
        return collection.database

    @classmethod
    def _get_table_from_database(cls, database):
        if cls.table_name:
            return getattr(database, cls.table_name)
        raise AttributeError("Undefined table.")
