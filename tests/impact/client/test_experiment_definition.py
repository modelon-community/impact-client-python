import pytest

import modelon.impact.client.experiment_definition as experiment_definition
import modelon.impact.client
from modelon.impact.client.entities import CustomFunction


@pytest.fixture
def fmu():
    return modelon.impact.client.entities.ModelExecutable("Workspace", "Test")


@pytest.fixture
def custom_function():
    return CustomFunction('dynamic', [])


def test_validate_workspaces(fmu, custom_function):
    spec = experiment_definition.SimpleExperimentDefinition(
        fmu, custom_function=custom_function
    )
    config = spec.to_dict
    assert config == {
        "experiment": {
            "analysis": {
                "analysis_function": "dynamic",
                "parameters": {},
                "simulation_options": {},
                "solver_options": {},
                "simulation_log_level": "WARNING",
            },
            "fmu_id": "Test",
            "modifiers": {"variables": {}},
        }
    }
