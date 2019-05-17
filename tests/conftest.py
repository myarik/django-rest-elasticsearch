# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import pytest
import rest_framework

from elasticsearch_dsl import search as search_
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

from .test_data import create_test_index, DATA


DRF_VERSION = tuple(map(int, rest_framework.VERSION.split('.')))


def pytest_configure():
    import django
    from django.conf import settings

    settings.configure(
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        ROOT_URLCONF='tests.urls',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    "debug": True,  # We want template errors to raise
                }
            },
        ],
        ALLOWED_HOSTS=['localhost', 'testserver'],
        ES_CLIENT = connections.create_connection(hosts=[os.environ.get('TEST_ES_SERVER', {})], timeout=20)
    )

    django.setup()


@pytest.fixture(scope='session')
def es_client():
    """Create and return elasticsearch connection"""
    connection = Elasticsearch([os.environ.get('TEST_ES_SERVER', {})])
    connections.add_connection('default', connection)
    return connection


@pytest.fixture(scope='function')
def es_data_client(es_client):
    """Create elasticsearch index with preparing data and
    delete after exit of the scope.
    """
    create_test_index()
    bulk(es_client, DATA, raise_on_error=True, refresh=True)
    yield es_client
    es_client.indices.delete('test-*', ignore=404)


@pytest.fixture
def search(es_data_client, scope='function'):
    """Create and return Search test instance"""
    return search_.Search(index='test')
