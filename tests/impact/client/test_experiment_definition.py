from modelon.impact.client import (
    SimpleExperimentDefinition,
    Range,
    Choices,
    SimpleExperimentExtension,
)
import pytest
from modelon.impact.client import exceptions

from tests.impact.client.fixtures import *


def test_experiment_definition_default_options(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param
    )
    config = definition.to_dict()
    assert config == {
        "experiment": {
            "version": 2,
            "base": {
                "model": {"fmu": {"id": "Test"}},
                "modifiers": {'variables': {}},
                "analysis": {
                    "type": "dynamic",
                    "parameters": {},
                    "simulationOptions": {"ncp": 500},
                    "solverOptions": {},
                    "simulationLogLevel": "WARNING",
                },
            },
            "extensions": [],
        }
    }


def test_experiment_definition_with_options(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu,
        custom_function=custom_function_no_param,
        simulation_options=custom_function_no_param.get_simulation_options().with_values(
            ncp=2000, rtol=0.0001
        ),
        solver_options={'a': 1},
    )
    config = definition.to_dict()
    assert config["experiment"]["base"]["analysis"]["simulationOptions"] == {
        "ncp": 2000,
        "rtol": 0.0001,
    }
    assert config["experiment"]["base"]["analysis"]["solverOptions"] == {"a": 1}


def test_experiment_definition_with_modifier(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param,
    ).with_modifiers({'h0': Range(0.1, 0.5, 3)}, v=Choices(0.1, 0.5, 3))
    config = definition.to_dict()
    assert config["experiment"]["base"]["modifiers"]["variables"] == {
        'h0': 'range(0.1,0.5,3)',
        'v': 'choices(0.1, 0.5, 3)',
    }


def test_experiment_definition_with_fmu_modifiers(
    fmu_with_modifiers, custom_function_no_param
):
    definition = SimpleExperimentDefinition(
        fmu_with_modifiers, custom_function=custom_function_no_param,
    )
    config = definition.to_dict()
    assert config["experiment"]["base"]["modifiers"]["variables"] == {'PI.K': 20}


def test_experiment_definition_with_extensions(fmu, custom_function_no_param):
    ext1 = SimpleExperimentExtension().with_modifiers(p=2)
    ext2 = SimpleExperimentExtension({'final_time': 10}).with_modifiers(p=3)
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param,
    ).with_extensions([ext1, ext2])
    config = definition.to_dict()
    assert config["experiment"]["extensions"] == [
        {"modifiers": {"variables": {"p": 2}}},
        {
            "modifiers": {"variables": {"p": 3}},
            "analysis": {"parameters": {'final_time': 10},},
        },
    ]


def test_experiment_definition_with_cases(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param,
    ).with_cases([{'p': 2}, {'p': 3}])
    config = definition.to_dict()
    assert config["experiment"]["extensions"] == [
        {"modifiers": {"variables": {"p": 2}}},
        {"modifiers": {"variables": {"p": 3}}},
    ]


def test_failed_compile_exp_def(
    fmu_compile_failed, custom_function_no_param, solver_options, simulation_options
):
    pytest.raises(
        exceptions.OperationFailureError,
        SimpleExperimentDefinition,
        fmu_compile_failed,
        custom_function_no_param,
        solver_options,
        simulation_options,
    )


def test_cancelled_compile_exp_def(
    fmu_compile_cancelled, custom_function_no_param, solver_options, simulation_options
):
    pytest.raises(
        exceptions.OperationFailureError,
        SimpleExperimentDefinition,
        fmu_compile_cancelled,
        custom_function_no_param,
        solver_options,
        simulation_options,
    )


def test_invalid_option_input(custom_function, custom_function_no_param):
    pytest.raises(
        TypeError,
        SimpleExperimentDefinition,
        custom_function,
        custom_function_no_param,
        {},
    )


def test_invalid_fmu_input(fmu, custom_function_no_param):
    pytest.raises(
        TypeError, SimpleExperimentDefinition, fmu, custom_function_no_param, "", ""
    )


def test_experiment_extension_default_options():
    ext = SimpleExperimentExtension()
    config = ext.to_dict()
    assert config == {}


def test_experiment_extension_with_options(custom_function_no_param):
    ext = SimpleExperimentExtension(
        {'stop_time': 5},
        {'a': 1},
        custom_function_no_param.get_simulation_options().with_values(
            ncp=2000, rtol=0.0001
        ),
    )
    config = ext.to_dict()
    assert config == {
        "analysis": {
            "parameters": {'stop_time': 5},
            "simulationOptions": {'ncp': 2000, 'rtol': 0.0001},
            "solverOptions": {'a': 1},
        },
    }


def test_experiment_extension_with_modifiers():
    ext = SimpleExperimentExtension().with_modifiers({'PI.k': 10}, P=5, d=15)
    config = ext.to_dict()
    assert config == {
        "modifiers": {"variables": {'PI.k': 10, 'P': 5, 'd': 15}},
    }


def test_experiment_extension_with_range_modifier():
    ext = SimpleExperimentExtension()
    pytest.raises(ValueError, ext.with_modifiers, {'h0': Range(0.1, 0.5, 3)})


def test_experiment_extension_with_choices_modifier():
    ext = SimpleExperimentExtension()
    pytest.raises(ValueError, ext.with_modifiers, {'h0': Choices(0.1, 0.5, 3)})


def test_invalid_with_extensions_input(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param,
    )
    pytest.raises(TypeError, definition.with_extensions, {})


def test_invalid_with_extensions_list_input(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param,
    )
    pytest.raises(TypeError, definition.with_extensions, [{}])


def test_invalid_with_cases_input(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param,
    )
    pytest.raises(TypeError, definition.with_cases, {})


def test_invalid_with_cases_list_input(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param,
    )
    pytest.raises(TypeError, definition.with_cases, [[]])
