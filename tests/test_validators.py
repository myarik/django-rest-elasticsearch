# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from rest_framework_elasticsearch import es_validators


@pytest.mark.parametrize("value", (True, 'True', 'true', '1'))
def test_boolean_validator_true(value):
    assert es_validators.BooleanFieldValidator.validate(value)


@pytest.mark.parametrize("value", (False, 'False', 'false', '0'))
def test_boolean_validator_false(value):
    assert not es_validators.BooleanFieldValidator.validate(value)


@pytest.mark.parametrize("value", (20, 1.5, [5], {}, 'test', None))
def test_boolean_validator_invalid(value):
    assert es_validators.BooleanFieldValidator.validate(value) is None


@pytest.mark.parametrize("value", (0, 1, 50, 2.5, 300.02, 10e9, '42'))
def test_integer_validator_valid(value):
    expected = int(value)
    assert es_validators.IntegerFieldValidator.validate(value) == expected


@pytest.mark.parametrize("value", ('one', 'a1', {}, [], None))
def test_integer_validator_invalid(value):
    assert es_validators.IntegerFieldValidator.validate(value) is None


@pytest.mark.parametrize("value", (0, 1, 50, 2.5, 300.02, 10e9, '42'))
def test_float_validator_valid(value):
    expected = float(value)
    assert es_validators.FloatFieldValidator.validate(value) == expected


@pytest.mark.parametrize("value", ('one', 'a1', {}, [], None))
def test_float_validator_invalid(value):
    assert es_validators.FloatFieldValidator.validate(value) is None


@pytest.mark.parametrize("field_type, value, expected", [
    # BooleanFieldValidator
    ('boolean', 'true', True),
    ('boolean', '0', False),
    # IntegerFieldValidator
    ('short', '1', 1),
    ('integer', '100', 100),
    ('long', 2.5, 2),
    # FloatFieldValidator
    ('float', '2.5', 2.5),
    ('double', '100.01', 100.01),
    # Wrong field type
    ('test', 'test', 'test'),
])
def test_es_field_validator(field_type, value, expected):
    validator = es_validators.ESFieldValidator()
    assert validator.validate(field_type, value) == expected
