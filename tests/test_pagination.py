# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from rest_framework.test import APIRequestFactory
from rest_framework_elasticsearch.es_pagination import (
    ElasticLimitOffsetPagination)
from .test_data import DATA


rf = APIRequestFactory()


@pytest.fixture
def paginator(scope='function'):
    return ElasticLimitOffsetPagination()


def test_paginate_get_count(search, paginator):
    result = paginator._get_count(search)
    assert result == len(DATA)


@pytest.mark.parametrize('limit, offset, expected', [
    (5, 0, 5),
    (5, 5, 5),
    (5, 10, 4),
    (100, 0, 14),
    (100, 6, 8),
    (100, 50, 0),
    # default limit value is 10
    (0, 0, 10),
])
def test_paginate_search(search, paginator, limit, offset, expected):
    request = rf.get('/test/')
    request.query_params = {'limit': limit, 'offset': offset}
    result = paginator.paginate_search(search, request)
    assert len(result) == expected
