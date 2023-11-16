from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from modelon.impact.client.entities.interfaces.case import CaseInterface
from modelon.impact.client.entities.interfaces.custom_function import (
    CustomFunctionInterface,
)
from modelon.impact.client.entities.interfaces.experiment import ExperimentInterface
from modelon.impact.client.entities.interfaces.external_result import (
    ExternalResultInterface,
)
from modelon.impact.client.entities.interfaces.model import ModelInterface
from modelon.impact.client.entities.interfaces.model_executable import (
    ModelExecutableInterface,
)
from modelon.impact.client.experiment_definition.interfaces.extension import (
    BaseExperimentExtension,
)
from modelon.impact.client.options import (
    CompilerOptions,
    RuntimeOptions,
    SimulationOptions,
    SolverOptions,
)

if TYPE_CHECKING:
    from modelon.impact.client.entities.case import Case
    from modelon.impact.client.entities.custom_function import CustomFunction
    from modelon.impact.client.entities.experiment import Experiment
    from modelon.impact.client.entities.external_result import ExternalResult
    from modelon.impact.client.entities.model import Model
    from modelon.impact.client.entities.model_executable import ModelExecutable
    from modelon.impact.client.experiment_definition.extension import (
        SimpleExperimentExtension,
    )

    CaseOrExperimentOrExternalResult = Union[Case, Experiment, ExternalResult]
    RuntimeOptionsOrDict = Union[RuntimeOptions, Dict[str, Any]]
    SimulationOptionsOrDict = Union[SimulationOptions, Dict[str, Any]]
    SolverOptionsOrDict = Union[SolverOptions, Dict[str, Any]]
    CompilerOptionsOrDict = Union[CompilerOptions, Dict[str, Any]]


def assert_valid_args(
    model: Optional[Model] = None,
    fmu: Optional[ModelExecutable] = None,
    custom_function: Optional[CustomFunction] = None,
    solver_options: Optional[SolverOptionsOrDict] = None,
    simulation_options: Optional[SimulationOptionsOrDict] = None,
    compiler_options: Optional[CompilerOptionsOrDict] = None,
    runtime_options: Optional[RuntimeOptionsOrDict] = None,
) -> None:
    if fmu and not isinstance(fmu, ModelExecutableInterface):
        raise TypeError("FMU must be an instance of ModelExecutable class!")
    if model and not isinstance(model, ModelInterface):
        raise TypeError("Model must be an instance of Model class!")
    if custom_function and not isinstance(custom_function, CustomFunctionInterface):
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


def validate_initialize_from(
    entity: Optional[CaseOrExperimentOrExternalResult],
) -> None:
    if entity and not isinstance(
        entity, (CaseInterface, ExperimentInterface, ExternalResultInterface)
    ):
        raise TypeError(
            "The entity argument be an instance of "
            "Case or Experiment or ExternalResult!"
        )
    if isinstance(entity, ExperimentInterface) and len(entity.get_cases()) > 1:
        raise ValueError(
            "Cannot initialize from an experiment containing multiple"
            " cases! Please specify a case object instead."
        )


def assert_valid_case_modifiers(cases_modifiers: List[Dict[str, Any]]) -> None:
    if not isinstance(cases_modifiers, list):
        raise TypeError("The case modifiers argument must be a list!")
    for case_modifier in cases_modifiers:
        if not isinstance(case_modifier, dict):
            raise TypeError(
                "The variable modifiers in the case_modifier list must be a "
                "dictionary!"
            )


def assert_valid_extensions(
    experiment_extensions: List[SimpleExperimentExtension],
) -> None:
    if not isinstance(experiment_extensions, list):
        raise TypeError("The experiment extensions argument must be a list!")
    for extension in experiment_extensions:
        if not isinstance(extension, BaseExperimentExtension):
            raise TypeError(
                "The extension object in the experiment extension list "
                "must be an instance of SimpleExperimentExtension class!"
            )
