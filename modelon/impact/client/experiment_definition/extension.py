from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from modelon.impact.client.entities.interfaces.case import CaseInterface
from modelon.impact.client.entities.interfaces.experiment import ExperimentInterface
from modelon.impact.client.experiment_definition.interfaces.extension import (
    BaseExperimentExtension,
)
from modelon.impact.client.experiment_definition.modifiers import (
    Modifier,
    ensure_as_modifier,
    modifiers_to_dict,
)
from modelon.impact.client.experiment_definition.operators import Operator
from modelon.impact.client.experiment_definition.util import (
    case_to_identifier_dict,
    custom_function_parameters_to_dict,
    get_options,
)

if TYPE_CHECKING:
    from modelon.impact.client.entities.case import Case
    from modelon.impact.client.entities.experiment import Experiment

    CaseOrExperiment = Union[Case, Experiment]

logger = logging.getLogger(__name__)


def _validate_initialize_from(entity: Optional[CaseOrExperiment]) -> None:
    if not entity:
        return
    if entity and not isinstance(entity, (ExperimentInterface, CaseInterface)):
        raise TypeError(
            "It is only supported to specify initialize from either Experiment "
            "or Case for experiment extensions"
        )
    if isinstance(entity, ExperimentInterface) and len(entity.get_cases()) > 1:
        raise ValueError(
            "Cannot initialize from an experiment containing multiple"
            " cases! Please specify a case object instead."
        )


