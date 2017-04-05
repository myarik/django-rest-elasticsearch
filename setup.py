#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, '__init__.py'), 'rb') as init_py:
        src = init_py.read().decode('utf-8')
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", src).group(1)


def read(*paths):
    """
    Build a file path from paths and return the contents.
    """
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='rest_framework_elasticsearch',
    version=get_version('rest_framework_elasticsearch'),
    url='https://github.com/myarik/rest_framework_elasticsearch',
    license='MIT License',
    description='Elasticsearch support for Django REST Framework',
    long_description=read('README.md'),
    author='Yaroslav Muravskyi',
    author_email='y@myarik.com',
    packages=[
        "rest_framework_elasticsearch",
    ],
    include_package_data=True,
    install_requires=[
        "Django>=1.8,<1.11",
        "djangorestframework>=3.2.0",
        "elasticsearch-dsl>=5.0.0,<6.0.0"
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
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
