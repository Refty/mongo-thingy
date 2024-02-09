## Database/collection "discovery"

### Default behaviour

```python
>>> class AuthenticationGroup(Thingy):
...     pass

>>> connect("mongodb://localhost/")
>>> AuthenticationGroup.collection
Collection(Database(MongoClient(host=['localhost:27017'], ...), 'authentication'), 'group')
```

### Use mismatching names for Thingy class and database collection

You can either specify the collection name:

```python
>>> class Foo(Thingy):
...   collection_name = "bar"
```

or the collection directly:

```python
>>> class Foo(Thingy):
...   collection = db.bar
```

You can then check what collection is being used with:

```python
>>> Foo.collection
Collection(Database(MongoClient('localhost', 27017), 'database'), 'bar')
```
