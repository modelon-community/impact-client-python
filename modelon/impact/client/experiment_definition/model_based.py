from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

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
from modelon.impact.client.experiment_definition.expansion import (
    ExpansionAlgorithm,
    FullFactorial,
)
from modelon.impact.client.experiment_definition.extension import (
    SimpleExperimentExtension,
)
from modelon.impact.client.experiment_definition.interfaces.definition import (
    BaseExperimentDefinition,
)
from modelon.impact.client.experiment_definition.modifiers import (
    Modifier,
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
    from modelon.impact.client.entities.model import Model
    from modelon.impact.client.options import (
        CompilerOptions,
        RuntimeOptions,
        SimulationOptions,
        SolverOptions,
    )

    CaseOrExperimentOrExternalResult = Union[Case, Experiment, ExternalResult]
    RuntimeOptionsOrDict = Union[RuntimeOptions, Dict[str, Any]]
    SimulationOptionsOrDict = Union[SimulationOptions, Dict[str, Any]]
    SolverOptionsOrDict = Union[SolverOptions, Dict[str, Any]]
    CompilerOptionsOrDict = Union[CompilerOptions, Dict[str, Any]]

logger = logging.getLogger(__name__)


class SimpleModelicaExperimentDefinition(BaseExperimentDefinition):
    """A simple experiment definition class for defining experiments.

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
        self._variable_modifiers: Dict[str, Modifier] = {}
        self._extensions: List[SimpleExperimentExtension] = []
        self._expansion: ExpansionAlgorithm = FullFactorial()

    @property
    def modifiers(self) -> Dict[str, Any]:
        """Returns the variable modifiers dict."""
        return self._variable_modifiers

    @property
    def model(self) -> Model:
        """Returns the Model class."""
        return self._model

    @property
    def fmi_target(self) -> str:
        """Returns the FMI target."""
        return self._fmi_target

    @property
    def fmi_version(self) -> str:
        """Returns the FMI version."""
        return self._fmi_version

    @property
    def platform(self) -> str:
        """Returns the platform to compile FMU for."""
        return self._platform

    @property
    def compiler_log_level(self) -> str:
        """Returns the compiler log level."""
        return self._compiler_log_level

    @property
    def compiler_options(self) -> Dict[str, Any]:
        """Returns the compiler options as a dict."""
        return self._compiler_options

    @property
    def runtime_options(self) -> Dict[str, Any]:
        """Returns the runtime options as a dict."""
        return self._runtime_options

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
    def expansion(self) -> ExpansionAlgorithm:
        """Returns the expansion algorithm class."""
        return self._expansion

    @property
    def initialize_from(self) -> Optional[CaseOrExperimentOrExternalResult]:
        """Returns the case, experiment or result the experiment definition was
        initialized from."""
        return self._initialize_from

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
        new._variable_modifiers = self._variable_modifiers

        for name, value in modifiers.items():
            new._variable_modifiers[name] = ensure_as_modifier(value)
        return new

    def with_expansion(
        self, expansion: Optional[ExpansionAlgorithm] = None
    ) -> SimpleModelicaExperimentDefinition:
        """Sets the expansion algorithm for an experiment.

        Args:
            expansion: An expansion algorithm. Available algorithms are LatinHypercube,
                Sobol and FullFactorial.
                Default: FullFactorial.

        Example::

            from modelon.impact.client import Sobol, Beta, Normal

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
        new_expansion = expansion or FullFactorial()
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
        new._expansion = new_expansion
        new._variable_modifiers = self._variable_modifiers
        return new

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

            result = workspace.upload_result('A.mat').wait()
            experiment_definition = model.new_experiment_definition(custom_function)
            experiment_definition.with_initialize_from(result)

        """
        validate_initialize_from(entity)
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

        assert_valid_extensions(experiment_extensions)
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
        """Sets up an experiment with multiple cases with different variable modifiers.

        Args:
            cases_modifiers: A list of variable modifier dictionaries.
                Multiple dictionaries with variable modifiers could to added to create
                multiple cases.

        Example::

            model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
            experiment_definition = model.new_experiment_definition(
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
        custom_function_parameters = custom_function_parameters_to_dict(
            self._custom_function.parameter_values.as_raw_dict()
        )
        variable_modifiers = modifiers_to_dict(self._variable_modifiers)
        exp_dict: Dict[str, Any] = {
            "experiment": {
                "version": 3,
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
                    "modifiers": {"variables": variable_modifiers},
                    "analysis": {
                        "type": self._custom_function.name,
                        "parameters": custom_function_parameters,
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
