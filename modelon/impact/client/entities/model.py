from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from modelon.impact.client.entities.interfaces.model import ModelInterface
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.project import Project
from modelon.impact.client.experiment_definition.model_based import (
    SimpleModelicaExperimentDefinition,
)
from modelon.impact.client.experiment_definition.modifiers import Enumeration
from modelon.impact.client.operations.fmu_import import FMUImportOperation
from modelon.impact.client.operations.model_executable import (
    CachedModelExecutableOperation,
    ModelExecutableOperation,
)
from modelon.impact.client.options import (
    CompilerOptions,
    ProjectExecutionOptions,
    RuntimeOptions,
    SimulationOptions,
    SolverOptions,
)

if TYPE_CHECKING:
    from modelon.impact.client.entities.case import Case
    from modelon.impact.client.entities.custom_function import CustomFunction
    from modelon.impact.client.entities.experiment import Experiment
    from modelon.impact.client.entities.external_result import ExternalResult
    from modelon.impact.client.operations.base import BaseOperation
    from modelon.impact.client.sal.service import Service

    CaseOrExperimentOrExternalResult = Union[Case, Experiment, ExternalResult]

logger = logging.getLogger(__name__)

CompilationOperations = Union[ModelExecutableOperation, CachedModelExecutableOperation]

RuntimeOptionsOrDict = Union[RuntimeOptions, Dict[str, Any]]
CompilerOptionsOrDict = Union[CompilerOptions, Dict[str, Any]]
SimulationOptionsOrDict = Union[SimulationOptions, Dict[str, Any]]
SolverOptionsOrDict = Union[SolverOptions, Dict[str, Any]]


def to_domain_parameter_value(
    param_data: Dict[str, Any]
) -> Union[str, int, float, bool, Enumeration]:
    return (
        Enumeration(param_data["value"])
        if param_data.get("dataType", "") == "ENUMERATION"
        else param_data["value"]
    )


def _assert_valid_compilation_options(
    compiler_options: Optional[CompilerOptionsOrDict] = None,
    runtime_options: Optional[RuntimeOptionsOrDict] = None,
) -> None:
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


