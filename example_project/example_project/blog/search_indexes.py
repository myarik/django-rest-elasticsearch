# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from elasticsearch_dsl import (
    DocType,
    Date,
    Keyword,
    Text,
    Boolean
)


class BlogIndex(DocType):
    title = Text(fields={'raw': Keyword()})
    created_at = Date()
    body = Text()
    tags = Keyword(multi=True)
    is_published = Boolean()

    class Meta:
        index = 'blog'
