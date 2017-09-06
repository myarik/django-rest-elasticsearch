from config.es_client import es_client

from rest_framework_elasticsearch import es_views, es_pagination, es_filters
from .search_indexes import BlogIndex


class BlogView(es_views.ListElasticAPIView):
    es_client = es_client
    es_model = BlogIndex
    es_paginator_class = es_pagination.ElasticLimitOffsetPagination

    es_filter_backends = (
        es_filters.ElasticFieldsFilter,
        es_filters.ElasticSearchFilter,
        es_filters.ElasticOrderingFilter,
    )
    es_ordering = 'created_at'
    es_filter_fields = (
        es_filters.ESFieldFilter('tag', 'tags'),
        es_filters.ESFieldFilter('is_published', 'is_published')
    )
    es_search_fields = (
        'tags',
        'title',
    )
