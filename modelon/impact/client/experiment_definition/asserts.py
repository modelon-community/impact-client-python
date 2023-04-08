from __future__ import annotations
from typing import Optional, Dict, Union, Any, TYPE_CHECKING
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.options import (
    SolverOptions,
    SimulationOptions,
    RuntimeOptions,
    CompilerOptions,
)
from modelon.impact.client.entities.custom_function import CustomFunction
import modelon.impact.client.entities.model
import modelon.impact.client.entities.model_executable
import modelon.impact.client.experiment_definition.extension

CaseOrExperimentOrExternalResult = Union[Case, Experiment, ExternalResult]
RuntimeOptionsOrDict = Union[RuntimeOptions, Dict[str, Any]]
SimulationOptionsOrDict = Union[SimulationOptions, Dict[str, Any]]
SolverOptionsOrDict = Union[SolverOptions, Dict[str, Any]]
CompilerOptionsOrDict = Union[CompilerOptions, Dict[str, Any]]

if TYPE_CHECKING:
    from modelon.impact.client.entities.model import Model
    from modelon.impact.client.entities.model_executable import ModelExecutable


def assert_valid_args(
    model: Optional[Model] = None,
    fmu: Optional[ModelExecutable] = None,
    custom_function: Optional[CustomFunction] = None,
    solver_options: Optional[SolverOptionsOrDict] = None,
    simulation_options: Optional[SimulationOptionsOrDict] = None,
    compiler_options: Optional[CompilerOptionsOrDict] = None,
    runtime_options: Optional[RuntimeOptionsOrDict] = None,
) -> None:
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
            "instance of CompilerOptions class!"
        )
    if runtime_options is not None and not isinstance(
        runtime_options, (RuntimeOptions, dict)
    ):
        raise TypeError(
            "Runtime options object must either be a dictionary or an "
            "instance of RuntimeOptions class!"
        )
