import logging
from typing import Any, Dict, Optional, Union
from modelon.impact.client.sal.model_executable import ModelExecutableService
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.operations.model_executable import (
    ModelExecutableOperation,
    CachedModelExecutableOperation,
)

from modelon.impact.client.experiment_definition import base
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.options import ExecutionOptions
from modelon.impact.client import asserts

logger = logging.getLogger(__name__)

Options = Union[ExecutionOptions, Dict[str, Any]]
CompilationOperations = Union[ModelExecutableOperation, CachedModelExecutableOperation]


class Model:
    """
    Class containing Model functionalities.
    """

    def __init__(
        self,
        class_name: str,
        workspace_id: str,
        workspace_service: WorkspaceService,
        model_exe_service: ModelExecutableService,
    ):
        self._class_name = class_name
        self._workspace_id = workspace_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def __repr__(self):
        return f"Class name '{self._class_name}'"

    def __eq__(self, obj):
        return isinstance(obj, Model) and obj._class_name == self._class_name

    @property
    def name(self) -> str:
        """Class name"""
        return self._class_name

    def compile(
        self,
        compiler_options: Options,
        runtime_options: Optional[Options] = None,
        compiler_log_level: str = "warning",
        fmi_target: str = "me",
        fmi_version: str = "2.0",
        platform: str = "auto",
        force_compilation: bool = False,
    ) -> CompilationOperations:
        """Compiles the model to an FMU.
        Returns an modelon.impact.client.operations.ModelExecutableOperation class
        object.

        Parameters:

            compiler_options --
                An compilation options class instance of
                modelon.impact.client.options.ExecutionOptions or
                a dictionary object containing the compiler options.

            runtime_options --
                An runtime options class instance of
                modelon.impact.client.options.ExecutionOptions or
                a dictionary object containing the runtime options. Default: None.

            compiler_log_level --
                The logging for the compiler. Possible values are "error",
                "warning", "info", "verbose" and "debug". Default: 'warning'.

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

            force_compilation --
                Force a model compilation.

        Returns:

            modelexecutableoperation --
                An modelon.impact.client.operations.ModelExecutableOperation class
                object.

        Example::

            compile_ops=model.compile(compiler_options)
            compile_ops.cancel()
            compile_ops.status()
            compiler_options=custom_function.get_compiler_options.with_values(c_compiler='gcc')
            runtime_options={'cs_solver':0}
            model.compile(compiler_options, runtime_options).wait()
            model.compile({'c_compiler':'gcc'}).wait()
        """
        asserts.assert_valid_args(
            compiler_options=compiler_options, runtime_options=runtime_options
        )
        compiler_options = (
            dict(compiler_options)
            if isinstance(compiler_options, ExecutionOptions)
            else compiler_options
            if isinstance(compiler_options, dict)
            else {}
        )
        runtime_options = (
            dict(runtime_options)
            if isinstance(runtime_options, ExecutionOptions)
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
            fmu_id, modifiers = self._model_exe_sal.fmu_setup(
                self._workspace_id, body, True
            )
            if fmu_id:
                return CachedModelExecutableOperation(
                    self._workspace_id,
                    fmu_id,
                    self._workspace_sal,
                    self._model_exe_sal,
                    None,
                    modifiers,
                )

        # No cached FMU, setup up a new one
        fmu_id, _ = self._model_exe_sal.fmu_setup(self._workspace_id, body, False)

        return ModelExecutableOperation(
            self._workspace_id,
            self._model_exe_sal.compile_model(self._workspace_id, fmu_id),
            self._workspace_sal,
            self._model_exe_sal,
        )

    def new_experiment_definition(
        self,
        custom_function: CustomFunction,
        *,
        compiler_options: Optional[Options] = None,
        fmi_target: str = "me",
        fmi_version: str = "2.0",
        platform: str = "auto",
        compiler_log_level: str = "warning",
        runtime_options: Optional[Options] = None,
        solver_options: Optional[Options] = None,
        simulation_options: Optional[Options] = None,
        simulation_log_level: str = "WARNING",
    ):
        """
        Returns a new experiment definition using this Model.

        Parameters:

            custom_function --
                The custom function to use for this experiment.

            compiler_options --
                An compilation options class instance of
                modelon.impact.client.options.ExecutionOptions or
                a dictionary object containing the compiler options.

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
                An runtime options class instance of
                modelon.impact.client.options.ExecutionOptions or
                a dictionary object containing the runtime options. Default: None.

            solver_options --
                The solver options to use for this experiment. By default the options
                is set to None, which means the default options for the
                custom_function input is used.

            simulation_options --
                The simulation_options to use for this experiment. By default the
                options is set to None, which means the default options for the
                custom_function input is used.

            simulation_log_level --
                Simulation log level for this experiment. Default is 'WARNING'.

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
        return base.SimpleModelicaExperimentDefinition(
            model=self,
            custom_function=custom_function,
            compiler_options=compiler_options,
            fmi_target=fmi_target,
            fmi_version=fmi_version,
            platform=platform,
            compiler_log_level=compiler_log_level,
            runtime_options=runtime_options,
            solver_options=solver_options,
            simulation_options=simulation_options,
            simulation_log_level=simulation_log_level,
        )
