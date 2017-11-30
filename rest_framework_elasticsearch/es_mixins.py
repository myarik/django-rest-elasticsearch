# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from django.core.exceptions import ImproperlyConfigured
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from rest_framework.response import Response

from .es_inspector import EsAutoSchema


class ListElasticMixin(object):
    es_client = None

    es_model = None
    es_pagination_class = None

    es_filter_backends = ()
    es_excludes_fields = ()

    schema = EsAutoSchema()

    def get_es_client(self):
        """
        You may want to override this if you need to provide different
        Elasticsearch.client depending on the incoming request.
        """
        assert self.es_client is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        es_client = self.es_client
        if not isinstance(es_client, Elasticsearch):
            raise ValueError("Incorrect value es_client")
        return es_client

    def filter_search(self, search):
        for backend in list(self.es_filter_backends):
            search = backend().filter_search(self.request, search, self)
        return search

    def excludes_respond_fields(self, search):
        if self.es_excludes_fields:
            search = search.source(**{'excludes': self.es_excludes_fields})
        return search

    def get_es_search(self):
        if self.es_model is None:
            msg = (
                "Cannot use %s on a view which does not have the 'es_model'"
            )
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        index = self.es_model()._get_index()
        es_client = self.get_es_client()
        s = Search(using=es_client, index=index, doc_type=self.es_model)
        return s

    @staticmethod
    def es_representation(iterable):
        """
        List of object instances
        """
        return [
            item.to_dict() for item in iterable
            ]

    @property
    def es_paginator(self):
        """
        The es_paginator instance associated with the view
        """
        if not hasattr(self, '_es_paginator'):
            if self.es_pagination_class is None:
                self._es_paginator = None
            else:
                self._es_paginator = self.es_pagination_class()
        return self._es_paginator

    def paginate_search(self, search):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.es_paginator is None:
            return None
        return self.es_paginator.paginate_search(search, self.request, view=self)

    def list(self, request, *args, **kwargs):
        search = self.filter_search(self.get_es_search())
        search = self.excludes_respond_fields(search)
        page = self.paginate_search(search)
        if page is not None:
            return self.es_paginator.get_paginated_response(
                self.es_representation(page)
            )
        return Response(self.es_representation(search.scan()))
