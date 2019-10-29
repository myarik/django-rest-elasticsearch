# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from rest_framework.test import APIRequestFactory
from elasticsearch_dsl import Q

from rest_framework_elasticsearch.es_filters import (
    ESFieldFilter, ElasticOrderingFilter, ElasticFieldsFilter,
    ElasticFieldsRangeFilter, ElasticSearchFilter, ElasticGeoBoundingBoxFilter, ElasticGeoDistanceFilter)
from rest_framework_elasticsearch.es_views import ElasticAPIView
from .test_data import DataDocType, DATA
from .utils import get_search_ids


rf = APIRequestFactory()


@pytest.mark.parametrize('dataset, expected', [
    (
        ('label', 'name', 'description'),
        ('label', 'name', 'description')
    ),
    (
        ('label', None, 'description'),
        ('label', 'label', 'description')
    ),
    (
        ('label', None, None),
        ('label', 'label', None)
    )
])
def test_es_field_filters(dataset, expected):
    ffilter = ESFieldFilter(dataset[0],
                            name=dataset[1],
                            description=dataset[2])
    assert expected == (ffilter.label, ffilter.name, ffilter.description)


class TestElasticOrderingFilter:

    def setup_method(self):
        self.backend = ElasticOrderingFilter()

    def create_view(self, es_ordering_fields):
        """Create and return test view class instance

        Args:
            es_ordering_fields (tuple): ordering fields
        Returns:
            ElasticAPIView: test view instance
        """
        view = ElasticAPIView()
        view.es_ordering_fields = es_ordering_fields
        return view

    @pytest.mark.parametrize('es_ordering_fields, expected', [
        (
            ("first_name", ("is_active", "active")),
            ("first_name", ("is_active", "active")),
        ),
        (
            "first_name",
            ("first_name",)
        )
    ])
    def test_get_es_ordering_fields(self, es_ordering_fields, expected):
        view = self.create_view(es_ordering_fields)
        result = self.backend.get_es_ordering_fields(view)
        assert expected == result

    @pytest.mark.parametrize('es_ordering_fields, expected', [
        (
            ("is_active", "active"),
            ("is_active", "active")
        ),
        (
            "first_name",
            ("first_name", "first_name")
        )
    ])
    def test_validation(self, es_ordering_fields, expected):
        result = ElasticOrderingFilter.validation(es_ordering_fields)
        assert expected == result

    def test_get_valid_fields_with_es_ordering_fields(self):
        es_ordering_fields = (
            "first_name",
            "last_name",
            ("is_active", "active")
        )
        view = self.create_view(es_ordering_fields)
        expected = [
            ("first_name", "first_name"),
            ("last_name", "last_name"),
            ("is_active", "active")
        ]
        result = self.backend.get_valid_fields([], view)
        assert result == expected

    def test_get_valid_fields_without_es_ordering_fields(self):
        view = self.create_view(None)
        valid_fields = []
        self.backend.get_default_valid_fields = lambda q, v: valid_fields
        result = self.backend.get_valid_fields([], view)
        assert result == valid_fields

    @pytest.mark.parametrize('fields, expected', [
        (
            ['first_name', 'last_name', '-active'],
            ['first_name', '-is_active']
        ),
        (
            ['+first_name', 'last_name', '#active'],
            ['+first_name']
        ),
        (
            ['+first_name', '-active'],
            ['+first_name', '-is_active']
        )
    ])
    def test_remove_invalid_fields(self, fields, expected):
        es_ordering_fields = (
            "first_name",
            ("is_active", "active")
        )
        view = self.create_view(es_ordering_fields)
        request = rf.get('/test/')
        result = self.backend.remove_invalid_fields([], fields, view, request)
        assert result == expected

    def test_filter_search(self, search):

        def get_expected():
            """Return expected data items sorted by id"""
            items = [
                (
                    item['_id'],
                    item['_source']['first_name'],
                    item['_source']['is_active']
                )
                for item in DATA
            ]
            items = sorted(items, key=lambda tup: (tup[1], not tup[2]))
            return items

        es_ordering_fields = (
            ("first_name", "first_name"),
            ("is_active", "-active")
        )
        view = self.create_view(es_ordering_fields)

        request = rf.get('/test/')
        request.query_params = {'ordering': 'first_name,active'}

        search = self.backend.filter_search(request, search, view)
        result = [
            (item.meta.id, item.first_name, item.is_active)
            for item in search[:len(DATA)].execute()
        ]
        assert result == get_expected()


