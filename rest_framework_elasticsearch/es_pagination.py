# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from rest_framework.pagination import LimitOffsetPagination


class ElasticLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10

    def _get_count(self, search):
        response = search.execute()
        return response.hits.total

    def paginate_search(self, search, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None
        self.offset = self.get_offset(request)
        self.count = self._get_count(search)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(search[self.offset:self.offset + self.limit])
