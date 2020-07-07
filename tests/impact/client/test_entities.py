import pytest

from modelon.impact.client.entities import CustomFunction


@pytest.fixture
def custom_function():
    return CustomFunction(
        'test',
        [
            {'name': 'p1', 'defaultValue': 1.0, 'type': 'Number'},
            {'name': 'p2', 'defaultValue': True, 'type': 'Boolean'},
            {
                'name': 'p3',
                'defaultValue': 'hej',
                'type': 'Enumeration',
                'values': ['hej', 'då'],
            },
            {'name': 'p4', 'defaultValue': 'a string', 'type': 'String'},
        ],
    )


def test_custom_function_with_parameters_ok(custom_function):
    new = custom_function.with_parameters(p1=3.4, p2=False, p3='då', p4='new string')
    assert new.parameter_values == {
        'p1': 3.4,
        'p2': False,
        'p3': 'då',
        'p4': 'new string',
    }


def test_custom_function_with_parameters_no_such_parameter(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, does_not_exist=3.4)


def test_custom_function_with_parameters_cannot_set_number_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p1='not a number')


def test_custom_function_with_parameters_cannot_set_boolean_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p2='not a boolean')


def test_custom_function_with_parameters_cannot_set_enumeration_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p3=4.6)


def test_custom_function_with_parameters_cannot_set_string_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p4=4.6)


def test_custom_function_with_parameters_cannot_set_enumeration_value(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p3='not in values')
