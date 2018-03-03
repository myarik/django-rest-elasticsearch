# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework import serializers


class BaseElasticSerializer(object):
    def es_instance(self):
        raise NotImplementedError

    def get_es_model(self):
        if not hasattr(self.Meta, 'es_model'):
            raise ValueError(
                'Can not find es_model value'
            )
        return self.Meta.es_model

    def save(self, using=None, index=None, validate=True, **kwargs):
        instance = self.es_instance()
        instance.save(using=using, index=index, validate=validate, **kwargs)

    def delete(self, using=None, index=None, **kwargs):
        instance = self.es_instance()
        instance.delete(using=using, index=index, **kwargs)


class ElasticSerializer(BaseElasticSerializer,
                        serializers.Serializer):
    def get_es_instace_pk(self, data):
        try:
            return data['id']
        except KeyError:
            raise ValueError(
                'Can not save object without id'
            )

    def es_repr(self, data):
        data['meta'] = dict(id=self.get_es_instace_pk(data))
        model = self.get_es_model()
        return model(**data)

    def es_instance(self):
        if not self.is_valid():
            raise serializers.ValidationError(self.errors)
        return self.es_repr(self.data)


class ElasticModelSerializer(BaseElasticSerializer,
                             serializers.ModelSerializer):
    def get_es_instace_pk(self, instance):
        return instance.pk

    def es_repr(self, instance):
        data = self.to_representation(instance)
        data['meta'] = dict(id=self.get_es_instace_pk(instance))
        model = self.get_es_model()
        return model(**data)

    def es_instance(self):
        if not self.instance:
            raise ValueError("Can't reproduce object")
        return self.es_repr(self.instance)
