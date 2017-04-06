# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

from django.conf.urls import url

from .views import BlogView

urlpatterns = [
    url(
        regex=r'^api/list$',
        view=BlogView.as_view(),
        name='blog-list'
    ),
]
