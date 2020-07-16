import pytest
import unittest.mock

import modelon.impact.client.experiment_definition as experiment_definition
import modelon.impact.client
from modelon.impact.client.entities import CustomFunction, ExecutionOption


@pytest.fixture
def fmu():
    return modelon.impact.client.entities.ModelExecutable("Workspace", "Test")


@pytest.fixture
def custom_function():
    custom_function_service = unittest.mock.MagicMock()
    return CustomFunction("test_ws", 'dynamic', [], custom_function_service)


@pytest.fixture
def options():
    custom_function_service = unittest.mock.MagicMock()
    opts = {
        "compiler": {},
        "runtime": {},
        "simulation": {"ncp": 2000},
        "solver": {"rtol": 0.0001},
    }
    return ExecutionOption("test_ws", opts, "dynamic", custom_function_service)


def test_validate_workspaces(fmu, custom_function, options):
    spec = experiment_definition.SimpleExperimentDefinition(
        fmu, custom_function=custom_function, options=options
    )
    config = spec.to_dict
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
