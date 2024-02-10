# Examples

## First steps

### Connect, insert and find thingies

```python
>>> from mongo_thingy import connect, Thingy
>>> connect("mongodb://localhost/test")

>>> class User(Thingy):
...     pass

>>> user = User({"name": "Mr. Foo", "age": 42}).save()
>>> User.count_documents()
1
>>> User.find_one({"age": 42})
User({'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 42})
```

In an AsyncIO (or Tornado) environment, use the asynchronous class instead:

```python
>>> from mongo_thingy import connect, AsyncThingy
>>> connect("mongodb://localhost/test")

>>> class User(AsyncThingy):
...     pass

>>> user = await User({"name": "Mr. Foo", "age": 42}).save()
>>> await User.count_documents()
1
>>> await User.find_one({"age": 42})
User({'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 42})
```

To use another backend than the default ones, just pass its client class with
``client_cls``:

```python
>>> import mongomock
>>> connect(client_cls=mongomock.MongoClient)
```

### Update a thingy

```python
>>> user.age
42
>>> user.age = 1337
>>> user.save()
User({'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337})
```
