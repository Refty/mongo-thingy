.. _Thingy: https://github.com/numberly/thingy

============
Mongo-Thingy
============

Mongo-Thingy is the most Pythonic and friendly-yet-powerful way to use MongoDB.

Its main goal is give you full advantage of MongoDB schema-less design by NOT
asking you to define schemas in your code.

It also has cool "side-features" such as joins, views (inherited from Thingy_),
collection discovery, and more!


Install
=======

.. code-block:: sh

   $ pip install mongo-thingy


Examples
========

Dead-simple first steps (insert, count, find, find_one, update)
---------------------------------------------------------------

.. code-block:: python

   >>> from mongo_thingy import connect, Thingy
   >>> connect("mongodb://localhost/test")

   >>> class User(Thingy):
   ...     pass

   >>> User({"name": "Mr. Foo", "age": 42}).save()
   >>> User.count()
   1

   >>> user = User.find_one({"age": 42})
   >>> user.name
   'Mr. Foo'
   >>> user.age = 1337
   >>> user.save()

   >>> users = User.find({"name": {"regexp": "^Mr. "}})
   >>> users[0]
   User({'_id': ObjectId('58e7dcf70825540f0b9e159f'), 'name': 'Mr. Foo', 'age': 1337})