class TestElasticFieldsFilter:

    def setup_method(self):
        self.backend = ElasticFieldsFilter()

    def create_view(self, es_filter_fields):
        """Create and return test view class instance

        Args:
            es_filter_fields ([ESFieldFilter]): filtering fields
        Returns:
            ElasticAPIView: test view instance
        """
        view = ElasticAPIView()
        view.es_model = DataDocType
        view.es_filter_fields = es_filter_fields
        return view

    def test_get_es_filter_fields(self):
        es_filter_fields = (
            ESFieldFilter('skills'),
            ESFieldFilter('active', 'is_active')
        )
        view = self.create_view(es_filter_fields)
        result = self.backend.get_es_filter_fields(view)
        assert result == es_filter_fields

    @pytest.mark.parametrize('es_filter_fields, query_params, expected', [
        (
            [ESFieldFilter('active', 'is_active')],
            {'active': 'False'},
            [3, 6, 8, 10]
        ),
        (
            [
                ESFieldFilter('birthday')
            ],
            {'birthday': '1985-03-17T12:20:09'},
            [1]
        ),
        (
            [ESFieldFilter('skills')],
            {'skills': 'python'},
            [1, 4, 5, 10]
        ),
        (
            [ESFieldFilter('skills')],
            {'skills': 'python,ruby'},
            [1, 4, 5, 6, 10]
        ),
        (
            [ESFieldFilter('active', 'is_active')],
            {'active': 'False', 'skills': 'python'},
            [3, 6, 8, 10]
        ),
        (
            [ESFieldFilter('active', 'is_active')],
            {'active': 'False', 'skills': 'python'},
            [3, 6, 8, 10]
        ),
        (
            [ESFieldFilter('score')],
            {'score': '200'},
            [2, 13]
        ),
    ])
    def test_filter_search(self, search, es_filter_fields,
                           query_params, expected):
        view = self.create_view(es_filter_fields)
        request = rf.get('/test/')
        request.query_params = query_params
        search = self.backend.filter_search(request, search, view)
        result = get_search_ids(search)
        assert sorted(result) == sorted(expected)


class TestElasticFieldsRangeFilter:

    def setup_method(self):
        self.backend = ElasticFieldsRangeFilter()

    def create_view(self, es_range_filter_fields):
        """Create and return test view class instance

        Args:
            es_range_filter_fields ([ESFieldFilter]): filtering range fields
        Returns:
            ElasticAPIView: test view instance
        """
        view = ElasticAPIView()
        view.es_model = DataDocType
        view.es_range_filter_fields = es_range_filter_fields
        return view

    def test_get_es_filter_fields(self):
        es_range_filter_fields = (
            ESFieldFilter('skills'),
            ESFieldFilter('active', 'is_active')
        )
        view = self.create_view(es_range_filter_fields)
        result = self.backend.get_es_range_filter_fields(view)
        assert result == es_range_filter_fields

    @pytest.mark.parametrize('es_filter_fields, query_params, expected', [
        (
            [ESFieldFilter('score')],
            {'from_score': '500'},
            [6, 7, 8, 10, 11]
        ),
        (
            [ESFieldFilter('score')],
            {'to_score': '100'},
            [1, 3, 5, 9, 12, 14]
        ),
        (
            [ESFieldFilter('score')],
            {'from_score': '500', 'to_score': '600'},
            [7, 8, 10]
        ),
        (
            [ESFieldFilter('score')], {}, [int(item['_id']) for item in DATA]
        ),
    ])
    def test_filter_search(self, search, es_filter_fields,
                           query_params, expected):
        view = self.create_view(es_filter_fields)
        request = rf.get('/test/')
        request.query_params = query_params
        search = self.backend.filter_search(request, search, view)
        search = self.backend.filter_search(request, search, view)
        result = get_search_ids(search)
        assert sorted(result) == sorted(expected)


