from modelon.impact.client.client import Client
from modelon.impact.client.experiment_definition import (
    SimpleFMUExperimentDefinition,
    SimpleModelicaExperimentDefinition,
    SimpleExperimentExtension,
)
from modelon.impact.client.operators import Range, Choices

SimpleExperimentDefinition = SimpleFMUExperimentDefinition  # For compability
