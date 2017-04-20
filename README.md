# Elasticsearch for Django REST Framework

## About
Django REST Elasticsearch provides the easy way for integration [Django REST Framework](http://django-rest-framework.org/) and [Elasticsearch](https://github.com/elastic/elasticsearch).
The library uses Elasticsearch DSL library ([elasticsearch-dsl-py](https://github.com/elastic/elasticsearch-dsl-py)) It is a high-level library to the official low-level client.

## Requirements
- Django REST Framework 3.5 and above
- elasticsearch-dsl>=5.0.0,<6.0.0 (**Elasticsearch 5.x**)

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
class BlogIndex(DocType):
    pk = Integer()
    title = Text(fields={'raw': Keyword()})
    created_at = Date()
    body = Text()
    tags = Keyword(multi=True)
    is_published = Boolean()

    class Meta:
        index = 'blog'
```

After, create the mappings in Elasticsearch

    BlogIndex.init()

Finally, create a view. The view provides search by a word in a title and filtering by tags.
```python
from rest_framework_elasticsearch import es_views, es_pagination, es_filters

class BlogView(es_views.ListElasticAPIView):
    es_client = es_client
    es_model = BlogIndex
    es_paginator = es_pagination.ElasticLimitOffsetPagination()
    es_filter_backends = (
        es_filters.ElasticFieldsFilter,
        es_filters.ElasticSearchFilter,
        es_filters.ElasticOrderingFilter,
    )
    es_ordering = 'created_at'
    es_filter_fields = (
        es_filters.ESFieldFilter('tag', 'tags'),
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
```

## Documentation
Documentation is available at [http://django-rest-elasticsearch.readthedocs.io](http://django-rest-elasticsearch.readthedocs.io/en/latest/)