class TestElasticSearchFilter:

    def setup_method(self):
        self.backend = ElasticSearchFilter()

    def create_view(self, es_search_fields):
        """Create and return test view class instance

        Args:
            es_search_fields ([ESFieldFilter]): search fields
        Returns:
            ElasticAPIView: test view instance
        """
        view = ElasticAPIView()
        view.es_model = DataDocType
        view.es_search_fields = es_search_fields
        return view

    @pytest.mark.parametrize('search_param, query_params, expected', [
        (
            None, {'search': 'test'}, 'test'
        ),
        (
            'search', {'search': 'test'}, 'test'
        ),
        (
            'q', {'q': 'test'}, 'test'
        ),
        (
            'search', {'q': 'test'}, ''
        ),
    ])
    def test_get_search_query(self, search_param, query_params, expected):
        request = rf.get('/test/')
        request.query_params = query_params
        if search_param:
            self.backend.search_param = search_param
        result = self.backend.get_search_query(request)
        assert result == expected

    def test_get_es_query(self):

        class TestElasticSearchFilter(ElasticSearchFilter):
            def get_es_query(self, s_query, s_fields, **kwargs):
                return Q("match", query=s_query, field=s_fields)

        s_query = "test"
        s_fields = "first_name"
        backend = TestElasticSearchFilter()
        result = backend.get_es_query(s_query, s_fields)
        expected = Q("match", query=s_query, field=s_fields)
        assert result == expected

    @pytest.mark.parametrize('es_search_fields, query_params, expected', [
        (
            ('first_name',),
            {'search': 'Zofia'},
            [1]
        ),
        (
            ('first_name', 'last_name', 'city'),
            {'search': 'Zofia'},
            [1]
        ),
        (
            ('first_name', 'last_name', 'city'),
            {'search': 'Zofia Rome'},
            [4, 7]
        ),
        (
            ('description'),
            {'search': 'information'},
            [2]
        ),
        (
            ('description'),
            {'search': 'Ford Prefect'},
            [2, 8, 10, 5, 6, 12]
        ),
        (
            ('description'),
            {'search': 'Earth'},
            [5, 3, 14]
        ),
        (
            ('description'),
            {'search': 'The Hitchhiker’s Guide'},
            [8]
        ),
    ])
    def test_filter_search(self, search, es_search_fields,
                           query_params, expected):
        view = self.create_view(es_search_fields)
        request = rf.get('/test/')
        request.query_params = query_params
        search = self.backend.filter_search(request, search, view)
        result = get_search_ids(search)

        # The es filters do not ensure the order.
        assert result.sort() == expected.sort()


class TestElasticGeoBoundingBoxFilter:

    def setup_method(self):
        self.backend = ElasticGeoBoundingBoxFilter()

    def create_view(self, es_geo_location_field, es_geo_location_field_name):
        """Create and return test view class instance

        Args:
            es_geo_location_field  ESFieldFilter
        Returns:
            ElasticAPIView: test view instance
        """
        view = ElasticAPIView()
        view.es_model = DataDocType
        view.es_geo_location_field = es_geo_location_field
        view.es_geo_location_field_name = es_geo_location_field_name
        return view

    @pytest.mark.parametrize('es_geo_location_field, es_geo_location_field_name, query_params, expected', [
        (
                ESFieldFilter('location'),
                'location',
                {'location': '25.55235365216549, 120.245361328125|21.861498734372567,122.728271484375'},  # Taiwan
                [14, 10, 12, 13, 11]  # Taiwan
        ),
        (
                ESFieldFilter('location'),
                'location',
                {'location': '43.99281450048989,-8.876953125|35.31736632923788,4.39453125'},  # Spain
                [1, 2, 3, 4]  # Spain
        ),
        (
                ESFieldFilter('location'),
                'location',
                {'location': '49.781264058178344,-125.5078125|24.206889622398023,-71.982421875'},  # USA
                [5, 6, 7]  # USA
        ),
    ])
    def test_geobounding_box_search(self, search, es_geo_location_field,
                                    es_geo_location_field_name, query_params, expected):

        view = self.create_view(es_geo_location_field, es_geo_location_field_name)

        request = rf.get('/test/')
        request.query_params = query_params
        search = self.backend.filter_search(request, search, view)
        result = get_search_ids(search)
        assert sorted(result) == sorted(expected)


class TestElasticGeoDistanceFilter:

    def setup_method(self):
        self.backend = ElasticGeoDistanceFilter()

    def create_view(self, es_geo_location_field, es_geo_location_field_name):
        """Create and return test view class instance

        Args:
            es_geo_location_field  ESFieldFilter
        Returns:
            ElasticAPIView: test view instance
        """
        view = ElasticAPIView()
        view.es_model = DataDocType
        view.es_geo_location_field = es_geo_location_field
        view.es_geo_location_field_name = es_geo_location_field_name
        return view

    @pytest.mark.parametrize('es_geo_location_field,es_geo_location_field_name, query_params, expected', [
        (
                ESFieldFilter('location'),
                'location',
                {'location': '800km|39.2663,-4.1748'},  # Spain
                [1, 2, 3, 4]  # Spain
        ),
        (
                ESFieldFilter('location'),
                'location',
                {'location': '500km|25.55235365216549,120.245361328125'},  # Taiwan
                [14, 10, 12, 13, 11]  # Taiwan
        ),
    ])
    def test_geodistance_search(self, search, es_geo_location_field,
                                es_geo_location_field_name, query_params, expected):

        view = self.create_view(es_geo_location_field, es_geo_location_field_name)

        request = rf.get('/test/')
        request.query_params = query_params
        search = self.backend.filter_search(request, search, view)
        result = get_search_ids(search)

        # The es filters do not ensure the order.
        assert sorted(result) == sorted(expected)