import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

from modelon.impact.client.experiment_definition.operators import Operator
from modelon.impact.client import exceptions
from modelon.impact.client.experiment_definition.extension import (
    SimpleExperimentExtension,
)
from modelon.impact.client.experiment_definition.expansion import (
    ExpansionAlgorithm,
    FullFactorial,
)
from modelon.impact.client.experiment_definition.util import (
    get_options,
    case_to_identifier_dict,
)
from modelon.impact.client.experiment_definition.asserts import (
    validate_and_set_initialize_from,
    assert_unique_exp_initialization,
    assert_valid_args,
)

logger = logging.getLogger(__name__)


def _assert_successful_compilation(fmu):
    if not fmu.is_successful():
        raise exceptions.OperationFailureError(
            "Compilation process has failed! See the log for more info!"
        )


def _assert_valid_case_modifiers(cases_modifiers):
    if not isinstance(cases_modifiers, list):
        raise TypeError("The case modifiers argument must be a list!")
    for case_modifier in cases_modifiers:
        if not isinstance(case_modifier, dict):
            raise TypeError(
                "The variable modifiers in the case_modifier list must be a "
                "dictionary!"
            )


def _assert_valid_extensions(experiment_extensions):
    if not isinstance(experiment_extensions, list):
        raise TypeError("The experiment extensions argument must be a list!")
    for extension in experiment_extensions:
        if not isinstance(extension, SimpleExperimentExtension):
            raise TypeError(
                "The extension object in the experiment extension list "
                "must be an instance of modelon.impact.client.experiment_definition."
                "extension.SimpleExperimentExtension class!"
            )


class BaseExperimentDefinition(ABC):
    """
    Base class for an Experiment definition class.
    """

    @abstractmethod
    def validate(self):
        """
        Validates the modifiers appended to the experiment definition.
        """

    @abstractmethod
    def to_dict(self):
        """
        Returns the experiment definition as a dictionary.
        """


