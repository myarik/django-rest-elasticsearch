# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
from functools import reduce

from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from elasticsearch_dsl import Q, ValidationException

from rest_framework import filters
from rest_framework.settings import api_settings
from rest_framework.compat import coreapi, coreschema


class ESFieldFilter(object):
    def __init__(self, label, name=None, description=None):
        self.label = label
        self._name = name
        # API docs filter description
        self.description = description

    @property
    def name(self):
        if self._name is None:
            return self.label
        return self._name


class BaseEsFilterBackend(object):
    """
    A base class from Elastycsearch filter backend classes.
    """

    def filter_search(self, request, search, view):
        """
        Return a filtered search.
        """
        raise NotImplementedError(".filter_search() must be overridden.")

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return []


class ElasticOrderingFilter(filters.OrderingFilter, BaseEsFilterBackend):

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


class ElasticFieldsFilter(BaseEsFilterBackend):
    filter_description = _('A filter term.')

    @staticmethod
    def clean_field(field, data):
        # Hook for validate bolean
        if field.name == 'boolean':
            if data in (True, 'True', 'true', '1'):
                return True
            elif data in (False, 'False', 'false', '0'):
                return False
            else:
                return
        try:
            data = field.clean(data)
        except ValidationException:
            return
        # Hook for validate integer
        if field.name in ['short', 'integer', 'long']:
            try:
                data = int(data)
            except (ValueError, TypeError):
                return

        # Hook for validate float
        if field.name in ['float', 'double']:
            try:
                data = float(data)
            except (ValueError, TypeError):
                return
        return data

    def get_es_filter_fields(self, view):
        return getattr(view, 'es_filter_fields', tuple())

    def filter_search(self, request, search, view):
        es_model = getattr(view, 'es_model', None)
        for item in self.get_es_filter_fields(view):
            try:
                field = reduce(lambda d, key: d[key] if d else None,
                               item.name.split('.'), es_model._doc_type.mapping)
            except KeyError:
                # Incorrect field
                continue
            args = request.query_params.get(item.label, '')
            data = [self.clean_field(field, value.strip()) for value in args.split(',')]
            # Remove empty string and None values
            data = [value for value in data
                    if value is not None and value is not '']
            if data:
                search = search.filter('terms', **{item.name: data})
        return search

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        fields = []
        for item in self.get_es_filter_fields(view):
            field = coreapi.Field(
                name=item.label,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(item.label),
                    description=force_text(item.description or self.filter_description)
                )
            )
            fields.append(field)

        return fields


class ElasticFieldsRangeFilter(ElasticFieldsFilter):

    def get_es_filter_fields(self, view):
        return getattr(view, 'es_range_filter_fields', tuple())

    def filter_search(self, request, search, view):
        es_model = getattr(view, 'es_model', None)
        for item in self.get_es_filter_fields(view):
            try:
                field = reduce(lambda d, key: d[key] if d else None,
                               item.name.split('.'), es_model._doc_type.mapping)
            except KeyError:
                # Incorrect field
                continue
            from_arg = self.clean_field(
                field,
                request.query_params.get('from_{}'.format(item.label), '').strip()
            )
            to_arg = self.clean_field(
                field,
                request.query_params.get('to_{}'.format(item.label), '').strip()
            )

            options = {}
            if from_arg:
                options['gte'] = from_arg
            if to_arg:
                options['lte'] = to_arg
            if options:
                search = search.filter(
                    'range',
                    **{item.name: options}
                )
        return search


class ElasticSearchFilter(BaseEsFilterBackend):
    search_param = api_settings.SEARCH_PARAM
    search_should_match = '75%'
    search_title = _('Search')
    search_description = _('A search term.')

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

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.search_title),
                    description=force_text(self.search_description)
                )
            )
        ]
