# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
from rest_framework_elasticsearch.es_serializer import ElasticModelSerializer

from .models import Blog
from .search_indexes import BlogIndex


class ElasticBlogSerializer(ElasticModelSerializer):
    class Meta:
        model = Blog
        es_model = BlogIndex
        fields = ('pk', 'title', 'created_at', 'tags', 'body', 'is_published')