class SimpleFMUExperimentDefinition(BaseExperimentDefinition):
    """
    A simple experiment definition class for defining experiements.

    Parameters:

        fmu --
            The FMU to be excecuted for this experiment.

        custom_function --
            The custom function to use for this experiment.

        solver_options --
            The solver options to use for this experiment. By default, the options
            is set to None, which means the default options for the
            custom_function input is used.

        simulation_options --
            The simulation_options to use for this experiment. By default, the
            options is set to None, which means the default options for the
            custom_function input is used.

        simulation_log_level --
            Simulation log level for this experiment. Default is 'WARNING'.

    Examples::

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
        fmu,
        custom_function,
        solver_options=None,
        simulation_options=None,
        simulation_log_level="WARNING",
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
        self._variable_modifiers = fmu._variable_modifiers()
        self._extensions = []
        self._initialize_from_experiment = None
        self._initialize_from_case = None
        self._initialize_from_external_result = None

    def validate(self):
        add = set(self._variable_modifiers.keys()) - set(
            self._fmu.get_settable_parameters()
        )
        if add:
            raise KeyError(
                f"Paramter(s) '{', '.join(add)}' {'are' if len(add)>1 else 'is'} "
                "not a valid parameter modifier! Call the get_settable_parameters() "
                "method on the fmu to view the list of settable parameters."
            )

    def with_modifiers(self, modifiers=None, **modifiers_kwargs):
        """Sets the modifiers parameters for an experiment.

        Parameters:

            modifiers --
                A dictionary of variable modifiers.

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
        )
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._initialize_from_external_result = self._initialize_from_external_result
        new._extensions = self._extensions
        for variable, value in modifiers_aggregate.items():
            new._variable_modifiers[variable] = (
                str(value) if isinstance(value, Operator) else value
            )
        return new

    def with_extensions(self, experiment_extensions):
        """Sets up an experiment with multiple experiment extensions.

        Parameters:

            experiment_extensions --
                "A list of experiment extension objects."
                "Extension object must an instance of "
                "modelon.impact.client.experiment_definition."
                "extension.SimpleExperimentExtension class."

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
        )
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions + exp_ext
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._initialize_from_external_result = self._initialize_from_external_result

        return new

    def with_cases(self, cases_modifiers):
        """Sets up an experiment with multiple cases with different
        variable modifiers.

        Parameters:

            cases_modifiers --
                A list of variable modifier dictionaries.
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

    def to_dict(self):
        """Returns the experiment definition as a dictionary.

        Returns:

            definition_dict --
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
        exp_dict = {
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
        if self._initialize_from_experiment:
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFrom"
            ] = self._initialize_from_experiment.id
        elif self._initialize_from_case:
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromCase"
            ] = case_to_identifier_dict(self._initialize_from_case)
        elif self._initialize_from_external_result:
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromExternalResult"
            ] = self._initialize_from_external_result.id
        return exp_dict

    def initialize_from(self, entity):
        """Sets the experiment or case to initialize from for an experiment.

        Parameters:

            entity --
                "An instance of modelon.impact.client.entities.case.Case or "
                "modelon.impact.client.entities.experiment.Experiment."

        Example::

            experiment = workspace.get_experiment(experiment_id)
            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            initialize_from(experiment)

            experiment = workspace.get_experiment(experiment_id)
            case = experiment.get_case('case_1')
            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            initialize_from(case)

            result = workspace.upload_result('C:/A.mat').wait()
            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            initialize_from(result)
        """
        new = SimpleFMUExperimentDefinition(
            self._fmu,
            self._custom_function,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
        )
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._initialize_from_external_result = self._initialize_from_external_result
        validate_and_set_initialize_from(entity, new)
        assert_unique_exp_initialization(
            new._initialize_from_experiment,
            new._initialize_from_case,
            new._initialize_from_external_result,
        )
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions

        return new


class SimpleModelicaExperimentDefinition(BaseExperimentDefinition):
    """
    A simple experiment definition class for defining experiements.

    Parameters:

        model --
            The Model class object.

        custom_function --
            The custom function to use for this experiment.

        compiler_options --
            The compiler options to use for this experiment. By default the options
            is set to None, which means the default options for the
            custom_function input is used.

        fmi_target --
            Compiler target. Possible values are 'me' and 'cs'. Default: 'me'.

        fmi_version --
            The FMI version. Valid options are '1.0' and '2.0'. Default: '2.0'.

        platform --
            Platform for FMU binary.The OS running the Impact server must match the
            environment that runs the compiled FMU. This is necessary as the
            binaries packaged with the FMU are based on the platform generating
            the FMU. For example, if the Impact server is running Linux the binary
            in the downloaded FMU is compiled for Linux. The downloaded FMU can
            then not be simulated on Windows.
            Supported options are:-
                - 'auto': platform is selected automatically.
                - "linux64": generate a 32 bit FMU.
                - "win32": generate a 32 bit FMU.
                - "win64": generate a 64 bit FMU
            Default: 'auto'.

        compiler_log_level --
            The logging for the compiler. Possible values are "error",
            "warning", "info", "verbose" and "debug". Default: 'warning'.

        runtime_options --
            The runtime options to use for this experiment. By default the options
            is set to None, which means the default options for the
            custom_function input is used.

        solver_options --
            The solver options to use for this experiment. By default the options
            is set to None, which means the default options for the
            custom_function input is used.

        simulation_options --
            The simulation options to use for this experiment. By default the
            options is set to None, which means the default options for the
            custom_function input is used.

        simulation_log_level --
            Simulation log level for this experiment. Default: 'WARNING'.

    Examples::

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
        model,
        custom_function,
        *,
        compiler_options=None,
        fmi_target="me",
        fmi_version="2.0",
        platform="auto",
        compiler_log_level="warning",
        runtime_options=None,
        solver_options=None,
        simulation_options=None,
        simulation_log_level="WARNING",
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
        self._variable_modifiers = {}
        self._extensions = []
        self._initialize_from_experiment = None
        self._initialize_from_case = None
        self._initialize_from_external_result = None
        self._expansion = FullFactorial()

    def validate(self):
        raise NotImplementedError(
            "Validation is not supported for SimpleModelicaExperimentDefinition class"
        )

    def with_modifiers(
        self, modifiers: Optional[Dict[str, Any]] = None,
    ) -> 'SimpleModelicaExperimentDefinition':
        """Sets the modifiers parameters for an experiment.

        Parameters:

            modifiers --
                A dictionary of variable modifiers. Could be used if
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
        )
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._initialize_from_external_result = self._initialize_from_external_result
        new._extensions = self._extensions
        new._expansion = self._expansion

        for variable, value in modifiers.items():
            new._variable_modifiers[variable] = (
                str(value) if isinstance(value, Operator) else value
            )
        return new

    def with_expansion(self, expansion: ExpansionAlgorithm = FullFactorial()):
        """Sets the expansion algorithm for an experiment.

        Parameters:

            expansion --
                An expansion algorithm. Avaiable algorithms are LatinHypercube,
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
        )
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._initialize_from_external_result = self._initialize_from_external_result
        new._extensions = self._extensions
        new._expansion = expansion
        new._variable_modifiers = self._variable_modifiers
        return new

    def initialize_from(self, entity):
        """Sets the experiment or case to initialize from for an experiment.

        Parameters:

            entity --
                "An instance of modelon.impact.client.entities.case.Case or "
                "modelon.impact.client.entities.experiment.Experiment."

        Example::

            experiment = workspace.get_experiment(experiment_id)
            experiment_definition = model.new_experiment_definition(custom_function).
            initialize_from(experiment)

            experiment = workspace.get_experiment(experiment_id)
            case = experiment.get_case('case_1')
            experiment_definition = model.new_experiment_definition(custom_function).
            initialize_from(case)

            result = workspace.upload_result('C:/A.mat').wait()
            experiment_definition = model.new_experiment_definition(custom_function).
            initialize_from(result)
        """
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
        )
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._initialize_from_external_result = self._initialize_from_external_result
        new._expansion = self._expansion
        validate_and_set_initialize_from(entity, new)
        assert_unique_exp_initialization(
            new._initialize_from_experiment,
            new._initialize_from_case,
            new._initialize_from_external_result,
        )
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions
        return new

    def with_extensions(self, experiment_extensions):
        """Sets up an experiment with multiple experiment extensions.

        Parameters:

            experiment_extensions --
                "A list of experiment extension objects."
                "Extension object must an instance of "
                "modelon.impact.client.experiment_definition."
                "extension.SimpleExperimentExtension class."

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
        )
        new._variable_modifiers = self._variable_modifiers
        new._extensions = self._extensions + exp_ext
        new._initialize_from_experiment = self._initialize_from_experiment
        new._initialize_from_case = self._initialize_from_case
        new._initialize_from_external_result = self._initialize_from_external_result
        new._expansion = self._expansion
        return new

    def with_cases(self, cases_modifiers):
        """Sets up an experiment with multiple cases with different
        variable modifiers.

        Parameters:

            cases_modifiers --
                A list of variable modifier dictionaries.
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

    def to_dict(self):
        """Returns the experiment definition as a dictionary.

        Returns:

            definition_dict --
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

        exp_dict = {
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
        if self._initialize_from_experiment:
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFrom"
            ] = self._initialize_from_experiment.id
        elif self._initialize_from_case:
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromCase"
            ] = case_to_identifier_dict(self._initialize_from_case)
        elif self._initialize_from_external_result:
            exp_dict["experiment"]["base"]["modifiers"][
                "initializeFromExternalResult"
            ] = self._initialize_from_external_result.id
        return exp_dict
