import modelon.impact.client.experiment_definition as experiment_definition
import pytest
import modelon.impact.client.exceptions as exceptions
from tests.impact.client.fixtures import *


def test_experiment_definition(fmu, custom_function_no_param, options):
    spec = experiment_definition.SimpleExperimentDefinition(
        fmu, custom_function=custom_function_no_param, options=options
    )
    config = spec.to_dict()
    assert config == {
        "experiment": {
            "analysis": {
                "analysis_function": "dynamic",
                "parameters": {},
                "simulation_options": {"ncp": 2000},
                "solver_options": {"rtol": 0.0001},
                "simulation_log_level": "WARNING",
            },
            "fmu_id": "Test",
            "modifiers": {"variables": {}},
        }
    }


def test_failed_compile_exp_def(fmu_compile_failed, custom_function_no_param, options):
    pytest.raises(
        exceptions.OperationFailureError,
        experiment_definition.SimpleExperimentDefinition,
        fmu_compile_failed,
        custom_function_no_param,
        options,
    )


def test_cancelled_compile_exp_def(
    fmu_compile_cancelled, custom_function_no_param, options
):
    pytest.raises(
        exceptions.OperationFailureError,
        experiment_definition.SimpleExperimentDefinition,
        fmu_compile_cancelled,
        custom_function_no_param,
        options,
    )


def test_invalid_option_input(custom_function, custom_function_no_param):
    pytest.raises(
        TypeError,
        experiment_definition.SimpleExperimentDefinition,
        custom_function,
        custom_function_no_param,
        {},
    )


def test_invalid_fmu_input(fmu, custom_function_no_param):
    pytest.raises(
        TypeError,
        experiment_definition.SimpleExperimentDefinition,
        fmu,
        custom_function_no_param,
        {},
    )