class Model(ModelInterface):
    """Class containing Model functionalities."""

    def __init__(
        self, class_name: str, workspace_id: str, project_id: str, service: Service
    ):
        self._class_name = class_name
        self._workspace_id = workspace_id
        self._project_id = project_id
        self._sal = service

    def __repr__(self) -> str:
        return f"Class name '{self._class_name}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Model) and obj._class_name == self._class_name

    @property
    def name(self) -> str:
        """Class name."""
        return self._class_name

    def compile(
        self,
        compiler_options: CompilerOptionsOrDict,
        runtime_options: Optional[RuntimeOptionsOrDict] = None,
        compiler_log_level: str = "warning",
        fmi_target: str = "me",
        fmi_version: str = "2.0",
        platform: str = "auto",
        force_compilation: bool = False,
    ) -> CompilationOperations:
        """Compiles the model to an FMU. Returns an ModelExecutableOperation class
        object.

        Args:
            compiler_options: An compilation options class instance of
                CompilerOptions or a dictionary object containing the
                compiler options.
            runtime_options: An runtime options class instance of
                RuntimeOptions or a dictionary object containing the
                runtime options. Default: None.
            compiler_log_level: The logging for the compiler. Possible values are
                "error", "warning", "info", "verbose" and "debug". Default: 'warning'.
            fmi_target: Compiler target. Possible values are 'me' and 'cs'.
                Default: 'me'.
            fmi_version: The FMI version. Valid options are '1.0' and '2.0'.
                Default: '2.0'.
            platform: Platform for FMU binary.The OS running the Impact server must
                match the environment that runs the compiled FMU. This is necessary as
                the binaries packaged with the FMU are based on the platform generating
                the FMU. For example, if the Impact server is running Linux the binary
                in the downloaded FMU is compiled for Linux. The downloaded FMU can
                then not be simulated on Windows. Default: 'auto'. Supported
                options are:-

                - 'auto': platform is selected automatically
                - "linux64": generate a 32 bit FMU
                - "win64": generate a 64 bit FMU

            force_compilation: Force a model compilation.

        Returns:
            An ModelExecutableOperation class object.

        Example::

            compile_ops=model.compile(compiler_options)
            compile_ops.cancel()
            compile_ops.status
            compiler_options=custom_function.get_compiler_options().with_values(c_compiler='gcc')
            runtime_options={'cs_solver':0}
            model.compile(compiler_options, runtime_options).wait()
            model.compile({'c_compiler':'gcc'}).wait()

        """
        _assert_valid_compilation_options(
            compiler_options=compiler_options, runtime_options=runtime_options
        )
        compiler_options = (
            dict(compiler_options)
            if isinstance(compiler_options, CompilerOptions)
            else compiler_options
            if isinstance(compiler_options, dict)
            else {}
        )
        runtime_options = (
            dict(runtime_options)
            if isinstance(runtime_options, RuntimeOptions)
            else runtime_options
            if isinstance(runtime_options, dict)
            else {}
        )

        body = {
            "input": {
                "class_name": self._class_name,
                "compiler_options": compiler_options,
                "runtime_options": runtime_options,
                "compiler_log_level": compiler_log_level,
                "fmi_target": fmi_target,
                "fmi_version": fmi_version,
                "platform": platform,
            }
        }
        if not force_compilation:
            fmu_id, modifiers = self._sal.model_executable.fmu_setup(
                self._workspace_id, body, True
            )
            modifiers_dict = {
                modifier["name"]: to_domain_parameter_value(modifier["value"])
                for modifier in modifiers
            }
            if fmu_id:
                return CachedModelExecutableOperation[ModelExecutable](
                    self._workspace_id,
                    fmu_id,
                    self._sal,
                    ModelExecutable.from_operation,
                    None,
                    modifiers_dict,
                )

        # No cached FMU, setup up a new one
        fmu_id, _ = self._sal.model_executable.fmu_setup(
            self._workspace_id, body, False
        )

        return ModelExecutableOperation[ModelExecutable](
            self._workspace_id,
            self._sal.model_executable.compile_model(self._workspace_id, fmu_id),
            self._sal,
            ModelExecutable.from_operation,
        )

    def new_experiment_definition(
        self,
        custom_function: CustomFunction,
        *,
        fmi_target: str = "me",
        fmi_version: str = "2.0",
        platform: str = "auto",
        compiler_log_level: str = "warning",
        compiler_options: Optional[CompilerOptionsOrDict] = None,
        runtime_options: Optional[RuntimeOptionsOrDict] = None,
        solver_options: Optional[SolverOptionsOrDict] = None,
        simulation_options: Optional[SimulationOptionsOrDict] = None,
        simulation_log_level: str = "WARNING",
        initialize_from: Optional[CaseOrExperimentOrExternalResult] = None,
    ) -> SimpleModelicaExperimentDefinition:
        """Returns a new experiment definition using this Model.

        Args:
            custom_function: The custom function to use for this experiment.
            fmi_target: Compiler target. Possible values are 'me' and 'cs'.
            Default: 'me'.
            fmi_version: The FMI version. Valid options are '1.0' and '2.0'.
            Default: '2.0'.
            platform: Platform for FMU binary.The OS running the Impact server must
                match the environment that runs the compiled FMU. This is necessary as
                the binaries packaged with the FMU are based on the platform generating
                the FMU. For example, if the Impact server is running Linux the binary
                in the downloaded FMU is compiled for Linux. The downloaded FMU can
                then not be simulated on Windows. Default: 'auto'. Supported
                options are:-

                - 'auto': platform is selected automatically
                - "linux64": generate a 32 bit FMU
                - "win64": generate a 64 bit FMU
            compiler_log_level: The logging for the compiler. Possible values are
                "error", "warning", "info", "verbose" and "debug". Default: 'warning'.
            compiler_options: An compilation options class instance of
                CompilerOptions or a dictionary object containing the compiler options.
            runtime_options: An runtime options class instance of RuntimeOptions or
                a dictionary object containing the runtime options. Default: None.
            solver_options: The solver options to use for this experiment.
                By default the options is set to None, which means the default options
                for the custom_function input is used.
            simulation_options:
                The simulation_options to use for this experiment. By default the
                options is set to None, which means the default options for the
                custom_function input is used.
            simulation_log_level:
                Simulation log level for this experiment. Default is 'WARNING'.
            initialize_from: Optional entity to initialize from. An instance of
                Case or Experiment or ExternalResult. Default: None

        Example::

            model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
            dynamic = workspace.get_custom_function('dynamic')
            solver_options = {'atol':1e-8}
            simulation_options = dynamic.get_simulation_options().
            with_values(ncp=500)
            experiment_definition = model.new_experiment_definition(
                dynamic,
                solver_options=solver_options,
                simulation_options=simulation_options
            )
            experiment = workspace.execute(experiment_definition).wait()

        """
        options = self._sal.project.project_options_get(
            self._project_id, self._workspace_id, custom_function=custom_function.name
        )
        project_options = ProjectExecutionOptions(options, custom_function.name)
        return SimpleModelicaExperimentDefinition(
            model=self,
            custom_function=custom_function,
            compiler_options=compiler_options or project_options.compiler_options,
            fmi_target=fmi_target,
            fmi_version=fmi_version,
            platform=platform,
            compiler_log_level=compiler_log_level,
            runtime_options=runtime_options or project_options.runtime_options,
            solver_options=solver_options or project_options.solver_options,
            simulation_options=simulation_options or project_options.simulation_options,
            simulation_log_level=simulation_log_level,
            initialize_from=initialize_from,
        )

    def import_fmu(
        self,
        fmu_path: str,
        class_name: Optional[str] = None,
        overwrite: bool = False,
        include_patterns: Optional[Union[str, List[str]]] = None,
        exclude_patterns: Optional[Union[str, List[str]]] = None,
        top_level_inputs: Optional[Union[str, List[str]]] = None,
        step_size: float = 0.0,
    ) -> FMUImportOperation:
        """Uploads a FMU.

        Args:
            fmu_path:
                The path for the FMU to be imported.
            class_name:
                Qualified name of generated class. By default, 'class_name' is
                set to the name of the library followed by a name based
                on the filename of the imported FMU.
            overwrite:
                Determines if any already existing files should be overwritten.
                Default: False.
            include_patterns, exclude_patterns:
                Specifies what variables from the FMU to include and/or exclude in the
                wrapper model. These two arguments are patterns or lists of patterns as
                the same kind as the argument 'filter' for the function
                'get_model_variables' in PyFMI. If both 'include_patterns' and
                'exclude_patterns' are given, then all variables that matches
                'include_patterns' but does not match 'exclude_patterns' are included.
                Derivatives and variables with a leading underscore in the name are
                always excluded.
                Default value: None (which means to include all the variables).
            top_level_inputs:
                Specify what inputs that should be kept as inputs, i.e. with or without
                the input keyword. The argument is a pattern similar to the arguments
                include_patterns and exclude_patterns. Example: If
                top_level_inputs = 'my_inputs*', then all input variables matching the
                pattern 'my_inputs*' will be generated as inputs, and all other inputs
                not matching the pattern as model variables. If top_level_inputs = '',
                then no input is imported as an input.
                Default value: None (which means all inputs are kept as inputs)
                Type: str or a list of strings
            step_size:
                Specify what value to set for the parameter for step size in the
                generated model. By default the parameter is set to zero, which
                means that the step size will be set during simulation based
                on simulation properties such as the time interval.
                This can also be manually set to any real non-negative number.
                The value of the step size parameter can also be set via the function
                set_step_size, which must be invoked before importing the model.
                Default value: 0.0 (which during simulation is set according to the
                description above).

        Example::

            workspace = client.get_workspace("test")
            package = workspace.get_model('MyPackage')
            fmu_content = package.import_fmu('C:/A.fmu').wait()
            fmu_content = package.import_fmu('C:/B.fmu',
                class_name="MyPackage.Model").wait()

        """
        resp = self._sal.project.project_get(
            self._project_id, vcs_info=False, size_info=False
        )
        project = Project(
            resp["id"],
            resp["projectType"],
            resp["storageLocation"],
            None,
            self._sal,
        )
        modelica_content = project.get_modelica_library_by_name(self._class_name)
        if not modelica_content:
            raise ValueError(
                f"No modelica package with name {self._class_name} exists "
                f"in the Project - '{project.name}'"
            )
        class_name = class_name or ".".join(
            [
                self._class_name,
                os.path.split(fmu_path)[-1].strip(".fmu"),
            ]
        )
        resp = self._sal.project.fmu_import(
            self._project_id,
            modelica_content.id,
            fmu_path,
            class_name,
            overwrite,
            include_patterns,
            exclude_patterns,
            top_level_inputs,
            step_size=step_size,
        )

        return FMUImportOperation[Model](
            resp["data"]["location"],
            self._workspace_id,
            self._project_id,
            self._sal,
            Model.from_operation,
        )

    @classmethod
    def from_operation(cls, operation: BaseOperation[Model], **kwargs: Any) -> Model:
        assert isinstance(operation, FMUImportOperation)
        return cls(**kwargs, service=operation._sal)
