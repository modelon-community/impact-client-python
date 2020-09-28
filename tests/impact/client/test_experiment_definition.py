from modelon.impact.client import SimpleExperimentDefinition, Range
import pytest
from modelon.impact.client import exceptions

from tests.impact.client.fixtures import *


def test_experiment_definition(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param
    )
    config = definition.to_dict()
    assert config == {
        "experiment": {
            "analysis": {
                "analysis_function": "dynamic",
                "parameters": {},
                "simulation_options": {"ncp": 500},
                "solver_options": {},
                "simulation_log_level": "WARNING",
            },
            "fmu_id": "Test",
            "modifiers": {'variables': {}},
        }
    }


def test_experiment_definition_default_options(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param
    )
    config = definition.to_dict()
    assert config == {
        "experiment": {
            "analysis": {
                "analysis_function": "dynamic",
                "parameters": {},
                "simulation_options": {"ncp": 500},
                "solver_options": {},
                "simulation_log_level": "WARNING",
            },
            "fmu_id": "Test",
            "modifiers": {'variables': {}},
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
    assert config["experiment"]["analysis"]["simulation_options"] == {
        "ncp": 2000,
        "rtol": 0.0001,
    }
    assert config["experiment"]["analysis"]["solver_options"] == {"a": 1}


def test_experiment_definition_with_modifier(fmu, custom_function_no_param):
    definition = SimpleExperimentDefinition(
        fmu,
        custom_function=custom_function_no_param,
    ).with_modifiers({'h0': Range(0.1, 0.5, 3)}, v=1)
    config = definition.to_dict()
    assert config["experiment"]["modifiers"]["variables"] == {
        'h0': 'range(0.1,0.5,3)',
        'v': 1,
    }


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
