# Elasticsearch for Django REST Framework

## About
Django REST Elasticsearch provides the easy way for integration [Django REST Framework](http://django-rest-framework.org/) and [Elasticsearch](https://github.com/elastic/elasticsearch).
The library uses Elasticsearch DSL library ([elasticsearch-dsl-py](https://github.com/elastic/elasticsearch-dsl-py)) It is a high-level library to the official low-level client.

## Requirements
- Django REST Framework 3.5 and above
- elasticsearch-dsl>=5.0.0,<7.0.0 (**Elasticsearch 5.x**)

## Example
Let's take a look at a quick example of using Django REST Elasticsearch to build a simple application.

Install using `pip`...

    pip install django-rest-elasticsearch

Let's create a simple Django model
```python
class Blog(models.Model):
    title = models.CharField(_('Title'), max_length=1000)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    body = models.TextField(_('Body'))
    tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    is_published = models.BooleanField(_('Is published'), default=False)

    def __str__(self):
        return self.title
```

Create a `DocType` to represent our Blog model
```python

from elasticsearch_dsl import Document, Date, Integer, Keyword, Text

class BlogIndex(Document):
    pk = Integer()
    title = Text(fields={'raw': Keyword()})
    created_at = Date()
    body = Text()
    tags = Keyword(multi=True)
    is_published = Boolean()

    class Index:
        name = 'blog'
```

After, create the mappings in Elasticsearch

    BlogIndex.init()

Finally, create a view. The view provides search by a word in a title and filtering by tags.
```python
from rest_framework_elasticsearch import es_views, es_pagination, es_filters

class BlogView(es_views.ListElasticAPIView):
    es_client = es_client
    es_model = BlogIndex
    es_pagination_class = es_pagination.ElasticLimitOffsetPagination
    es_filter_backends = (
        es_filters.ElasticFieldsFilter,
        es_filters.ElasticFieldsRangeFilter,
        es_filters.ElasticSearchFilter,
        es_filters.ElasticOrderingFilter,
    )
    es_ordering = 'created_at'
    es_filter_fields = (
        es_filters.ESFieldFilter('tag', 'tags'),
    )
    es_range_filter_fields = (
        es_filters.ESFieldFilter('created_at'),
    )
    es_search_fields = (
        'tags',
        'title',
    )
```

This will allow the client to filter the items in the list by making queries such as:
```
http://example.com/blogs/api/list?search=elasticsearch
http://example.com/blogs/api/list?tag=opensource
http://example.com/blogs/api/list?tag=opensource,aws
http://example.com/blogs/api/list?to_created_at=2020-10-01&from_created_at=2017-09-01
```


## Development
Activate Virtual Environment [virtualenvs](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
```
$ virtualenv venv
$ source venv/bin/activate
```

To run all of the tests for **django-rest-elasticsearch**, run:
```
$ python setup.py test
```

Use the `pytest` for running scripts
- Run all of the tests in `test/test_filters.py`
```
$ pytest tests/test_filters.py
```

- Run only the `TestElasticSearchFilter` test.
```
$ pytest tests/test_filters.py::TestElasticSearchFilter
```

By default, the test connection is attempted at **localhost:9200**, based on
the defaults specified in the **elasticsearch-py** [Connection](https://github.com/elastic/elasticsearch-py/blob/master/elasticsearch/connection/base.py#L29)
class. Elasticsearch instance at **localhost:9200**
does not meet these requirements, it is possible to specify a different test
Elasticsearch server through the **TEST_ES_SERVER** environment variable.
```
$ TEST_ES_SERVER=my-test-server:9201 pytest
```

For running tests in ralease environments use [tox](https://tox.readthedocs.io/)
```
$ tox
```

### Docker

This package also can be ran using Docker and the default entrypoint run the pytests.

```
docker-compose up
```

## Documentation
Documentation is available at [http://django-rest-elasticsearch.readthedocs.io](http://django-rest-elasticsearch.readthedocs.io/en/latest/)

