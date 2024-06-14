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

