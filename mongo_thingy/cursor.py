from pymongo.cursor import Cursor as MongoCursor


class Cursor(MongoCursor):

    def __init__(self, bind, collection, filter=None, *args, **kwargs):
        self.bind = bind
        super(Cursor, self).__init__(collection, filter or {}, *args, **kwargs)

    def __getitem__(self, index):
        document = super(Cursor, self).__getitem__(index)
        return self.bind(document)

    def next(self):
        document = super(Cursor, self).__next__()
        return self.bind(document)

    __next__ = next


__all__ = ["Cursor"]
