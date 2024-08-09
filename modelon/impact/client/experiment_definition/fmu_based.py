from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from modelon.impact.client import exceptions
from modelon.impact.client.entities.interfaces.case import CaseInterface
from modelon.impact.client.entities.interfaces.experiment import ExperimentInterface
from modelon.impact.client.entities.interfaces.external_result import (
    ExternalResultInterface,
)
from modelon.impact.client.experiment_definition.asserts import (
    assert_valid_args,
    assert_valid_case_modifiers,
    assert_valid_extensions,
    validate_initialize_from,
)
from modelon.impact.client.experiment_definition.extension import (
    SimpleExperimentExtension,
)
from modelon.impact.client.experiment_definition.interfaces.definition import (
    BaseExperimentDefinition,
)
from modelon.impact.client.experiment_definition.modifiers import (
    ensure_as_modifier,
    modifiers_to_dict,
)
from modelon.impact.client.experiment_definition.util import (
    case_to_identifier_dict,
    custom_function_parameters_to_dict,
    get_options,
)

if TYPE_CHECKING:
    from modelon.impact.client.entities.case import Case
    from modelon.impact.client.entities.custom_function import CustomFunction
    from modelon.impact.client.entities.experiment import Experiment
    from modelon.impact.client.entities.external_result import ExternalResult
    from modelon.impact.client.entities.model_executable import ModelExecutable
    from modelon.impact.client.options import SimulationOptions, SolverOptions

    CaseOrExperimentOrExternalResult = Union[Case, Experiment, ExternalResult]
    SimulationOptionsOrDict = Union[SimulationOptions, Dict[str, Any]]
    SolverOptionsOrDict = Union[SolverOptions, Dict[str, Any]]

logger = logging.getLogger(__name__)


def _assert_successful_compilation(fmu: ModelExecutable) -> None:
    if not fmu.is_successful():
        raise exceptions.OperationFailureError(
            "Compilation process has failed! See the log for more info!"
        )


