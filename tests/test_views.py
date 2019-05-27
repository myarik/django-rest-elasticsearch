# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from django.core.exceptions import ImproperlyConfigured
from rest_framework.test import APIRequestFactory
from elasticsearch_dsl import Search

from rest_framework_elasticsearch.es_filters import (
    ESFieldFilter, ElasticOrderingFilter, ElasticFieldsFilter,
    ElasticFieldsRangeFilter, ElasticSearchFilter)
from rest_framework_elasticsearch.es_views import ElasticAPIView
from .test_data import DataDocType, DATA
from .utils import get_search_ids


rf = APIRequestFactory()


class TestElasticAPIView:
    """ElasticAPIView tests class"""

    def create_view(self, es_client):
        """Create and return test view class instance

        Args:
            es_client (Elasticsearch): elasticsearch connection client
        Returns:
            ElasticAPIView: test view instance
        """
        view = ElasticAPIView()
        view.es_client = es_client
        view.es_model = DataDocType
        view.es_filter_backends = (
            ElasticSearchFilter,
            ElasticFieldsFilter,
            ElasticFieldsRangeFilter,
            ElasticOrderingFilter
        )
        return view

    def test_get_es_search_fields(self):
        view = ElasticAPIView()
        assert view.get_es_search_fields() is None

        es_search_fields = ('first_name', 'last_name')
        view.es_search_fields = es_search_fields
        assert view.get_es_search_fields() == es_search_fields

    def test_get_es_filter_fields(self):
        view = ElasticAPIView()
        assert view.get_es_filter_fields() == tuple()

        es_filter_fields = ('first_name', 'last_name')
        view.es_filter_fields = es_filter_fields
        assert view.get_es_filter_fields() == es_filter_fields

    def test_get_es_range_filter_fields(self):
        view = ElasticAPIView()
        assert view.get_es_range_filter_fields() == tuple()

        es_range_filter_fields = ('first_name', 'last_name')
        view.es_range_filter_fields = es_range_filter_fields
        assert view.get_es_range_filter_fields() == es_range_filter_fields

    def test_get_es_ordering_fields(self):
        view = ElasticAPIView()
        assert view.get_es_ordering_fields() is None

        es_ordering_fields = ('first_name', 'last_name')
        view.es_ordering_fields = es_ordering_fields
        assert view.get_es_ordering_fields() == es_ordering_fields

    def test_get_es_excludes_fields(self):
        view = ElasticAPIView()
        assert view.get_es_excludes_fields() is None

        es_excludes_fields = ('first_name', 'last_name')
        view.es_excludes_fields = es_excludes_fields
        assert view.get_es_excludes_fields() == es_excludes_fields

    def test_get_es_client_without_es_client(self):
        view = ElasticAPIView()
        with pytest.raises(Exception) as err:
            view.get_es_client()
            assert err.message == (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % view.__class__.__name__
            )

    def test_get_es_client_with_wrong_es_client(self):
        view = ElasticAPIView()
        view.es_client = str
        with pytest.raises(ValueError):
            view.get_es_client()

    def test_get_es_client(self, es_data_client):
        view = ElasticAPIView()
        view.es_client = es_data_client
        assert view.get_es_client() == es_data_client

    def test_get_es_search_without_es_model(self, es_data_client):
        view = ElasticAPIView()
        with pytest.raises(ImproperlyConfigured) as err:
            view.get_es_search()
            assert err.message == (
                "Cannot use %s on a view which does not have the 'es_model'" %
                view.__class__.__name__
            )

    def test_get_es_search(self, es_data_client):
        view = self.create_view(es_data_client)
        expected = Search(using=es_data_client,
                          index='test',
                          doc_type=DataDocType)
        assert view.get_es_search().to_dict() == expected.to_dict()

    @pytest.mark.parametrize('query_params, expected', [
        (
            {'search': 'Ford Prefect'},
            [2, 8, 10, 5, 6, 12]
        ),
        (
            {'search': 'Earth'},
            [5, 3, 14]
        ),
        (
            {'search': 'Ford Prefect', 'active': 'False'},
            [6, 8, 10]
        ),
        (
            {'search': 'Ford Prefect', 'from_score': '200'},
            [2, 6, 8, 10]
        ),
    ])
    def test_filter_search(self, search, es_client, query_params, expected):
        view = self.create_view(es_client)
        view.es_search_fields = ('description',)
        view.es_filter_fields = (
            ESFieldFilter('skills'),
            ESFieldFilter('active', 'is_active')
        )
        view.es_range_filter_fields = (
            ESFieldFilter('score'),
        )

        view.request = rf.get('/test/')
        view.request.query_params = query_params

        search = view.filter_search(search)
        result = get_search_ids(search)
        assert sorted(result) == sorted(expected)

    def test_es_representation(self, search, es_client):
        view = self.create_view(es_client)

        view.request = rf.get('/test/')
        view.request.query_params = {'active': 'False'}

        search = view.filter_search(search)
        result = search[:len(DATA)].execute()
        expected = [item.to_dict() for item in result]
        assert view.es_representation(result) == expected

    def test_excludes_respond_fields(self, search, es_client):
        view = self.create_view(es_client)
        view.es_excludes_fields = (
            'last_name',
            'city',
            'skills',
            'birthday',
            'is_active',
            'description',
            'score',
            'location'
        )

        view.request = rf.get('/test/')
        view.request.query_params = {'active': 'False'}

        search = view.excludes_respond_fields(search)
        result = view.es_representation(search[:len(DATA)].execute())
        expected = {'first_name': 'test'}.keys()
        for item in result:
            assert item.keys() == expected

    def test_do_search(self, search, es_client):
        view = self.create_view(es_client)
        # mock get_es_search method
        view.get_es_search = lambda: search
        view.es_search_fields = ('description',)
        view.es_excludes_fields = ('birthday', 'description', 'score')

        view.request = rf.get('/test/')
        view.request.query_params = {'search': 'Earth', 'active': 'False'}

        search = view.do_search()
        result = search[:len(DATA)].execute()
        expected = [item.to_dict() for item in result]
        assert view.es_representation(result) == expected

    def test_get_queryset(self, search, es_client):
        view = self.create_view(es_client)
        # mock get_es_search method
        view.get_es_search = lambda: search
        view.es_filter_fields = (
            ESFieldFilter('active', 'is_active'),
        )
        view.es_search_fields = ('description',)
        view.es_ordering_fields = ("first_name",)
        view.es_excludes_fields = (
            'birthday',
            'score',
            'skills',
            'description',
            'location'
        )

        view.request = rf.get('/test/')
        view.request.query_params = {
            'search': 'Earth',
            'active': 'False',
            'ordering': 'first_name'
        }

        result = view.get_queryset()
        assert result == [
            {
                'city': 'Manila',
                'first_name': 'Samantha',
                'is_active': False,
                'last_name': 'Arundhati'
            }
        ]
