import pytest
from modelon.impact.client.options import (
    CompilerOptions,
    SimulationOptions,
    SolverOptions,
    RuntimeOptions,
)

from tests.impact.client.fixtures import *


class TestCustomFunction:
    def test_custom_function_with_parameters_ok(self, custom_function):
        new = custom_function.with_parameters(
            p1=3.4, p2=False, p3='då', p4='new string', p5=4
        )
        assert new.parameter_values == {
            'p1': 3.4,
            'p2': False,
            'p3': 'då',
            'p4': 'new string',
            'p5': 4.0,
        }

    def test_custom_function_with_parameters_no_such_parameter(self, custom_function):
        pytest.raises(ValueError, custom_function.with_parameters, does_not_exist=3.4)

    def test_custom_function_with_parameters_cannot_set_number_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p1='not a number')

    def test_custom_function_with_parameters_cannot_set_boolean_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p2='not a boolean')

    def test_custom_function_with_parameters_cannot_set_enumeration_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3=4.6)

    def test_custom_function_with_parameters_cannot_set_string_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p4=4.6)

    def test_custom_function_with_parameters_cannot_set_enumeration_value(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3='not in values')

    def test_compiler_options(self, custom_function):
        new = custom_function.get_compiler_options().with_values(c_compiler='gcc')
        assert dict(new) == {"c_compiler": "gcc"}
        assert isinstance(new, CompilerOptions)
        defaults = custom_function.get_compiler_options(use_defaults=True)
        assert dict(defaults) == {'c_compiler': 'msvs'}

    def test_runtime_options(self, custom_function):
        new = custom_function.get_runtime_options().with_values(cs_solver=0)
        assert dict(new) == {"cs_solver": 0}
        assert isinstance(new, RuntimeOptions)
        defaults = custom_function.get_runtime_options(use_defaults=True)
        assert dict(defaults) == {'log_level': 2}

    def test_simulation_options(self, custom_function):
        new = custom_function.get_simulation_options().with_values(ncp=500)
        assert dict(new) == {"ncp": 500}
        assert isinstance(new, SimulationOptions)
        defaults = custom_function.get_simulation_options(use_defaults=True)
        assert dict(defaults) == {'ncp': 500}

    def test_solver_options(self, custom_function):
        new = custom_function.get_solver_options().with_values(atol=1e-7, rtol=1e-9)
        assert dict(new) == {'atol': 1e-7, 'rtol': 1e-9}
        assert isinstance(new, SolverOptions)
        defaults = custom_function.get_solver_options(use_defaults=True)
        assert dict(defaults) == {'rtol': 1e-05}
