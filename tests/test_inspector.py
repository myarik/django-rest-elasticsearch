# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from rest_framework_elasticsearch.es_views import ElasticAPIView
from rest_framework_elasticsearch.es_filters import (
    ElasticFieldsFilter, ElasticOrderingFilter, ElasticFieldsRangeFilter,
    ElasticSearchFilter, ESFieldFilter)
from rest_framework_elasticsearch import es_pagination
from rest_framework_elasticsearch.es_inspector import EsAutoSchema
from tests.conftest import DRF_VERSION


@pytest.mark.skipif(DRF_VERSION < (3, 7),
                    reason="The schema generation added in the DRF 3.7")
class TestEsAutoSchema:

    def setup_method(self):
        self.inspector = EsAutoSchema()

    def test_get_es_filter_fields(self):
        view = ElasticAPIView()
        view.es_filter_backends = (ElasticFieldsFilter,)
        view.es_filter_fields = (
            ESFieldFilter('score'),
            ESFieldFilter('description')
        )
        self.inspector.view = view
        for fields in (self.inspector.get_es_filter_fields('/', 'GET'),
                       self.inspector.get_filter_fields('/', 'GET')):
            field_names = [field.name for field in fields]
            assert sorted(field_names) == ['description', 'score']

    def test_get_es_filter_fields_with_range_filters(self):
        view = ElasticAPIView()
        view.es_filter_backends = (ElasticFieldsFilter,
                                   ElasticFieldsRangeFilter)
        view.es_filter_fields = (
            ESFieldFilter('score'),
            ESFieldFilter('description')
        )
        view.es_range_filter_fields = (ESFieldFilter('date'),)
        self.inspector.view = view
        for fields in (self.inspector.get_es_filter_fields('/', 'GET'),
                       self.inspector.get_filter_fields('/', 'GET')):
            field_names = [field.name for field in fields]
            assert sorted(field_names) == ['description', 'from_date', 'score', 'to_date']

    def test_get_es_pagination_fields(self):
        view = ElasticAPIView()
        view.es_pagination_class = es_pagination.ElasticLimitOffsetPagination
        self.inspector.view = view
        for fields in (self.inspector.get_es_pagination_fields('/', 'GET'),
                       self.inspector.get_pagination_fields('/', 'GET')):
            field_names = [field.name for field in fields]
            assert sorted(field_names) == ['limit', 'offset']

    def test_get_link(self):
        view = ElasticAPIView()
        view.es_filter_backends = (ElasticFieldsFilter,
                                   ElasticFieldsRangeFilter,
                                   ElasticOrderingFilter,
                                   ElasticSearchFilter)
        view.es_filter_fields = (
            ESFieldFilter('score'),
            ESFieldFilter('description')
        )
        view.es_range_filter_fields = (ESFieldFilter('date'),)
        view.es_pagination_class = es_pagination.ElasticLimitOffsetPagination
        self.inspector.view = view
        link = self.inspector.get_link('/', 'GET', 'localhost')
        field_names = [field.name for field in link.fields]
        assert sorted(field_names) == ['description', 'from_date', 'limit',
                                       'offset', 'ordering', 'score', 'search',
                                       'to_date']
