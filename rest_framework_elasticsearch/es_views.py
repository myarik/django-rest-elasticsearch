# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from rest_framework import views

from .es_mixins import ListElasticMixin


class ListElasticAPIView(ListElasticMixin,
                         views.APIView):
    """
    Concrete view for listing a queryset.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
