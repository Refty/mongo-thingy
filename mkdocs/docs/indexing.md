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
