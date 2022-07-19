import logging
from abc import ABC

from modelon.impact.client.experiment_definition.operators import Operator
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.experiment_definition.util import (
    get_options,
    case_to_identifier_dict,
)
from modelon.impact.client.experiment_definition.asserts import (
    validate_and_set_initialize_from,
    assert_unique_exp_initialization,
)

logger = logging.getLogger(__name__)


class BaseExperimentExtension(ABC):
    """
    Base class for an experiment extension class.
    """


class SimpleExperimentExtension(BaseExperimentExtension):
    """
    A simple experiment extension class for defining experiement extensions.

    Parameters:

        parameter_modifiers --
            The custom function parameters passes as a dictionary. By default, the
            parameter_modifier is set to None, which means the options set in
            the experiment definition will be used.

        solver_options --
            A solver options class instance of
            modelon.impact.client.options.SolverOptions or
            a dictionary object containing the solver options. By
            default, the options is set to None, which means an empty dictionary
            is passed in the experiment extension.

        simulation_options --
            A simulation options class instance of
            modelon.impact.client.options.SimulationOptions or
            a dictionary object containing the simulation options. By
            default, the options is set to None, which means an empty dictionary
            is passed in the experiment extension.

        simulation_log_level --
            Simulation log level for this experiment. Default: 'WARNING'.

    Examples::

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
        parameter_modifiers=None,
        solver_options=None,
        simulation_options=None,
        simulation_log_level=None,
    ):
        self._parameter_modifiers = (
            {} if parameter_modifiers is None else parameter_modifiers
        )
        self._solver_options = get_options(dict, solver_options)
        self._simulation_options = get_options(dict, simulation_options)
        self._simulation_log_level = simulation_log_level
        self._variable_modifiers = {}
        self._initialize_from_experiment = None
        self._initialize_from_case = None
        self._case_label = None

    def with_modifiers(self, modifiers=None, **modifiers_kwargs):
        """Sets the modifiers variables for an experiment extension.

        Parameters:

            modifiers --
                A dictionary of variable modifiers.

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
        )
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._case_label = self._case_label
        for variable, value in modifiers_aggregate.items():
            if isinstance(value, Operator):
                raise ValueError(
                    "Range operator is not supported when using extentions"
                    " in the experiment"
                )
            new._variable_modifiers[variable] = value
        return new

    def with_case_label(self, case_label):
        """Sets the case label for an experiment extension.

        Parameters:

            case_label --
                A case label string.

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
        )
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._variable_modifiers = self._variable_modifiers
        new._case_label = case_label

        return new

    def initialize_from(self, entity):
        """Sets the experiment or case to initialize from for an experiment extension.

        Parameters:

            entity --
                "An instance of modelon.impact.client.entities.case.Case or "
                "modelon.impact.client.entities.experiment.Experiment."

        Example::
            experiment = workspace.get_experiment(experiment_id)
            simulate_ext = SimpleExperimentExtension().initialize_from(experiment)

            experiment = workspace.get_experiment(experiment_id)
            case = experiment.get_case('case_1')
            simulate_ext = SimpleExperimentExtension().initialize_from(case)
        """
        new = SimpleExperimentExtension(
            self._parameter_modifiers,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
        )
        if isinstance(entity, ExternalResult):
            raise TypeError(
                "It is not supported to specify initialize from external result for "
                "experiment extensions"
            )

        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        validate_and_set_initialize_from(entity, new)
        assert_unique_exp_initialization(
            new._initialize_from_experiment, new._initialize_from_case,
        )
        new._variable_modifiers = self._variable_modifiers
        new._case_label = self._case_label
        return new

    def to_dict(self):
        """Returns the experiment extensions as a dictionary.

        Returns:

            extensions_dict --
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
        ext_dict = {}
        if self._variable_modifiers:
            ext_dict["modifiers"] = {"variables": self._variable_modifiers}

        if self._parameter_modifiers:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["parameters"] = self._parameter_modifiers

        if self._solver_options:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["solverOptions"] = self._solver_options

        if self._simulation_options:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["simulationOptions"] = self._simulation_options

        if self._simulation_log_level:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["simulationLogLevel"] = self._simulation_log_level

        if self._initialize_from_experiment:
            ext_dict["modifiers"][
                "initializeFrom"
            ] = self._initialize_from_experiment.id

        elif self._initialize_from_case:
            ext_dict["modifiers"]["initializeFromCase"] = case_to_identifier_dict(
                self._initialize_from_case
            )
        if self._case_label:
            ext_dict["caseData"] = [{"label": self._case_label}]

        return ext_dict
