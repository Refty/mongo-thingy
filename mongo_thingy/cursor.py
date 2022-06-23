class Cursor:

    def __init__(self, delegate, thingy_cls=None, view=None):
        self.delegate = delegate
        self.thingy_cls = thingy_cls

        if isinstance(view, str):
            view = self.get_view(view)

        self.thingy_view = view

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
            document = self.delegate.limit(-1).next()
        except StopIteration:
            return None
        return self.bind(document)

    def get_view(self, name):
        return self.thingy_cls._views[name]

    def next(self):
        document = self.delegate.__next__()
        return self.bind(document)

    def view(self, name="defaults"):
        self.thingy_view = self.get_view(name)
        return self

    __next__ = next


__all__ = ["Cursor"]
