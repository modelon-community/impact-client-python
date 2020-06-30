import modelon.impact.client.experiment_definition as experiment_definition
import modelon.impact.client
import pytest


@pytest.fixture
def fmu():
    return modelon.impact.client.entities.ModelExecutable("Workspace", "Test")


def test_validate_workspaces(fmu):
    spec = experiment_definition.SimpleExperimentDefinition(
        fmu, "dynamic", parameters={}
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
