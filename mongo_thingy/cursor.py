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


class Cursor:
    distinct = _Proxy("distinct")
    explain = _Proxy("explain")
    limit = _ChainingProxy("limit")
    skip = _ChainingProxy("skip")
    sort = _ChainingProxy("sort")
    next = _BindingProxy("next")

    def __init__(self, delegate, thingy_cls=None, view=None):
        self.delegate = delegate
        self.thingy_cls = thingy_cls

        if isinstance(view, str):
            view = self.get_view(view)

        self.thingy_view = view

    def __getattribute__(self, name):
        attribute = object.__getattribute__(self, name)
        if isinstance(attribute, _Proxy):
            return attribute(self)
        return attribute

    def __getitem__(self, index):
        document = self.delegate.__getitem__(index)
        return self.bind(document)

    def bind(self, document):
        if not self.thingy_cls:
            return document
        thingy = self.thingy_cls(document)
        if self.thingy_view is not None:
            return self.thingy_view(thingy)
        return thingy

    def clone(self):
        delegate = self.delegate.clone()
        return self.__class__(delegate, thingy_cls=self.thingy_cls,
                              view=self.thingy_view)

    def first(self):
        try:
            document = self.delegate.clone().limit(-1).next()
        except StopIteration:
            return None
        return self.bind(document)

    def get_view(self, name):
        return self.thingy_cls._views[name]

    def view(self, name="defaults"):
        self.thingy_view = self.get_view(name)
        return self

    __next__ = next


__all__ = ["Cursor"]
