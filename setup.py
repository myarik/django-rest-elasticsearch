#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup, find_packages


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, '__init__.py'), 'rb') as init_py:
        src = init_py.read().decode('utf-8')
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", src).group(1)


setup(
    name='django-rest-elasticsearch',
    version=get_version('rest_framework_elasticsearch'),
    url='https://github.com/myarik/rest_framework_elasticsearch',
    license='BSD',
    description='Elasticsearch support for Django REST Framework',
    author='Yaroslav Muravskyi',
    author_email='y@myarik.com',

    packages=find_packages(
        where='.',
        exclude=('example_project*', )
    ),
    include_package_data=True,
    install_requires=[
        "Django>=1.8",
        "djangorestframework>=3.2.0",
        "elasticsearch-dsl>=5.0.0,<6.0.0"
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
