# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from rest_framework import views

from rest_framework_elasticsearch import es_mixins


class ListElasticAPIView(es_mixins.ListElasticMixin,
                         views.APIView):
    """
    Concrete view for listing a queryset.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

