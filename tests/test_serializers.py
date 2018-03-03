# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

import pytest
from django.db import models

from rest_framework_elasticsearch.es_serializer import (
    BaseElasticSerializer, ElasticSerializer, ElasticModelSerializer)
from .test_data import DataDocType, DATA


class DjangoModel(models.Model):
    """Django ORM test model"""
    first_name = models.CharField(max_length=100)

    class Meta:
        app_label = 'tests'


class TestBaseElasticSerializer:

    def setup_method(self):
        self.serializer = BaseElasticSerializer()
        # mock serializer Meta class
        self.serializer.Meta = type(str('Meta'), tuple(), {})

    def test_es_instance(self):
        with pytest.raises(NotImplementedError):
            self.serializer.es_instance()

    def test_get_es_model_without_es_model(self):
        with pytest.raises(ValueError) as err:
            self.serializer.get_es_model()
            assert err.message == 'Can not find es_model value'

    def test_get_es_model(self):
        self.serializer.Meta.es_model = DataDocType
        assert self.serializer.get_es_model() == DataDocType

    def test_save_and_delete(self, es_client):
        # Preparing test data
        self.serializer.Meta.es_model = DataDocType
        instance = DataDocType(**DATA[0]['_source'])
        self.serializer.es_instance = lambda: instance

        # Test save method
        self.serializer.save()
        instance_id = instance.meta['id']
        result = DataDocType.get(id=instance_id)
        assert instance.to_dict() == result.to_dict()

        # Test Delete method
        self.serializer.delete()
        result = DataDocType.get(id=instance_id, ignore=404)
        assert result is None


class TestElasticSerializer:

    def setup_method(self):
        self.serializer = ElasticSerializer()
        # mock serializer Meta class
        self.serializer.Meta = type(str('Meta'), tuple(), {})
        self.serializer.Meta.es_model = DataDocType

    def test_get_es_instace_pk(self):
        # Test without id value
        with pytest.raises(ValueError) as err:
            self.serializer.get_es_instace_pk({})
            assert err.message == 'Can not save object without id'

        # Test with id value
        assert self.serializer.get_es_instace_pk({'id': 1}) == 1

    def test_es_repr(self):
        instance = DataDocType(**DATA[0]['_source'])
        data = instance.to_dict()
        data['id'] = 1
        model = self.serializer.es_repr(copy.copy(data))
        assert model.to_dict() == data


class TestElasticModelSerializer:

    def setup_method(self):
        self.serializer = ElasticModelSerializer()
        # mock serializer Meta class
        self.serializer.Meta = type(str('Meta'), tuple(), {})
        self.serializer.Meta.es_model = DataDocType

    def test_get_es_instace_pk(self):
        instance = DjangoModel(first_name='test')
        instance.pk = 1
        assert self.serializer.get_es_instace_pk(instance) == 1

    def test_es_repr(self):
        self.serializer.Meta.model = DjangoModel
        self.serializer.Meta.fields = ['first_name']

        instance = DjangoModel(first_name='test')
        instance.pk = 1

        model = self.serializer.es_repr(instance)
        assert model.to_dict() == {'first_name': 'test'}
