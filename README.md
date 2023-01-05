[pymongo]: https://github.com/mongodb/mongo-python-driver
[thingy]: https://github.com/Refty/thingy
[mongomock]: https://github.com/mongomock/mongomock
[montydb]: https://github.com/davidlatwe/montydb
[motor]: https://github.com/mongodb/motor
[mongomock-motor]: https://github.com/michaelkryukov/mongomock_motor

![Mongo-Thingy](https://socialify.git.ci/Refty/mongo-thingy/image?font=Bitter&language=1&logo=https%3A%2F%2Fi.imgur.com%2FLeNC7Zb.png&owner=1&pattern=Charlie%20Brown&theme=Light)

<div align="center">
    <a href="https://pypi.org/project/mongo-thingy"><img src="https://img.shields.io/pypi/v/mongo-thingy.svg" alt="PyPI"></a>
    <img src="https://img.shields.io/pypi/pyversions/mongo-thingy" alt="Supported Python Versions">
    <a href="LICENSE"><img src="https://img.shields.io/github/license/refty/mongo-thingy" alt="License"></a>
    <a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-black" alt="Code style"></a>
    <br/>
    <a href="https://github.com/Refty/mongo-thingy/actions"><img src="https://img.shields.io/github/actions/workflow/status/Refty/mongo-thingy/tests.yml?branch=master" alt="Tests"></a>
    <a href="https://coveralls.io/github/Refty/mongo-thingy"><img src="https://img.shields.io/coveralls/Refty/mongo-thingy.svg" alt="Tests"></a>
    <a href="http://mongo-thingy.readthedocs.io"><img src="https://readthedocs.org/projects/mongo-thingy/badge" alt="Docs"></a>
    <br /><br />
</div>

**_Mongo-Thingy_ is the most idiomatic and friendly-yet-powerful way to use
MongoDB with Python.**

It is an _"Object-Document Mapper"_ that gives you full advantage of MongoDB
schema-less design by **not** asking you to define schemas in your code.

What you'll get:

- a simple and robust pure-Python code base, with 100% coverage and few
  dependencies;
- [PyMongo][pymongo] query language - no need to learn yet another one;
- both sync and async support! choose what suits you best;
- [Thingy][thingy] views - control what to show, and create fields based on
  other fields;
- swappable backend - wanna use SQLite behind the scenes? well, you can;
- versioning *(optional)* - rollback to any point in any thingy history;
- and more!

# Compatibility

We support all Python and MongoDB versions supported by [PyMongo][pymongo],
namely:

- CPython 3.7+ and PyPy3.7+
- MongoDB 3.6, 4.0, 4.2, 4.4, and 5.0.

As a backend, Mongo-Thingy supports the following libraries:

- Synchronous:

  * [PyMongo][pymongo] (default)
  * [Mongomock][mongomock]
  * [MontyDB][montydb]

- Asynchronous:

  * [Motor][motor] (default when Motor is installed)
  * [Motor][motor] with Tornado (default when Motor and Tornado are installed)
  * [Mongomock-Motor][mongomock-motor]

# Install

```sh
pip install mongo-thingy
```

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

## Thingy views power

### Complete information with properties

```python
>>> class User(Thingy):
...     @property
...     def username(self):
...         return "".join(char for char in self.name if char.isalpha())

>>> User.add_view(name="everything", defaults=True, include="username")
>>> user = User.find_one()
>>> user.view("everything")
{'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337, 'username': 'MrFoo'}
```

### Hide sensitive stuff

```python
>>> User.add_view(name="public", defaults=True, exclude="password")
>>> user.password = "t0ps3cr3t"
>>> user.view()
{'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337, 'password': 't0ps3cr3t'}
>>> user.view("public")
{'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337}
```

### Only use certain fields/properties

```python
>>> User.add_view(name="credentials", include=["username", "password"])
>>> user.view("credentials")
{'username': 'MrFoo', 'password': 't0ps3cr3t'}
```

### Apply views on cursors

```python
>>> cursor = User.find()
>>> for credentials in cursor.view("credentials"):
...     print(credentials)
{'username': 'MrFoo', 'password': 't0ps3cr3t'}
{'username': 'MrsBar', 'password': '123456789'}
...
```

And if your cursor is already exhausted, you can still apply a view!

```python
>>> users = User.find().to_list(None)
>>> for credentials in users.view("credentials"):
...     print(credentials)
{'username': 'MrFoo', 'password': 't0ps3cr3t'}
{'username': 'MrsBar', 'password': '123456789'}
...
```

## Versioning

```python
>>> from mongo_thingy.versioned import Versioned

>>> class Article(Versioned, Thingy):
...     pass

>>> article = Article(content="Cogito ergo sum")
>>> article.version
0

>>> article.save()
Article({'_id': ObjectId('...'), 'content': 'Cogito ergo sum'})
>>> article.version
1

>>> article.content = "Sum ergo cogito"
>>> article.save()
Article({'_id': ObjectId('...'), 'content': 'Sum ergo cogito'})
>>> article.version
2

>>> article.revert()
Article({'_id': ObjectId('...'), 'content': 'Cogito ergo sum'})
>>> article.version
3
```

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

## Indexes

### Create an index

```python
>>> User.create_index("email", sparse=True, unique=True)
```

### Add one or more indexes, create later

```python
>>> User.add_index("email", sparse=True, unique=True)
>>> User.add_index("username")

>>> User.create_indexes()
```

### Create all indexes of all thingies at once

```python
>>> from mongo_thingy import create_indexes
>>> create_indexes()
```

## Dealing with camelCase data

```python
>>> from mongo_thingy.camelcase import CamelCase

>>> class SystemUser(CamelCase, Thingy):
...     collection_name = "systemUsers"

>>> user = SystemUser.find_one()
>>> user.view()
{'_id': ObjectId(...), 'firstName': 'John', 'lastName': 'Doe'}

>>> user.first_name
'John'
>>> user.first_name = "Jonny"
>>> user.save()
SystemUser({'_id': ObjectId(...), firstName: 'Jonny', lastName: 'Doe'})
```

# Tests

To run the tests suite:

  - make sure you have a MongoDB database running on `localhost:27017` (you can
    spawn one with `docker-compose up -d`);
  - install developers requirements with `pip install -r requirements.txt`;
  - run `pytest`.

# Sponsors

<div align="center">
    &nbsp;&nbsp;&nbsp;
    <a href="https://numberly.com/"><img src="https://raw.githubusercontent.com/Refty/mongo-thingy/master/img/numberly.png" alt="Numberly"></a>
    &nbsp;&nbsp;&nbsp;
    &nbsp;&nbsp;&nbsp;
    <a href="https://refty.co/"><img src="https://raw.githubusercontent.com/Refty/mongo-thingy/master/img/refty.png" alt="Refty"></a>
    &nbsp;&nbsp;&nbsp;
</div>
