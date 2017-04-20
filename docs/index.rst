.. Elasticsearch for Django REST Framework documentation master file, created by
   sphinx-quickstart on Tue Apr 18 18:54:08 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Elasticsearch for Django REST Framework's
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   basic-usage
   pagination
   ordering

About
-----
Django REST Elasticsearch provides the easy way for integration `Django REST Framework <http://django-rest-framework.org/>`_ and `Elasticsearch <https://github.com/elastic/elasticsearch>`_.
The library uses `Elasticsearch DSL <https://github.com/elastic/elasticsearch-dsl-py>`_ library, it is a high-level library to the official low-level client.

Requirements
------------
- Django REST Framework 3.5 and above
- elasticsearch-dsl>=5.0.0,<6.0.0 (*Elasticsearch 5.x*)

Installation
------------
.. code-block:: none

    pip install django-rest-elasticsearch

Changelog
---------
v0.2.0
......

*Release date: 2017-04-07*
    - Initial release.
