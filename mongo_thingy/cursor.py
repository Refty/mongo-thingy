from pymongo.cursor import Cursor as MongoCursor


class Cursor(MongoCursor):

    def __init__(self, thingy_cls, collection, filter=None, view=None,
                 *args, **kwargs):
        self.thingy_cls = thingy_cls
        if view is not None:
            view = self.get_view(view)
        self.thingy_view = view
        super(Cursor, self).__init__(collection, filter or {}, *args, **kwargs)

    def __getitem__(self, index):
        document = super(Cursor, self).__getitem__(index)
        return self.bind(document)

    def bind(self, document):
        thingy = self.thingy_cls(document)
        if self.thingy_view is not None:
            return self.thingy_view(thingy)
        return thingy

    def get_view(self, name):
        return self.thingy_cls._views[name]

    def next(self):
        document = super(Cursor, self).__next__()
        return self.bind(document)

    def view(self, name="defaults"):
        self.thingy_view = self.get_view(name)
        return self

    __next__ = next


__all__ = ["Cursor"]
