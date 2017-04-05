# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from django.core.exceptions import ImproperlyConfigured
from elasticsearch_dsl import Search
from rest_framework.response import Response

from config.elasticsearch_connection import es_client


class ListElasticMixin(object):
    es_client = es_client

    es_model = None
    es_paginator = None
    es_filter_backends = ()
    es_excludes_fields = ()

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
        s = Search(using=self.es_client, index=index)
        return s

    @staticmethod
    def es_representation(iterable):
        """
        List of object instances
        """
        return [
            item.to_dict() for item in iterable
        ]

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
