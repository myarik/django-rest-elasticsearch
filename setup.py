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


def get_requires():
    """
    Return requires packages listend in `requirements.txt`.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    requirement_path = current_dir + '/requirements.txt'
    install_requires = []
    if os.path.isfile(requirement_path):
        with open(requirement_path) as f:
            install_requires = f.read().splitlines()
    return install_requires

def get_dev_requires():
    """
    Return development requires packages listend in `requirements_dev.txt`.
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    dev_requirement_path = current_dir + '/requirements_dev.txt'
 
    dev_install_requires = []
    if os.path.isfile(dev_requirement_path):
        with open(dev_requirement_path) as f:
            dev_install_requires = f.read().splitlines()
    return dev_install_requires


setup(
    name='django-rest-elasticsearch',
    version=get_version('rest_framework_elasticsearch'),
    url='https://github.com/myarik/rest_framework_elasticsearch',
    license='Apache 2.0',
    description='Elasticsearch support for Django REST Framework',
    author='Yaroslav Muravskyi',
    author_email='y@myarik.com',

    packages=find_packages(
        where='.',
        exclude=('example_project*','compose*')
    ),
    include_package_data=True,
    install_requires=get_requires(),
    tests_require=get_dev_requires(),
    setup_requires=get_dev_requires(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
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


