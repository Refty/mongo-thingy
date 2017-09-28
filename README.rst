.. _Thingy: https://github.com/numberly/thingy
.. _PyMongo: https://github.com/mongodb/mongo-python-driver

============
Mongo-Thingy
============

.. image:: https://img.shields.io/pypi/v/mongo-thingy.svg
   :target: https://pypi.python.org/pypi/Mongo-Thingy
.. image:: https://img.shields.io/github/license/numberly/mongo-thingy.svg
   :target: https://github.com/numberly/mongo-thingy/blob/master/LICENSE
.. image:: https://img.shields.io/travis/numberly/mongo-thingy.svg
   :target: https://travis-ci.org/numberly/mongo-thingy
.. image:: https://img.shields.io/coveralls/numberly/mongo-thingy.svg
   :target: https://coveralls.io/github/numberly/mongo-thingy

|

Mongo-Thingy is the most Pythonic and friendly-yet-powerful way to use MongoDB.

It is an "Object-Document Mapper" that gives you full advantage of MongoDB
schema-less design by **not** asking you to define schemas in your code, but
with all the powerful features you would expect from such a library.

Mongo-Thingy has:

- a simple and robust code base, with 100% coverage and few dependencies;
- PyMongo_ query language - no need to learn yet another one;
- Thingy_ views - control what to show, and create fields based on other fields;
- versioning (optional) - rollback to any point in any thingy history;
- and more!


Compatibility
=============

Mongo-Thingy is pure-Python.

It supports all Python and MongoDB versions supported by PyMongo_, namely:

- CPython 2.6, 2.7, 3.4+, PyPy, and PyPy3
- MongoDB 2.6, 3.0, 3.2, and 3.4


Install
=======

.. code-block:: sh

   $ pip install mongo-thingy


Examples
========

First steps
-----------

Connect, insert and find thingies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> from mongo_thingy import connect, Thingy
   >>> connect("mongodb://localhost/test")

   >>> class User(Thingy):
   ...     pass

   >>> user = User({"name": "Mr. Foo", "age": 42}).save()
   >>> User.count()
   1
   >>> User.find_one({"age": 42})
   User({'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 42})


Update a thingy
~~~~~~~~~~~~~~~

.. code-block:: python

   >>> user.age
   42
   >>> user.age = 1337
   >>> user.save()
   User({'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337})


Thingy views power
------------------

Complete information with properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> class User(Thingy):
   ...     @property
   ...     def username(self):
   ...         return "".join(char for char in self.name if char.isalpha())

   >>> User.add_view(name="everything", defaults=True, include="username")
   >>> user = User.find_one()
   >>> user.view("everything")
   {'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337, 'username': 'MrFoo'}


Hide sensitive stuff
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> User.add_view(name="public", defaults=True, exclude="password")
   >>> user.password = "t0ps3cr3t"
   >>> user.view()
   {'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337, 'password': 't0ps3cr3t'}
   >>> user.view("public")
   {'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337}


Only use certain fields/properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> User.add_view(name="credentials", include=["username", "password"])
   >>> user.view("credentials")
   {'username': 'MrFoo', 'password': 't0ps3cr3t'}


Apply views on cursors
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> for credentials in User.find().view("credentials"):
   ...     print(credentials)
   {'username': 'MrFoo', 'password': 't0ps3cr3t'}
   {'username': 'MrsBar', 'password': '123456789'}
   ...


Versioning
----------

.. code-block:: python

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


Database/collection "discovery"
-------------------------------

.. code-block:: python

   >>> class AuthenticationGroup(Thingy):
   ...     pass

   >>> connect("mongodb://localhost/")
   >>> AuthenticationGroup.collection
   Collection(Database(MongoClient(host=['localhost:27017'], ...), 'authentication'), 'group')


Indexes
-------

Create an index
~~~~~~~~~~~~~~~

.. code-block:: python

   >>> User.create_index("email", sparse=True, unique=True)


Add one or more indexes, create later
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> User.add_index("email", sparse=True, unique=True)
   >>> User.add_index("username")

   >>> User.create_indexes()


Create all indexes of all thingies at once
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> from mongo_thingy import create_indexes
   >>> create_indexes()


Tests
=====

To run Mongo-Thingy tests:

* make sure you have a MongoDB database running on ``localhost:27017``;
* install developers requirements with ``pip install -r requirements.txt``;
* run ``pytest``.


License
=======

MIT
