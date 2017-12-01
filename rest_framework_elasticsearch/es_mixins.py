# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework.response import Response


class ListElasticMixin(object):
    es_pagination_class = None

    @property
    def es_paginator(self):
        """The es_paginator instance associated with the view."""
        if not hasattr(self, '_es_paginator'):
            if self.es_pagination_class is None:
                self._es_paginator = None
            else:
                self._es_paginator = self.es_pagination_class()
        return self._es_paginator

    def paginate_search(self, search):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.es_paginator is None:
            return None
        return self.es_paginator.paginate_search(search, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.es_paginator is not None
        return self.es_paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        search = self.do_search()

        page = self.paginate_search(search)
        if page is not None:
            return self.get_paginated_response(self.es_representation(page))

        return Response(self.es_representation(search.scan()))
