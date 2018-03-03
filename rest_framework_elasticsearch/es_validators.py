# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class BaseESFieldValidator:
    # Elastycsearch field types
    es_types = []

    @staticmethod
    @abstractmethod
    def validate(value):
        # must be implemented in your class, this method
        # validated value and retun python type or None
        pass


class BooleanFieldValidator(BaseESFieldValidator):
    es_types = ['boolean']

    @staticmethod
    def validate(value):
        if value in (True, 'True', 'true', '1', 1):
            return True
        elif value in (False, 'False', 'false', '0', 0):
            return False
        return None


class IntegerFieldValidator(BaseESFieldValidator):
    es_types = ['short', 'integer', 'long']

    @staticmethod
    def validate(value):
        try:
            data = int(value)
        except (ValueError, TypeError):
            data = None
        return data


class FloatFieldValidator(BaseESFieldValidator):
    es_types = ['float', 'double']

    @staticmethod
    def validate(value):
        try:
            data = float(value)
        except (ValueError, TypeError):
            data = None
        return data


class ESFieldValidator:
    """ Factory class for Elastycsearch field validators.

    Methood `clean_field` accepts two position arguments - field_type and value,
    get validators and return converted python value or None.
    """
    validators = (
        BooleanFieldValidator,
        IntegerFieldValidator,
        FloatFieldValidator
    )

    def __init__(self, *args, **kwargs):
        self._validators = {t: v for v in self.validators for t in v.es_types}

    def validate(self, field_type, value):
        validator = self._validators.get(field_type)
        return validator.validate(value) if validator else value


field_validator = ESFieldValidator()
