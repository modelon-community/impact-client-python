from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List, TYPE_CHECKING, Union, Type

from modelon.impact.client.experiment_definition.operators import Operator
from modelon.impact.client import exceptions
from modelon.impact.client.experiment_definition.extension import (
    SimpleExperimentExtension,
)
from modelon.impact.client.experiment_definition.expansion import (
    ExpansionAlgorithm,
    FullFactorial,
)
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.experiment_definition.util import (
    get_options,
    case_to_identifier_dict,
)
from modelon.impact.client.experiment_definition.asserts import (
    assert_valid_args,
)

if TYPE_CHECKING:
    from modelon.impact.client.entities.model import Model
    from modelon.impact.client.entities.custom_function import CustomFunction
    from modelon.impact.client.entities.model_executable import ModelExecutable
    from modelon.impact.client.options import (
        SolverOptions,
        SimulationOptions,
        CompilerOptions,
        RuntimeOptions,
    )

    CaseOrExperimentOrExternalResult = Union[Case, Experiment, ExternalResult]
    RuntimeOptionsOrDict = Union[RuntimeOptions, Dict[str, Any]]
    SimulationOptionsOrDict = Union[SimulationOptions, Dict[str, Any]]
    SolverOptionsOrDict = Union[SolverOptions, Dict[str, Any]]
    CompilerOptionsOrDict = Union[CompilerOptions, Dict[str, Any]]

logger = logging.getLogger(__name__)


def _validate_initialize_from(
    entity: Optional[CaseOrExperimentOrExternalResult],
) -> None:
    if entity and not isinstance(entity, (Case, Experiment, ExternalResult)):
        raise TypeError(
            "The entity argument be an instance of "
            "Case or Experiment or ExternalResult!"
        )
    if isinstance(entity, Experiment) and len(entity.get_cases()) > 1:
        raise ValueError(
            "Cannot initialize from an experiment containing multiple"
            " cases! Please specify a case object instead."
        )


def _assert_successful_compilation(fmu: ModelExecutable) -> None:
    if not fmu.is_successful():
        raise exceptions.OperationFailureError(
            "Compilation process has failed! See the log for more info!"
        )


def _assert_valid_case_modifiers(cases_modifiers: List[Dict[str, Any]]) -> None:
    if not isinstance(cases_modifiers, list):
        raise TypeError("The case modifiers argument must be a list!")
    for case_modifier in cases_modifiers:
        if not isinstance(case_modifier, dict):
            raise TypeError(
                "The variable modifiers in the case_modifier list must be a "
                "dictionary!"
            )


def _assert_valid_extensions(
    experiment_extensions: List[SimpleExperimentExtension],
) -> None:
    if not isinstance(experiment_extensions, list):
        raise TypeError("The experiment extensions argument must be a list!")
    for extension in experiment_extensions:
        if not isinstance(extension, SimpleExperimentExtension):
            raise TypeError(
                "The extension object in the experiment extension list "
                "must be an instance of SimpleExperimentExtension class!"
            )


class BaseExperimentDefinition(ABC):
    """Base class for an Experiment definition class."""

    @abstractmethod
    def validate(self) -> None:
        """Validates the modifiers appended to the experiment definition."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Returns the experiment definition as a dictionary."""


class SimpleFMUExperimentDefinition(BaseExperimentDefinition):
    """A simple experiment definition class for defining experiements.

    Args:
        fmu: The FMU to be excecuted for this experiment.
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
        for variable, value in modifiers_aggregate.items():
            new._variable_modifiers[variable] = (
                str(value) if isinstance(value, Operator) else value
            )
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

        _assert_valid_extensions(experiment_extensions)
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
        """Sets up an experiment with multiple cases with different variable
        modifiers.

        Args:
            cases_modifiers: A list of variable modifier dictionaries.
                Multiple dictionaries with variable modifiers could to added to create
                multiple cases.

        Example::

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(
                custom_function).with_cases([{'PI.k': 20}, {'PI.k': 30}])

        """
        _assert_valid_case_modifiers(cases_modifiers)

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
        exp_dict: Dict[str, Any] = {
            "experiment": {
                "version": 2,
                "base": {
                    "model": {"fmu": {"id": self._fmu.id}},
                    "modifiers": {"variables": self._variable_modifiers},
                    "analysis": {
                        "type": self._custom_function.name,
                        "parameters": self._custom_function.parameter_values,
                        "simulationOptions": self._simulation_options,
                        "solverOptions": self._solver_options,
                        "simulationLogLevel": self._simulation_log_level,
                    },
                },
                "extensions": [ext.to_dict() for ext in self._extensions],
            }
        }
        if isinstance(self.initialize_from, Experiment):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFrom"
            ] = self.initialize_from.id
        elif isinstance(self.initialize_from, Case):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromCase"
            ] = case_to_identifier_dict(self.initialize_from)
        elif isinstance(self.initialize_from, ExternalResult):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromExternalResult"
            ] = self.initialize_from.id
        return exp_dict

    @property
    def initialize_from(self) -> Optional[CaseOrExperimentOrExternalResult]:
        return self._initialize_from

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

            result = workspace.upload_result('C:/A.mat').wait()
            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            experiment_definition.with_initialize_from(result)

        """
        _validate_initialize_from(entity)
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


