from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.options import (
    SolverOptions,
    SimulationOptions,
    RuntimeOptions,
    CompilerOptions,
)

import modelon.impact.client.entities.model

from modelon.impact.client.entities.custom_function import CustomFunction

import modelon.impact.client.entities.model_executable


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


def assert_valid_args(
    model=None,
    fmu=None,
    custom_function=None,
    solver_options=None,
    simulation_options=None,
    compiler_options=None,
    runtime_options=None,
):
    if fmu and not isinstance(
        fmu, modelon.impact.client.entities.model_executable.ModelExecutable
    ):
        raise TypeError("FMU must be an instance of ModelExecutable class!")
    if model and not isinstance(model, modelon.impact.client.entities.model.Model):
        raise TypeError("Model must be an instance of Model class!")
    if custom_function and not isinstance(custom_function, CustomFunction):
        raise TypeError("Custom_function must be an instance of CustomFunction class!")
    if solver_options is not None and not isinstance(
        solver_options, (SolverOptions, dict)
    ):
        raise TypeError(
            "Solver options must be an instance of SolverOptions class or a "
            "dictionary class object!"
        )
    if simulation_options is not None and not isinstance(
        simulation_options, (SimulationOptions, dict)
    ):
        raise TypeError(
            "Simulation options must be an instance of SimulationOptions class or"
            " a dictionary class object!"
        )
    if compiler_options is not None and not isinstance(
        compiler_options, (CompilerOptions, dict)
    ):
        raise TypeError(
            "Compiler options object must either be a dictionary or an "
            "instance of modelon.impact.client.options.CompilerOptions class!"
        )
    if runtime_options is not None and not isinstance(
        runtime_options, (RuntimeOptions, dict)
    ):
        raise TypeError(
            "Runtime options object must either be a dictionary or an "
            "instance of modelon.impact.client.options.RuntimeOptions class!"
        )
