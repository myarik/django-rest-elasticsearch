# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from functools import reduce
import re

from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from elasticsearch_dsl import Q

from rest_framework import filters
from rest_framework.settings import api_settings

from .es_validators import field_validator

try:
    from rest_framework.compat import coreapi, coreschema
except ImportError:
    coreapi = coreschema = None


ORDER_PATTERN = re.compile(r'(\?|[-+])?([.\w]+$)')


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

    def get_es_ordering_fields(self, view):
        ordering = view.get_es_ordering_fields()
        if isinstance(ordering, six.string_types):
            return (ordering,)
        return ordering

    @staticmethod
    def validation(field):
        return (field, field) if isinstance(field, six.string_types) else field

    def get_valid_fields(self, queryset, view, context={}):
        fields = self.get_es_ordering_fields(view)
        if not fields:
            return self.get_default_valid_fields(queryset, view)
        return [self.validation(field) for field in fields]

    def remove_invalid_fields(self, queryset, fields, view, request=None):
        """Remove not allowed ordering field."""
        ordering_fields = list()
        valid_fields = self.get_valid_fields(queryset,
                                             view,
                                             {'request': request})
        valid_fields = {field[1]: field[0] for field in valid_fields}
        for term in fields:
            res = ORDER_PATTERN.match(term)
            if not res:
                continue
            order, field = res.groups()
            match_field = valid_fields.get(field)
            if match_field and isinstance(match_field, six.string_types):
                ordering_fields.append((order or '') + match_field)
        return ordering_fields

    def filter_search(self, request, search, view):
        ordering = self.get_ordering(request, search, view)
        if ordering:
            search = search.sort(*ordering)
        return search


class ElasticFieldsFilter(BaseEsFilterBackend):
    filter_description = _('A filter term.')

    def get_es_filter_fields(self, view):
        return view.get_es_filter_fields()

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
            data = [field_validator.validate(field.name, value.strip())
                    for value in args.split(',')]
            # Remove empty string and None values
            data = [value for value in data if value not in (None, '')]
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
        return view.get_es_range_filter_fields()

    def filter_search(self, request, search, view):
        es_model = getattr(view, 'es_model', None)
        for item in self.get_es_filter_fields(view):
            try:
                field = reduce(lambda d, key: d[key] if d else None,
                               item.name.split('.'), es_model._doc_type.mapping)
            except KeyError:
                # Incorrect field
                continue

            from_arg_name = request.query_params.get('from_' + item.label, '')
            to_arg_name = request.query_params.get('to_' + item.label, '')

            from_arg = field_validator.validate(field.name, from_arg_name.strip())
            to_arg = field_validator.validate(field.name, to_arg_name.strip())

            options = {}

            if from_arg:
                options['gte'] = from_arg

            if to_arg:
                options['lte'] = to_arg

            if options:
                search = search.filter('range', **{item.name: options})

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

    def get_es_query(self, s_query, s_fields, **kwargs):
        """ Create and return elasticsearch Query.

        You could overload this method for creating your custom
        search Query object.

        Arguments:
            s_query: request search param
            s_fields: search fields

        Keyword arguments:
            request: request object
            view: view object
        """
        return Q("multi_match", query=s_query, fields=s_fields)

    def filter_search(self, request, search, view):
        s_query = self.get_search_query(request)
        s_fields = view.get_es_search_fields()
        if not s_query or not s_fields:
            return search

        q = self.get_es_query(s_query, s_fields, request=request, view=view)
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