class SimpleModelicaExperimentDefinition(BaseExperimentDefinition):
    """A simple experiment definition class for defining experiements.

    Args:
        model: The Model class object.
        custom_function:bThe custom function to use for this experiment.
        compiler_options:bThe compiler options to use for this experiment.
            By default the options is set to None, which means the default
            options for the custom_function input is used.
        fmi_target: Compiler target. Possible values are 'me' and 'cs'. Default: 'me'.
        fmi_version: The FMI version. Valid options are '1.0' and '2.0'. Default: '2.0'.
        platform: Platform for FMU binary.The OS running the Impact server must match
            the environment that runs the compiled FMU. This is necessary as the
            binaries packaged with the FMU are based on the platform generating
            the FMU. For example, if the Impact server is running Linux the binary
            in the downloaded FMU is compiled for Linux. The downloaded FMU can
            then not be simulated on Windows. Default: 'auto'. Supported options are:-

            - 'auto': platform is selected automatically
            - 'linux64': generate a 32 bit FMU
            - 'win32': generate a 32 bit FMU
            - 'win64': generate a 64 bit FMU
        compiler_log_level: The logging for the compiler. Possible values are "error",
            "warning", "info", "verbose" and "debug". Default: 'warning'.
        runtime_options: The runtime options to use for this experiment. By default the
            options is set to None, which means the default options for the
            custom_function input is used.
        solver_options: The solver options to use for this experiment. By default the
            options is set to None, which means the default options for the
            custom_function input is used.
        simulation_options: The simulation options to use for this experiment. By
            default the options is set to None, which means the default options for the
            custom_function input is used.
        simulation_log_level: Simulation log level for this experiment.
            Default: 'WARNING'.
        initialize_from: Optional entity to initialize from. An instance of
            Case or Experiment or ExternalResult. Default: None

    Example::

        model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
        simulation_options = custom_function.get_simulation_options()
        .with_values(ncp=500)
        solver_options = {'atol':1e-8}
        simulate_def = model.new_experiment_definition(
            custom_function,
            solver_options=solver_options,
            simulation_options=simulation_options
        )
        simulate_def.to_dict()

    """

    def __init__(
        self,
        model: Model,
        custom_function: CustomFunction,
        *,
        compiler_options: Optional[CompilerOptionsOrDict] = None,
        fmi_target: str = "me",
        fmi_version: str = "2.0",
        platform: str = "auto",
        compiler_log_level: str = "warning",
        runtime_options: Optional[RuntimeOptionsOrDict] = None,
        solver_options: Optional[SolverOptionsOrDict] = None,
        simulation_options: Optional[SimulationOptionsOrDict] = None,
        simulation_log_level: str = "WARNING",
        initialize_from: Optional[CaseOrExperimentOrExternalResult] = None,
    ):
        assert_valid_args(
            model=model,
            custom_function=custom_function,
            compiler_options=compiler_options,
            runtime_options=runtime_options,
            solver_options=solver_options,
            simulation_options=simulation_options,
        )
        self._model = model
        self._custom_function = custom_function
        self._compiler_options = get_options(
            custom_function.get_compiler_options, compiler_options
        )
        self._runtime_options = get_options(
            custom_function.get_runtime_options, runtime_options
        )
        self._fmi_target = fmi_target
        self._fmi_version = fmi_version
        self._platform = platform
        self._compiler_log_level = compiler_log_level
        self._solver_options = get_options(
            custom_function.get_solver_options, solver_options
        )
        self._simulation_options = get_options(
            custom_function.get_simulation_options, simulation_options
        )
        self._simulation_log_level = simulation_log_level
        self._initialize_from = initialize_from
        self._variable_modifiers: Dict[str, Any] = {}
        self._extensions: List[SimpleExperimentExtension] = []
        self._expansion = FullFactorial()

    def validate(self) -> None:
        raise NotImplementedError(
            "Validation is not supported for SimpleModelicaExperimentDefinition class"
        )

    def with_modifiers(
        self,
        modifiers: Optional[Dict[str, Any]] = None,
    ) -> SimpleModelicaExperimentDefinition:
        """Sets the modifiers parameters for an experiment.

        Args:
            modifiers: A dictionary of variable modifiers. Could be used if
                modifiers keys conflict with python identifiers or keywords.
                Default: None.

        Example::

            from modelon.impact.client import Range, Choices

            model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
            experiment_definition = model.new_experiment_definition(
                custom_function).with_modifiers({'inertia1.J': Choices(0.1, 0.9),
                'inertia2.J': Range(0.1, 0.5, 3)})

        """
        modifiers = {} if modifiers is None else modifiers
        new = SimpleModelicaExperimentDefinition(
            model=self._model,
            custom_function=self._custom_function,
            compiler_options=self._compiler_options,
            fmi_target=self._fmi_target,
            fmi_version=self._fmi_version,
            platform=self._platform,
            compiler_log_level=self._compiler_log_level,
            runtime_options=self._runtime_options,
            solver_options=self._solver_options,
            simulation_options=self._simulation_options,
            simulation_log_level=self._simulation_log_level,
            initialize_from=self._initialize_from,
        )
        new._extensions = self._extensions
        new._expansion = self._expansion

        for variable, value in modifiers.items():
            new._variable_modifiers[variable] = (
                str(value) if isinstance(value, Operator) else value
            )
        return new

    def with_expansion(
        self, expansion: Optional[Type[ExpansionAlgorithm]] = None
    ) -> SimpleModelicaExperimentDefinition:
        """Sets the expansion algorithm for an experiment.

        Args:
            expansion: An expansion algorithm. Avaiable algorithms are LatinHypercube,
                Sobol and FullFactorial.
                Default: FullFactorial.

        Example::

            from modelon.impact.client import Sobol, Beta

            model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
            experiment_definition = model.new_experiment_definition(
                custom_function).with_modifiers({'inertia1.J': Beta(0.1, 0.9),
                'inertia2.J': Normal(0.1, 0.5)}).with_expansion(Sobol(5))

        """
        if not isinstance(expansion, ExpansionAlgorithm):
            raise TypeError(
                f"The expansion argument is of type '{type(expansion)}' "
                "which is not a subtype of 'ExpansionAlgorithm'!"
            )
        expansion = expansion or FullFactorial()
        new = SimpleModelicaExperimentDefinition(
            model=self._model,
            custom_function=self._custom_function,
            compiler_options=self._compiler_options,
            fmi_target=self._fmi_target,
            fmi_version=self._fmi_version,
            platform=self._platform,
            compiler_log_level=self._compiler_log_level,
            runtime_options=self._runtime_options,
            solver_options=self._solver_options,
            simulation_options=self._simulation_options,
            simulation_log_level=self._simulation_log_level,
            initialize_from=self._initialize_from,
        )
        new._extensions = self._extensions
        new._expansion = expansion
        new._variable_modifiers = self._variable_modifiers
        return new

    @property
    def initialize_from(self) -> Optional[CaseOrExperimentOrExternalResult]:
        return self._initialize_from

    def with_initialize_from(
        self, entity: Optional[CaseOrExperimentOrExternalResult] = None
    ) -> SimpleModelicaExperimentDefinition:
        """Sets the experiment or case to initialize from for an experiment.

        Args:
            entity: An instance of Case or Experiment or ExternalResult.

        Example::

            experiment = workspace.get_experiment(experiment_id)
            experiment_definition = model.new_experiment_definition(custom_function)
            experiment_definition.with_initialize_from(experiment)

            experiment = workspace.get_experiment(experiment_id)
            case = experiment.get_case('case_1')
            experiment_definition = model.new_experiment_definition(custom_function)
            experiment_definition.with_initialize_from(case)

            result = workspace.upload_result('C:/A.mat').wait()
            experiment_definition = model.new_experiment_definition(custom_function)
            experiment_definition.with_initialize_from(result)

        """
        _validate_initialize_from(entity)
        new = SimpleModelicaExperimentDefinition(
            model=self._model,
            custom_function=self._custom_function,
            compiler_options=self._compiler_options,
            fmi_target=self._fmi_target,
            fmi_version=self._fmi_version,
            platform=self._platform,
            compiler_log_level=self._compiler_log_level,
            runtime_options=self._runtime_options,
            solver_options=self._solver_options,
            simulation_options=self._simulation_options,
            simulation_log_level=self._simulation_log_level,
            initialize_from=entity,
        )
        new._expansion = self._expansion
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions
        return new

    def with_extensions(
        self, experiment_extensions: List[SimpleExperimentExtension]
    ) -> SimpleModelicaExperimentDefinition:
        """Sets up an experiment with multiple experiment extensions.

        Args:
            experiment_extensions:
                A list of experiment extension objects.
                Extension object must an instance of
                SimpleExperimentExtension class.

        Example::

            model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
            experiment_definition = model.new_experiment_definition(custom_function).
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

        _assert_valid_extensions(experiment_extensions)
        exp_ext = []
        for extension in experiment_extensions:
            exp_ext.append(extension)

        new = SimpleModelicaExperimentDefinition(
            model=self._model,
            custom_function=self._custom_function,
            compiler_options=self._compiler_options,
            fmi_target=self._fmi_target,
            fmi_version=self._fmi_version,
            platform=self._platform,
            compiler_log_level=self._compiler_log_level,
            runtime_options=self._runtime_options,
            solver_options=self._solver_options,
            simulation_options=self._simulation_options,
            simulation_log_level=self._simulation_log_level,
            initialize_from=self._initialize_from,
        )
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions + exp_ext
        new._expansion = self._expansion
        return new

    def with_cases(
        self, cases_modifiers: List[Dict[str, Any]]
    ) -> SimpleModelicaExperimentDefinition:
        """Sets up an experiment with multiple cases with different variable
        modifiers.

        Args:
            cases_modifiers: A list of variable modifier dictionaries.
                Multiple dictionaries with variable modifiers could to added to create
                multiple cases.

        Example::

            model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
            experiment_definition = model.new_experiment_definition(
                custom_function).with_cases([{'PI.k': 20}, {'PI.k': 30}])

        """
        _assert_valid_case_modifiers(cases_modifiers)

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

            model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
            simulation_options = custom_function.get_simulation_options()
                .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_def = model.new_experiment_definition(
                custom_function,
                solver_options=solver_options,
                simulation_options=simulation_options
            )
            simulate_def.to_dict()

        """

        exp_dict: Dict[str, Any] = {
            "experiment": {
                "version": 2,
                "base": {
                    "model": {
                        "modelica": {
                            "className": self._model.name,
                            "compilerOptions": self._compiler_options,
                            "runtimeOptions": self._runtime_options,
                            "compilerLogLevel": self._compiler_log_level,
                            "fmiTarget": self._fmi_target,
                            "fmiVersion": self._fmi_version,
                            "platform": self._platform,
                        }
                    },
                    "modifiers": {"variables": self._variable_modifiers},
                    "analysis": {
                        "type": self._custom_function.name,
                        "parameters": self._custom_function.parameter_values,
                        "simulationOptions": self._simulation_options,
                        "solverOptions": self._solver_options,
                        "simulationLogLevel": self._simulation_log_level,
                    },
                    "expansion": {"algorithm": str(self._expansion)},
                },
                "extensions": [ext.to_dict() for ext in self._extensions],
            }
        }
        expansion_parameters = self._expansion.get_parameters_as_dict()
        if expansion_parameters is not None:
            exp_dict["experiment"]["base"]["expansion"][
                "parameters"
            ] = expansion_parameters
        if isinstance(self.initialize_from, Experiment):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFrom"
            ] = self.initialize_from.id
        elif isinstance(self.initialize_from, Case):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromCase"
            ] = case_to_identifier_dict(self.initialize_from)
        elif isinstance(self.initialize_from, ExternalResult):
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromExternalResult"
            ] = self.initialize_from.id
        return exp_dict
