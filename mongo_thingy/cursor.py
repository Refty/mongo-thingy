import functools


class _Proxy:
    def __init__(self, name):
        self.name = name

    def __call__(self, cursor):
        return getattr(cursor.delegate, self.name)


class _ChainingProxy(_Proxy):
    def __call__(self, cursor):
        method = getattr(cursor.delegate, self.name)

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            method(*args, **kwargs)
            return cursor

        return wrapper


class _BindingProxy(_Proxy):
    def __call__(self, cursor):
        method = getattr(cursor.delegate, self.name)

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            result = method(*args, **kwargs)
            return cursor.bind(result)

        return wrapper


class _AsyncBindingProxy(_Proxy):
    def __call__(self, cursor):
        method = getattr(cursor.delegate, self.name)

        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            result = await method(*args, **kwargs)
            if isinstance(result, list):
                return cursor.result_cls(cursor.bind(r) for r in result)
            return cursor.bind(result)

        return wrapper


class BaseCursor:
    distinct = _Proxy("distinct")
    explain = _Proxy("explain")
    limit = _ChainingProxy("limit")
    skip = _ChainingProxy("skip")
    sort = _ChainingProxy("sort")

    def __init__(self, delegate, thingy_cls=None, view=None):
        self.delegate = delegate
        self.thingy_cls = thingy_cls
        self.result_cls = getattr(thingy_cls, "_result_cls", list)

        if isinstance(view, str):
            view = self.get_view(view)

        self.thingy_view = view

    def __getattribute__(self, name):
        attribute = object.__getattribute__(self, name)
        if isinstance(attribute, _Proxy):
            return attribute(self)
        return attribute

    def bind(self, document):
        if not self.thingy_cls:
            return document
        thingy = self.thingy_cls(document)
        if self.thingy_view is not None:
            return self.thingy_view(thingy)
        return thingy

    def clone(self):
        delegate = self.delegate.clone()
        return self.__class__(
            delegate, thingy_cls=self.thingy_cls, view=self.thingy_view
        )

    def get_view(self, name):
        return self.thingy_cls._views[name]

    def view(self, name="defaults"):
        self.thingy_view = self.get_view(name)
        return self


class Cursor(BaseCursor):
    next = __next__ = _BindingProxy("__next__")

    def __getitem__(self, index):
        document = self.delegate.__getitem__(index)
        return self.bind(document)

    def to_list(self, length):
        if length is not None:
            self.limit(length)
        return self.result_cls(self)

    def delete(self):
        ids = self.distinct("_id")
        return self.thingy_cls.collection.delete_many({"_id": {"$in": ids}})

    def first(self):
        try:
            document = self.delegate.clone().limit(-1).__next__()
        except StopIteration:
            return None
        return self.bind(document)


class AsyncCursor(BaseCursor):
    to_list = _AsyncBindingProxy("to_list")
    next = __anext__ = _AsyncBindingProxy("__anext__")

    async def __aiter__(self):
        async for document in self.delegate:
            yield self.bind(document)

    async def delete(self):
        ids = await self.distinct("_id")
        return await self.thingy_cls.collection.delete_many({"_id": {"$in": ids}})

    async def first(self):
        try:
            document = await self.delegate.clone().limit(-1).__anext__()
        except StopAsyncIteration:
            return None
        return self.bind(document)


__all__ = ["AsyncCursor", "Cursor"]
