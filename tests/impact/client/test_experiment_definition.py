from modelon.impact.client import (
    SimpleExperimentDefinition,
    Range
)
import pytest
import modelon.impact.client.exceptions as exceptions

from tests.impact.client.fixtures import *


def test_experiment_definition(fmu, custom_function_no_param):
    spec = SimpleExperimentDefinition(
        fmu,
        custom_function=custom_function_no_param,
        options=custom_function_no_param.options(),
    )
    config = spec.to_dict()
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
    spec = SimpleExperimentDefinition(
        fmu,
        custom_function=custom_function_no_param,
        options=custom_function_no_param.options()
        .with_simulation_options(ncp=2000, rtol=0.0001)
        .with_solver_options(a=1),
    )
    config = spec.to_dict()
    assert config["experiment"]["analysis"]["simulation_options"] == {
        "ncp": 2000,
        "rtol": 0.0001,
    }
    assert config["experiment"]["analysis"]["solver_options"] == {"a": 1}


def test_experiment_definition_with_modifier(fmu, custom_function_no_param):
    spec = SimpleExperimentDefinition(
        fmu,
        custom_function=custom_function_no_param,
        options=custom_function_no_param.options(),
    ).with_modifiers(v=1, h0=Range(0.1, 0.5, 3))
    config = spec.to_dict()
    assert config["experiment"]["modifiers"]["variables"] == {
        'h0': 'range(0.1,0.5,3)',
        'v': 1,
    }


def test_failed_compile_exp_def(fmu_compile_failed, custom_function_no_param, options):
    pytest.raises(
        exceptions.OperationFailureError,
        SimpleExperimentDefinition,
        fmu_compile_failed,
        custom_function_no_param,
        options,
    )


def test_cancelled_compile_exp_def(
    fmu_compile_cancelled, custom_function_no_param, options
):
    pytest.raises(
        exceptions.OperationFailureError,
        SimpleExperimentDefinition,
        fmu_compile_cancelled,
        custom_function_no_param,
        options,
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
        TypeError,
        SimpleExperimentDefinition,
        fmu,
        custom_function_no_param,
        {},
    )