class SimpleExperimentExtension(BaseExperimentExtension):
    """A simple experiment extension class for defining experiment extensions.

    Args:
        parameter_modifiers: The custom function parameters passes as a dictionary.
            By default, the parameter_modifier is set to None, which means the options
            set in the experiment definition will be used.
        solver_options: A solver options class instance of SolverOptions or
            a dictionary object containing the solver options. By
            default, the options is set to None, which means an empty dictionary
            is passed in the experiment extension.
        simulation_options: A simulation options class instance of SimulationOptions or
            a dictionary object containing the simulation options. By
            default, the options is set to None, which means an empty dictionary
            is passed in the experiment extension.
        simulation_log_level: Simulation log level for this experiment.
            Default: 'WARNING'.
        initialize_from: Optional entity to initialize from. An instance of
            Case or Experiment. Default: None

    Example::

        fmu = model.compile().wait()
        simulation_options = custom_function.get_simulation_options()
        .with_values(ncp=500)
        solver_options = {'atol':1e-8}
        simulate_def = fmu.new_experiment_definition(
            custom_function,
            solver_options=solver_options,
            simulation_options=simulation_options
        ).with_modifiers({'inertia1.J': 2})
        simulate_ext = SimpleExperimentExtension(
        {'start_time': 0.0, 'final_time': 4.0},
        solver_options,
        simulation_options.with_values(ncp=600)
        ).with_modifiers({'PI.k': 40})
        simulate_def = simulate_def.with_extensions(simulate_ext)
        simulate_def.to_dict()

    """

    def __init__(
        self,
        parameter_modifiers: Optional[Dict[str, Any]] = None,
        solver_options: Optional[Dict[str, Any]] = None,
        simulation_options: Optional[Dict[str, Any]] = None,
        simulation_log_level: Optional[str] = None,
        initialize_from: Optional[CaseOrExperiment] = None,
    ):
        _validate_initialize_from(initialize_from)
        self._parameter_modifiers = (
            {} if parameter_modifiers is None else parameter_modifiers
        )
        self._solver_options = get_options(dict, solver_options)
        self._simulation_options = get_options(dict, simulation_options)
        self._simulation_log_level = simulation_log_level
        self._variable_modifiers: Dict[str, Modifier] = {}
        self._initialize_from = initialize_from
        self._case_label: Optional[str] = None

    @property
    def simulation_options(self) -> Dict[str, Any]:
        "Returns the simulation options as a dict."
        return self._simulation_options

    @property
    def solver_options(self) -> Dict[str, Any]:
        "Returns the solver options as a dict."
        return self._solver_options

    @property
    def simulation_log_level(self) -> Optional[str]:
        "Returns the simulation log level, if set."
        return self._simulation_log_level

    @property
    def modifiers(self) -> Dict[str, Any]:
        "Returns the variable modifiers dict."
        return self._variable_modifiers

    @property
    def case_label(self) -> Optional[str]:
        "Returns the case label if any set."
        return self._case_label

    @property
    def initialize_from(self) -> Optional[CaseOrExperiment]:
        "Returns the case or experiment the experiment extension was initialized from."
        return self._initialize_from

    def with_modifiers(
        self, modifiers: Optional[Dict[str, Any]] = None, **modifiers_kwargs: Any
    ) -> SimpleExperimentExtension:
        """Sets the modifiers variables for an experiment extension.

        Args:
            modifiers: A dictionary of variable modifiers.

        Example::

            simulation_options = custom_function.get_simulation_options()
            .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_ext = SimpleExperimentExtension().with_modifiers({'PI.k': 40})
            simulate_ext = SimpleExperimentExtension(
            {'start_time': 0.0, 'final_time': 4.0},
            solver_options,
            simulation_options
            ).with_modifiers({'PI.k': 40})

        """
        if modifiers_kwargs:
            logger.warning(
                "The argument 'modifier_kwargs' is deprecated and will be removed in a"
                " future release of the Impact Client. Please specify a "
                "dictionary of variable modifiers instead!"
            )
        modifiers = {} if modifiers is None else modifiers
        modifiers_aggregate = {**modifiers, **modifiers_kwargs}
        new = SimpleExperimentExtension(
            self._parameter_modifiers,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
            self._initialize_from,
        )
        new._case_label = self._case_label
        for variable, value in modifiers_aggregate.items():
            if isinstance(value, Operator):
                raise ValueError(
                    "Operators are not supported when using extentions"
                    " in the experiment"
                )
            new._variable_modifiers[variable] = ensure_as_modifier(value)
        return new

    def with_case_label(self, case_label: str) -> SimpleExperimentExtension:
        """Sets the case label for an experiment extension.

        Args:
            case_label: A case label string.

        Example::

            simulation_options = custom_function.get_simulation_options()
            .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_ext = SimpleExperimentExtension().with_case_label(
            'Cruise condition')
            simulate_ext = SimpleExperimentExtension(
            {'start_time': 0.0, 'final_time': 4.0},
            solver_options,
            simulation_options
            ).with_case_label('Cruise condition')

        """
        new = SimpleExperimentExtension(
            self._parameter_modifiers,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
            self._initialize_from,
        )
        new._variable_modifiers = self._variable_modifiers
        new._case_label = case_label

        return new

    def with_initialize_from(
        self, entity: Optional[CaseOrExperiment] = None
    ) -> SimpleExperimentExtension:
        """Sets the experiment or case to initialize from for an experiment extension.

        Args:
            entity: An instance of Case or Experiment classes.

        Example::

            experiment = workspace.get_experiment(experiment_id)
            simulate_ext = SimpleExperimentExtension()
            simulate_ext.with_initialize_from(experiment)

            experiment = workspace.get_experiment(experiment_id)
            case = experiment.get_case('case_1')
            simulate_ext = SimpleExperimentExtension()
            simulate_ext.with_initialize_from(case)

        """
        _validate_initialize_from(entity)
        new = SimpleExperimentExtension(
            self._parameter_modifiers,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
            entity,
        )
        new._variable_modifiers = self._variable_modifiers
        new._case_label = self._case_label
        return new

    def to_dict(self) -> Dict[str, Any]:
        """Returns the experiment extensions as a dictionary.

        Returns:
            A dictionary containing the experiment extensions.

        Example::

            fmu = model.compile().wait()
            simulation_options = custom_function.get_simulation_options()
                .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_ext = SimpleExperimentExtension(
            {'start_time': 0.0, 'final_time': 4.0},
            solver_options,
            simulation_options,
            ).with_modifiers({'PI.k': 40})
            simulate_ext.to_dict()

        """
        ext_dict: Dict[str, Any] = {}
        if self._variable_modifiers:
            ext_dict.setdefault("modifiers", {})
            variable_modifiers = modifiers_to_dict(self._variable_modifiers)
            ext_dict["modifiers"]["variables"] = variable_modifiers

        if self._parameter_modifiers:
            ext_dict.setdefault("analysis", {})
            custom_function_parameters = custom_function_parameters_to_dict(
                self._parameter_modifiers
            )
            ext_dict["analysis"]["parameters"] = custom_function_parameters

        if self._solver_options:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["solverOptions"] = self._solver_options

        if self._simulation_options:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["simulationOptions"] = self._simulation_options

        if self._simulation_log_level:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["simulationLogLevel"] = self._simulation_log_level

        if isinstance(self.initialize_from, ExperimentInterface):
            ext_dict.setdefault("modifiers", {})
            ext_dict["modifiers"]["initializeFrom"] = self.initialize_from.id
        elif isinstance(self.initialize_from, CaseInterface):
            ext_dict.setdefault("modifiers", {})
            ext_dict["modifiers"]["initializeFromCase"] = case_to_identifier_dict(
                self.initialize_from
            )

        if self._case_label:
            ext_dict["caseData"] = [{"label": self._case_label}]

        return ext_dict
