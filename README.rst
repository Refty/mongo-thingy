.. _Thingy: https://github.com/numberly/thingy

============
Mongo-Thingy
============

Mongo-Thingy is the most Pythonic and friendly-yet-powerful way to use MongoDB.

Its main goal is give you full advantage of MongoDB schema-less design by NOT
asking you to define schemas in your code.

It also has cool "side-features" such as views (inherited from Thingy_),
database/collection "discovery", and more!


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


Update thingies
~~~~~~~~~~~~~~~

.. code-block:: python

   >>> user.age
   42
   >>> user.age = 1337
   >>> user.save()
   User({'_id': ObjectId(...), 'name': 'Mr. Foo', 'age': 1337})


Thingy's views power
--------------------

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
