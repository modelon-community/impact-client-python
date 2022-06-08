from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.experiment import Experiment


def validate_and_set_initialize_from(entity, definition):
    if isinstance(entity, Experiment):
        if len(entity.get_cases()) > 1:
            raise ValueError(
                "Cannot initialize from an experiment result containing multiple"
                " cases! Please specify a case object instead."
            )
        definition._initialize_from_experiment = entity
    elif isinstance(entity, Case):
        definition._initialize_from_case = entity
    elif isinstance(entity, ExternalResult):
        definition._initialize_from_external_result = entity
    else:
        raise TypeError(
            "The entity argument be an instance of "
            "modelon.impact.client.entities.case.Case or "
            "modelon.impact.client.entities.experiment.Experiment or "
            "modelon.impact.client.entities.external_result.ExternalResult!"
        )


def assert_unique_exp_initialization(*initializing_from):
    initializing_from = [entity for entity in initializing_from if entity is not None]
    if len(initializing_from) > 1:
        raise ValueError(
            "An experiment can only be initialized from one entity. Experiment is "
            f"configured to initialize from {' and '.join(map(str, initializing_from))}"
        )
