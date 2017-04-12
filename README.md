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