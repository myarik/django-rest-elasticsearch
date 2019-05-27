# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ImproperlyConfigured
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from rest_framework import views

from .es_filters import ElasticSearchFilter
from .es_inspector import EsAutoSchema
from .es_mixins import ListElasticMixin
from .es_pagination import ElasticLimitOffsetPagination


class ElasticAPIView(views.APIView):
    """Elasticsearch base API view class."""
    es_client = None
    es_model = None
    es_filter_backends = (ElasticSearchFilter,)

    schema = EsAutoSchema()

    def get_es_search_fields(self):
        """
        Return field or fields used for search.
        The return value must be an iterable.
        """
        return getattr(self, 'es_search_fields', None)

    def get_es_filter_fields(self):
        """
        Return field or fields used for search filtering.
        The return value must be an iterable.
        """
        return getattr(self, 'es_filter_fields', tuple())

    def get_es_range_filter_fields(self):
        """
        Return field or fields used for search filtering by range.
        The return value must be an iterable.
        """
        return getattr(self, 'es_range_filter_fields', tuple())

    def get_es_ordering_fields(self):
        """
        Return field or fields used for search ordering.
        The return value must be an iterable.
        """
        return getattr(self, 'es_ordering_fields', None)

    def get_es_excludes_fields(self):
        """
        Return field or fields excluded from search results.
        The return value must be an iterable.
        """
        return getattr(self, 'es_excludes_fields', None)

    def get_es_geo_location_field(self):
        """
        Return field or fields used for search.
        The return value must be an iterable.
        """
        return getattr(self, 'es_geo_location_field', None)

    def get_es_geo_location_field_name(self):
        """
        """
        return getattr(self, 'es_geo_location_field_name', None)

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
        es_excludes_fields = self.get_es_excludes_fields()
        if es_excludes_fields:
            search = search.source(**{'excludes': es_excludes_fields})
        return search

    def get_es_search(self):
        if self.es_model is None:
            msg = "Cannot use %s on a view which does not have the 'es_model'"
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        index = self.es_model()._get_index()
        es_client = self.get_es_client()
        s = Search(using=es_client, index=index, doc_type=self.es_model)
        return s

    def do_search(self):
        search = self.filter_search(self.get_es_search())
        search = self.excludes_respond_fields(search)
        return search

    def es_representation(self, iterable):
        """List of object instances."""
        return [item.to_dict() for item in iterable]

    def get_queryset(self):
        """
        Get the list of elastic items for this view.
        This must be an iterable, and all items must be represented.
        """
        search = self.do_search()
        return self.es_representation(search)


class ListElasticAPIView(ListElasticMixin, ElasticAPIView):
    """Concrete view for listing a queryset."""
    es_pagination_class = ElasticLimitOffsetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
