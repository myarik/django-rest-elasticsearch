# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from rest_framework.test import APIRequestFactory

from rest_framework_elasticsearch.es_mixins import ListElasticMixin
from rest_framework_elasticsearch.es_views import ElasticAPIView
from rest_framework_elasticsearch.es_pagination import (
    ElasticLimitOffsetPagination)
from .test_data import DATA, DataDocType


rf = APIRequestFactory()


def create_view(es_client):
    """Create and return test view class instance

    Args:
        es_client (Elasticsearch): elasticsearch connection client
    Returns:
        (ListElasticMixin, ElasticAPIView): test view instance
    """

    class View(ListElasticMixin, ElasticAPIView):
        es_pagination_class = ElasticLimitOffsetPagination
        es_model = DataDocType
        es_search_fields = ('first_name',)

    return View()


def test_es_paginator_none():
    view = ListElasticMixin()
    assert view.es_paginator is None
    assert view._es_paginator is None


def test_es_paginator_class():
    view = ListElasticMixin()
    view.es_pagination_class = ElasticLimitOffsetPagination
    assert isinstance(view.es_paginator, ElasticLimitOffsetPagination)
    assert isinstance(view._es_paginator, ElasticLimitOffsetPagination)


def test_paginate_search_none(search):
    view = ListElasticMixin()
    assert view.paginate_search(search) is None


def test_get_paginated_response_none(search):
    view = ListElasticMixin()
    with pytest.raises(Exception):
        view.get_paginated_response(search)


def test_get_paginated_response(search):
    view = ListElasticMixin()
    view.es_pagination_class = ElasticLimitOffsetPagination

    view.request = rf.get('/test/')
    view.request.query_params = {}

    page = view.paginate_search(search)
    response = view.get_paginated_response(page)

    assert response.status_code == 200
    assert response.data['count'] == len(DATA)
    assert 'next' in response.data
    assert 'previous' in response.data
    assert 'results' in response.data


def test_list_paginated(search, es_client):
    view = create_view(es_client)
    # mock get_es_search method
    view.get_es_search = lambda: search

    view.request = rf.get('/test/')
    view.request.query_params = {}

    response = view.list(view.request)

    assert response.status_code == 200
    assert response.data['count'] == len(DATA)
    assert 'next' in response.data
    assert 'previous' in response.data
    assert len(response.data['results']) == 10


def test_list_representation(search, es_client):
    view = create_view(es_client)
    # mock get_es_search method
    view.get_es_search = lambda: search

    view.request = rf.get('/test/')
    view.request.query_params = {'search': 'Zofia'}

    response = view.list(view.request)

    assert response.status_code == 200
    assert response.data['count'] == 1
    assert response.data['next'] is None
    assert response.data['previous'] is None
    assert len(response.data['results']) == 1
