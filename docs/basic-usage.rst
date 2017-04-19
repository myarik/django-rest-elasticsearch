.. _basic-usage-label:

===========
Basic Usage
===========

Let's take a look at a quick example of using Django REST Elasticsearch to build a simple application.
In the example, we'll build a simple blogging system

Create model
------------
First of all, we create a model.

.. code:: python

    class Blog(models.Model):
        title = models.CharField(_('Title'), max_length=1000)
        created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
        body = models.TextField(_('Body'))
        tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)
        is_published = models.BooleanField(_('Is published'), default=False)

        def __str__(self):
            return self.title

Create the mappings in Elasticsearch
------------------------------------
Then, we have to create a model-like wrapper around our Django model.

.. code:: python

    class BlogIndex(DocType):

        pk = Integer()
        title = Text(fields={'raw': Keyword()})
        created_at = Date()
        body = Text()
        tags = Keyword(multi=True)
        is_published = Boolean()

        class Meta:
            index = 'blog'

After we need to create the mappings in Elasticsearch. For that you can create the mappings directly by calling the init class method:

.. code:: python

    BlogIndex.init()

In the `Document lifecycle documentation <http://elasticsearch-dsl.readthedocs.io/en/latest/persistence.html#document-life-cycle>`_, you can find the full explanation how to work with the document manually.
