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
