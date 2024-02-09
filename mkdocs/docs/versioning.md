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
