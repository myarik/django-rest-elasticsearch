# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .test_data import DATA


def get_search_ids(search):
    """Execute search and return list of items ids

    Args:
        search (elasticsearch_dsl.Search): search instance
    Returns:
        [int]: list of items ids
    """
    return [int(item.meta.id) for item in search[:len(DATA)].execute()]
