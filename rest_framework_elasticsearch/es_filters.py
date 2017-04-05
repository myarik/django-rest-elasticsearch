# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from django.utils import six
from elasticsearch_dsl import Q

from rest_framework import filters
from rest_framework.settings import api_settings


class ESFieldFilter(object):
    def __init__(self, label, name=None):
        self.label = label
        self._name = name

    @property
    def name(self):
        if self._name is None:
            return self.label
        return self._name


class ElasticOrderingFilter(filters.OrderingFilter):
    def get_default_ordering(self, view):
        ordering = getattr(view, 'es_ordering', None)
        if isinstance(ordering, six.string_types):
            return (ordering,)
        return ordering

    def get_valid_fields(self, queryset, view, context={}):
        valid_fields = getattr(view, 'es_ordering_fields', self.ordering_fields)

        if valid_fields is None:
            # Default to allowing filtering on serializer fields
            return self.get_default_valid_fields(queryset, view, context)

        else:
            valid_fields = [
                (item, item) if isinstance(item, six.string_types) else item
                for item in valid_fields
                ]
        return valid_fields

    def filter_search(self, request, search, view):
        ordering = self.get_ordering(request, search, view)
        if ordering:
            search = search.sort(*ordering)
        return search


class ElasticFieldsFilter(object):
    @staticmethod
    def get_filter(request, field):
        params = request.query_params.get(field.label)
        if params:
            return {
                field.name: [param.strip() for param in params.split(',')]
            }

    def filter_search(self, request, search, view):
        filter_fields = getattr(view, 'es_filter_fields', None)
        if filter_fields:
            for field in filter_fields:
                q_filter = self.get_filter(request, field)
                if q_filter:
                    search = search.filter('terms', **q_filter)
        return search


class ElasticSearchFilter(object):
    search_param = api_settings.SEARCH_PARAM
    search_should_match = '75%'

    def get_search_query(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        return request.query_params.get(self.search_param, '')

    def filter_search(self, request, search, view):
        search_fields = getattr(view, 'es_search_fields', None)
        search_query = self.get_search_query(request)

        if not search_fields or not search_query:
            return search
        q = Q("multi_match", query=search_query, fields=search_fields)
        search = search.query(q)
        search.query.minimum_should_match = self.search_should_match
        return search
