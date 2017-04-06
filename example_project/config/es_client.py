# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from elasticsearch import Elasticsearch, RequestsHttpConnection

es_client = Elasticsearch(
    hosts=['elasticsearch:9200/'],
    connection_class=RequestsHttpConnection
)
