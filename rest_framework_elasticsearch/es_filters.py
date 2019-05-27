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
    range_description = _('A range filter term.')

    def get_es_range_filter_fields(self, view):
        return view.get_es_range_filter_fields()

    def filter_search(self, request, search, view):
        es_model = getattr(view, 'es_model', None)
        for item in self.get_es_range_filter_fields(view):
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

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        fields = []
        for item in self.get_es_range_filter_fields(view):
            field = coreapi.Field(
                name='from_'+ item.label,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(item.label),
                    description=force_text(item.description or self.range_description)
                )
            )
            fields.append(field)
            field = coreapi.Field(
                name='to_'+ item.label,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(item.label),
                    description=force_text(item.description or self.range_description)
                )
            )
            fields.append(field)

        return fields

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


GEO_BOUNDING_BOX = 'geo_bounding_box'

class ElasticGeoBoundingBoxFilter(BaseEsFilterBackend):
    geo_bounding_box_param = ""
    geo_bounding_box_title = _('Geo Bounding Box')
    geo_bounding_box_description = _("""A Geo Bounding Box filter.
        Expects format {top left lat, lon}|{bottom right lat, lon}
        ex. Filter documents that are located in the given bounding box.
        44.87,40.07|43.87,41.11""")

    def get_geo_bounding_box_params(self, request, view):
        """
        Geo bounding box
        ?location__geo_bounding_box={top left lat, lon}|{bottom right lat, lon}
        ex. Filter documents that are located in the given bounding box.
        ?location__geo_bounding_box=44.87,40.07|43.87,41.11
        """

        location_field = view.get_es_geo_location_field()
        location_field_name = view.get_es_geo_location_field_name()

        if not location_field:
            return {}

        self.geo_bounding_box_param = location_field_name
        values = request.query_params.get(location_field_name, '').split('|')

        if len(values) < 2:
            return {}

        top_left_points = {}
        bottom_right_points = {}
        options = {}

        # Top left
        lat_lon = values[0].split(
            ','
        )
        if len(lat_lon) >= 2:
            top_left_points.update({
                'lat': float(lat_lon[0]),
                'lon': float(lat_lon[1]),
            })

        # Bottom right
        lat_lon = values[1].split(
            ','
        )
        if len(lat_lon) >= 2:
            bottom_right_points.update({
                'lat': float(lat_lon[0]),
                'lon': float(lat_lon[1]),
            })

        # Options
        for value in values[2:]:
            if ':' in value:
                opt_name_val = value.split(
                    ':'
                )
                if len(opt_name_val) >= 2:
                    if opt_name_val[0] in ('_name', 'validation_method', 'type'):
                        options.update(
                            {
                                opt_name_val[0]: opt_name_val[1]
                            }
                        )

        if not top_left_points or not bottom_right_points:
            return {}

        params = {
            self.geo_bounding_box_param: {
                'top_left': top_left_points,
                'bottom_right': bottom_right_points,
            }
        }

        params.update(options)
        return params

    def filter_search(self, request, search, view):
        geo_params = self.get_geo_bounding_box_params(request, view)

        if not geo_params:
            return search

        q = Q(GEO_BOUNDING_BOX, **geo_params)
        search = search.filter(q)
        return search

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.geo_bounding_box_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.geo_bounding_box_title),
                    description=force_text(self.geo_bounding_box_description)
                )
            )
        ]

GEO_DISTANCE = 'geo_distance'

class ElasticGeoDistanceFilter(BaseEsFilterBackend):
    geo_distance_param = ''
    geo_distance_title = _('Geo Distance')
    geo_distance_description = _("""A Geo Distance filter.
        Expects format {distance}{unit}|{lat}|{lon}.
        ex. Filter documents by radius of 100000km from the given location.
        100000km|12.04|-63.93""")

    def get_geo_distance_params(self, request, view):
        """
        Geo distance
        ?location__geo_distance={distance}{unit}|{lat}|{lon}
        ex. Filter documents by radius of 100000km from the given location.
        ?location__geo_distance=100000km|12.04|-63.93
        """
        location_field = view.get_es_geo_location_field()
        location_field_name = view.get_es_geo_location_field_name()

        if not location_field:
            return {}

        self.geo_distance_param = location_field_name
        values = request.query_params.get(self.geo_distance_param, '').split('|', 2)
        len_values = len(values)

        if len_values < 2:
            return {}

        lat_lon = values[1].split(',')

        params = {
            'distance': values[0],
        }
        if len(lat_lon) >= 2:
            params.update({
                self.geo_distance_param: {
                    'lat': float(lat_lon[0]),
                    'lon': float(lat_lon[1]),
                }
            })

        if len_values == 3:
            params['distance_type'] = values[2]

        return params

    def filter_search(self, request, search, view):
        geo_params = self.get_geo_distance_params(request, view)

        if not geo_params:
            return search

        q = Q(GEO_DISTANCE, **geo_params)
        search = search.query(q)
        return search

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.geo_distance_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.geo_distance_title),
                    description=force_text(self.geo_distance_description)
                )
            )
        ]