class SimpleFMUExperimentDefinition(BaseExperimentDefinition):
    """A simple experiment definition class for defining experiments.

    Args:
        fmu: The FMU to be executed for this experiment.
        custom_function: The custom function to use for this experiment.

        solver_options: The solver options to use for this experiment.
            By default, the options is set to None, which means the
            default options for the custom_function input is used.
        simulation_options: The simulation_options to use for this
            experiment. By default, the options is set to None, which
            means the default options for the custom_function input is used.
        simulation_log_level: Simulation log level for this experiment.
            Default is 'WARNING'.
        initialize_from: Optional entity to initialize from. An instance of
            Case or Experiment or ExternalResult. Default: None

    Example::

        fmu = model.compile().wait()
        simulation_options = custom_function.get_simulation_options()
        .with_values(ncp=500)
        solver_options = {'atol':1e-8}
        simulate_def = fmu.new_experiment_definition(custom_function,
        solver_options, simulation_options)
        simulate_def.to_dict()

    """

    def __init__(
        self,
        fmu: ModelExecutable,
        custom_function: CustomFunction,
        solver_options: Optional[SolverOptionsOrDict] = None,
        simulation_options: Optional[SimulationOptionsOrDict] = None,
        simulation_log_level: str = "WARNING",
        initialize_from: Optional[CaseOrExperimentOrExternalResult] = None,
    ):
        assert_valid_args(
            fmu=fmu,
            custom_function=custom_function,
            solver_options=solver_options,
            simulation_options=simulation_options,
        )
        _assert_successful_compilation(fmu)
        self._fmu = fmu
        self._custom_function = custom_function
        self._solver_options = get_options(
            custom_function.get_solver_options, solver_options
        )
        self._simulation_options = get_options(
            custom_function.get_simulation_options, simulation_options
        )

        self._simulation_log_level = simulation_log_level
        self._initialize_from = initialize_from
        self._variable_modifiers = fmu._variable_modifiers()
        self._extensions: List[SimpleExperimentExtension] = []

    @property
    def fmu(self) -> ModelExecutable:
        """Returns the ModelExecutable class."""
        return self._fmu

    @property
    def modifiers(self) -> Dict[str, Any]:
        """Returns the variable modifiers dict."""
        return self._variable_modifiers

    @property
    def simulation_options(self) -> Dict[str, Any]:
        """Returns the simulation options as a dict."""
        return self._simulation_options

    @property
    def solver_options(self) -> Dict[str, Any]:
        """Returns the solver options as a dict."""
        return self._solver_options

    @property
    def simulation_log_level(self) -> str:
        """Returns the simulation log level."""
        return self._simulation_log_level

    @property
    def custom_function(self) -> CustomFunction:
        """Returns the custom function class."""
        return self._custom_function

    @property
    def extensions(self) -> List[SimpleExperimentExtension]:
        """Returns the list of experiment extensions."""
        return self._extensions

    @property
    def initialize_from(self) -> Optional[CaseOrExperimentOrExternalResult]:
        """Returns the case, experiment or result the experiment definition was
        initialized from."""
        return self._initialize_from

    def validate(self) -> None:
        add = set(self._variable_modifiers.keys()) - set(
            self._fmu.get_settable_parameters()
        )
        if add:
            raise KeyError(
                f"Paramter(s) '{', '.join(add)}' {'are' if len(add)>1 else 'is'} "
                "not a valid parameter modifier! Call the get_settable_parameters() "
                "method on the fmu to view the list of settable parameters."
            )

    def with_modifiers(
        self, modifiers: Optional[Dict[str, Any]] = None, **modifiers_kwargs: Any
    ) -> SimpleFMUExperimentDefinition:
        """Sets the modifiers parameters for an experiment.

        Args:
            modifiers: A dictionary of variable modifiers.

        Example::

            from modelon.impact.client import Range, Choices

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(
                custom_function).with_modifiers({'inertia1.J': Choices(0.1, 0.9),
                'inertia2.J': Range(0.1, 0.5, 3)})

        """
        if modifiers_kwargs:
            logger.warning(
                "The argument 'modifier_kwargs' is deprecated and will be removed in a"
                " future release of the Impact Client. Please specify a "
                "dictionary of variable modifiers instead!"
            )
        modifiers = {} if modifiers is None else modifiers
        modifiers_aggregate = {**modifiers, **modifiers_kwargs}
        new = SimpleFMUExperimentDefinition(
            self._fmu,
            self._custom_function,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
            self._initialize_from,
        )
        new._extensions = self._extensions
        new._variable_modifiers = self._variable_modifiers
        for name, value in modifiers_aggregate.items():
            new._variable_modifiers[name] = ensure_as_modifier(value)
        return new

    def with_extensions(
        self, experiment_extensions: List[SimpleExperimentExtension]
    ) -> SimpleFMUExperimentDefinition:
        """Sets up an experiment with multiple experiment extensions.

        Args:
            experiment_extensions: "A list of experiment extension objects.
                Extension object must an instance of  SimpleExperimentExtension class.

        Example::

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            with_extensions(
                [
                    SimpleExperimentExtension().with_modifiers({'PI.k': 20}),
                    SimpleExperimentExtension().with_modifiers({'PI.k': 30}),
                ]
            )

            experiment_definition = fmu.new_experiment_definition(custom_function).
            with_extensions(
                [
                    SimpleExperimentExtension(
                        parameter_modifiers={'start_time': 0.0, 'final_time': 2.0}
                    ).with_modifiers({'PI.k': 20})
                ]
            )

        """

        assert_valid_extensions(experiment_extensions)
        exp_ext = []
        for extension in experiment_extensions:
            exp_ext.append(extension)

        new = SimpleFMUExperimentDefinition(
            self._fmu,
            self._custom_function,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
            self._initialize_from,
        )
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions + exp_ext
        return new

    def with_cases(
        self, cases_modifiers: List[Dict[str, Any]]
    ) -> SimpleFMUExperimentDefinition:
        """Sets up an experiment with multiple cases with different variable modifiers.

        Args:
            cases_modifiers: A list of variable modifier dictionaries.
                Multiple dictionaries with variable modifiers could to added to create
                multiple cases.

        Example::

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(
                custom_function).with_cases([{'PI.k': 20}, {'PI.k': 30}])

        """
        assert_valid_case_modifiers(cases_modifiers)

        extensions = [
            SimpleExperimentExtension().with_modifiers(modifiers)
            for modifiers in cases_modifiers
        ]
        return self.with_extensions(extensions)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the experiment definition as a dictionary.

        Returns:
            A dictionary containing the experiment definition.

        Example::

            fmu = model.compile().wait()
            simulation_options = custom_function.get_simulation_options()
                .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_def = fmu.new_experiment_definition(custom_function,
            solver_options, simulation_options)
            simulate_def.to_dict()

        """
        custom_function_parameters = custom_function_parameters_to_dict(
            self._custom_function.parameter_values.as_raw_dict()
        )
        variable_modifiers = {
            name: ensure_as_modifier(value)
            for name, value in self._variable_modifiers.items()
        }
        exp_dict: Dict[str, Any] = {
            "experiment": {
                "version": 3,
                "base": {
                    "model": {"fmu": {"id": self._fmu.id}},
                    "modifiers": {"variables": modifiers_to_dict(variable_modifiers)},
                    "analysis": {
                        "type": self._custom_function.name,
                        "parameters": custom_function_parameters,
                        "simulationOptions": self._simulation_options,
                        "solverOptions": self._solver_options,
                        "simulationLogLevel": self._simulation_log_level,
                    },
                },
                "extensions": [ext.to_dict() for ext in self._extensions],
            }
        }
        if isinstance(self.initialize_from, ExperimentInterface):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFrom"
            ] = self.initialize_from.id
        elif isinstance(self.initialize_from, CaseInterface):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromCase"
            ] = case_to_identifier_dict(self.initialize_from)
        elif isinstance(self.initialize_from, ExternalResultInterface):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromExternalResult"
            ] = self.initialize_from.id
        return exp_dict

    def with_initialize_from(
        self, entity: Optional[CaseOrExperimentOrExternalResult] = None
    ) -> SimpleFMUExperimentDefinition:
        """Sets the experiment or case to initialize from for an experiment.

        Args:
            entity: An instance of Case or Experiment or ExternalResult."

        Example::

            experiment = workspace.get_experiment(experiment_id)
            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            experiment_definition.with_initialize_from(experiment)

            experiment = workspace.get_experiment(experiment_id)
            case = experiment.get_case('case_1')
            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            experiment_definition.with_initialize_from(case)

            result = workspace.upload_result('A.mat').wait()
            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            experiment_definition.with_initialize_from(result)

        """
        validate_initialize_from(entity)
        new = SimpleFMUExperimentDefinition(
            self._fmu,
            self._custom_function,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
            entity,
        )
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions

        return new
