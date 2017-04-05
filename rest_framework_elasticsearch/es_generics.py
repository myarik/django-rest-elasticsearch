# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from rest_framework.generics import GenericAPIView

from .es_mixins import ListElasticMixin


class ListElasitcAPIView(ListElasticMixin,
                         GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list_elasticserach(request, *args, **kwargs)
