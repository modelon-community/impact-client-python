import os
import tempfile
import logging
from modelon.impact.client import operations

from modelon.impact.client.experiment_definition import (
    SimpleModelicaExperimentDefinition,
    SimpleFMUExperimentDefinition,
    assert_valid_args,
)
from collections.abc import Mapping
from modelon.impact.client.options import ExecutionOptions
from modelon.impact.client import exceptions
from enum import Enum

logger = logging.getLogger(__name__)


def _assert_successful_operation(is_successful, operation_name="Operation"):
    if not is_successful:
        raise exceptions.OperationFailureError(
            f"{operation_name} failed! See the log for more info!"
        )


def _assert_is_complete(status, operation_name="Operation"):
    if status not in (
        ModelExecutableStatus.SUCCESSFUL,
        ExperimentStatus.DONE,
        CaseStatus.SUCCESSFUL,
    ):
        if status in (ModelExecutableStatus.NOTSTARTED, ExperimentStatus.NOTSTARTED):
            raise exceptions.OperationNotCompleteError(
                f"{operation_name} is still in progress! Status : {status}."
                f" Please call the wait() method on the {operation_name} operation"
                " to wait until completion!"
            )
        elif status in (
            ModelExecutableStatus.CANCELLED,
            ExperimentStatus.CANCELLED,
            CaseStatus.CANCELLED,
        ):
            raise exceptions.OperationFailureError(
                f"{operation_name} was cancelled before completion! "
                f"Log file generated for cancelled {operation_name} is empty!"
            )


def _assert_variable_in_result(variables, result_variables):
    add = set(variables) - set(result_variables)
    if add:
        raise ValueError(
            f"Variable(s) '{', '.join(add)}' {'are' if len(add)>1 else 'is'} not"
            " present in the result"
        )


def _create_result_dict(variables, workspace_id, exp_id, case_id, exp_sal):
    response = exp_sal.trajectories_get(workspace_id, exp_id, variables)
    case_index = int(case_id.split("_")[1])
    data = {
        variable: response[i][case_index - 1] for i, variable in enumerate(variables)
    }
    return data


class ModelExecutableStatus(Enum):
    """
    Class representing an enumeration for the possible
    model-executable run info states.
    """

    NOTSTARTED = "not_started"
    CANCELLED = "cancelled"
    SUCCESSFUL = "successful"
    FAILED = "failed"


class ExperimentStatus(Enum):
    """
    Class representing an enumeration for the possible
    experiment run info states.
    """

    NOTSTARTED = "not_started"
    CANCELLED = "cancelled"
    DONE = "done"


class CaseStatus(Enum):
    """
    Class representing an enumeration for the possible
    Case run info states.
    """

    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workspace:
    """
    Class containing Workspace functionalities.
    """

    def __init__(
        self,
        workspace_id,
        workspace_service=None,
        model_exeutable=None,
        experiment_service=None,
        custom_function_service=None,
    ):
        self._workspace_id = workspace_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exeutable
        self._exp_sal = experiment_service
        self._custom_func_sal = custom_function_service

    def __repr__(self):
        return f"Workspace with id '{self._workspace_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Workspace) and obj._workspace_id == self._workspace_id

    @property
    def id(self):
        """Workspace id"""
        return self._workspace_id

    def get_custom_function(self, name):
        """
        Returns a CustomFunction class object.

        Parameters:

            name --
                The name of the custom function.

        Returns:

            custom_function --
                The CustomFunction class object.

        Example::

            workspace.get_custom_function('dynamic')
        """
        custom_function = self._custom_func_sal.custom_function_get(
            self._workspace_id, name
        )
        return CustomFunction(
            self._workspace_id,
            custom_function["name"],
            custom_function["parameters"],
            self._custom_func_sal,
        )

    def get_custom_functions(self):
        """
        Returns a list of CustomFunctions class objects.

        Returns:

            custom_functions --
                A list of CustomFunction class objects.

        Example::

            workspace.get_custom_functions()
        """
        custom_functions = self._custom_func_sal.custom_functions_get(
            self._workspace_id
        )
        return [
            CustomFunction(
                self._workspace_id,
                custom_function["name"],
                custom_function["parameters"],
                self._custom_func_sal,
            )
            for custom_function in custom_functions["data"]["items"]
        ]

    def delete(self):
        """Deletes a workspace.

        Example::

            workspace.delete()
        """
        self._workspace_sal.workspace_delete(self._workspace_id)

    def upload_model_library(self, path_to_lib):
        """Uploads a modelica library or a modelica model to the workspace.

        Parameters:

            path_to_lib --
                The path for the library to be imported.

        Example::

            workspace.upload_model_library('C:/A.mo')
            workspace.upload_model_library('C:/B.mol')
        """
        self._workspace_sal.library_import(self._workspace_id, path_to_lib)

    def lock(self):
        """Locks the workspace to the user.

        Example::

            workspace.lock()
        """
        self._workspace_sal.workspace_lock(self._workspace_id)

    def unlock(self):
        """Unlocks the workspace for other users.

        Example::

            workspace.unlock()
        """
        self._workspace_sal.workspace_unlock(self._workspace_id)

    def download(self, options, path):
        """Downloads the workspace as a binary compressed archive.
        Returns the local path to the downloaded workspace archive.

        Parameters:

            options --
                The definition of what workspace resources to include when
                exporting the workspace.

            path --
                The local path to store the downloaded workspace.

        Returns:

            path --
                Local path to the downloaded workspace archive.

        Example::

            options = {
                "contents": {
                    "libraries": [
                        {"name": "LiquidCooling", "resources_to_exclude": []},
                        {
                            "name": "Workspace",
                            "resources_to_exclude": ["my_plot.png", "my_sheet.csv"],
                        },
                    ],
                    "experiment_ids": [
                        "_nics_multibody_examples_elementary_doublependulum_20191029_084342_2c956e9",
                        "modelica_blocks_examples_pid_controller_20191023_151659_f32a30d",
                    ],
                    "fmu_ids": [
                        "_nics_multibody_examples_elementary_doublependulum_20191029_084342_2c956e9",
                        "modelica_blocks_examples_pid_controller_20191023_151659_f32a30d",
                    ],
                }
            }
            workspace.download(options, path)
        """
        data = self._workspace_sal.workspace_download(self._workspace_id, options)
        ws_path = os.path.join(path, self._workspace_id + ".zip")

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(ws_path, "wb") as f:
            f.write(data)
        return ws_path

    def clone(self):
        """Clones the workspace.
        Returns a clone Workspace class object.

        Returns:

            workspace_clone --
                Clones workspace class object.

        Example::

            workspace.clone()
        """
        resp = self._workspace_sal.workspace_clone(self._workspace_id)
        return Workspace(
            resp["workspace_id"],
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
        )

    def get_model(self, class_name):
        """
        Returns a Model class object.

        Parameters:

            class_name --
                The modelica class path of the model.

        Returns:

            model --
                Model class object.

        Example::

            workspace.get_model(class_name)
        """
        return Model(
            class_name, self._workspace_id, self._workspace_sal, self._model_exe_sal
        )

    def get_fmus(self):
        """
        Returns a list of ModelExecutable class objects.

        Returns:

            FMUs --
                List of ModelExecutable class objects.

        Example::

            workspace.get_fmus()
        """
        resp = self._workspace_sal.fmus_get(self._workspace_id)
        return [
            ModelExecutable(
                self._workspace_id,
                item["id"],
                self._workspace_sal,
                self._model_exe_sal,
                item,
            )
            for item in resp["data"]["items"]
        ]

    def get_fmu(self, fmu_id):
        """
        Returns a ModelExecutable class object.

        Returns:

            FMU --
                ModelExecutable class object.

        Example::

            workspace.get_fmu(fmu_id)
        """
        resp = self._workspace_sal.fmu_get(self._workspace_id, fmu_id)
        return ModelExecutable(
            self._workspace_id,
            resp["id"],
            self._workspace_sal,
            self._model_exe_sal,
            resp,
        )

    def get_experiments(self):
        """
        Returns a list of Experiment class objects.

        Returns:

            experiment --
                List of Experiment class objects.

        Example::

            workspace.get_experiments()
        """
        resp = self._workspace_sal.experiments_get(self._workspace_id)
        return [
            Experiment(
                self._workspace_id, item["id"], self._workspace_sal, self._exp_sal, item
            )
            for item in resp["data"]["items"]
        ]

    def get_experiment(self, experiment_id):
        """
        Returns an Experiment class object.

        Parameters:

            class_name --
                The modelica class path of the model.

        Returns:

            experiment --
                Experiment class object.

        Example::

            workspace.get_experiment(experiment_id)
        """
        resp = self._workspace_sal.experiment_get(self._workspace_id, experiment_id)
        return Experiment(
            self._workspace_id, resp["id"], self._workspace_sal, self._exp_sal, resp
        )

    def create_experiment(self, definition):
        """Creates an experiment.
        Returns an Experiment class object.

        Parameters:

            definition --
                An parametrized experiment definition class of type
                modelon.impact.client.experiment_definition.SimpleModelicaExperimentDefinition
                or
                modelon.impact.client.experiment_definition.SimpleFMUExperimentDefinition.

        Returns:

            experiment --
                Experiment class object.

        Example::

            workspace.create_experiment(definition)
        """
        if isinstance(definition, SimpleFMUExperimentDefinition):
            definition = definition.to_dict()
        elif isinstance(definition, SimpleModelicaExperimentDefinition):
            definition = definition.to_dict()
        elif not isinstance(definition, dict):
            raise TypeError(
                "Definition object must either be a dictionary or an instance of either"
                "modelon.impact.client.experiment_definition."
                "SimpleModelicaExperimentDefinition class or modelon.impact.client."
                "experiment_definition.SimpleFMUExperimentDefinition.!"
            )

        resp = self._workspace_sal.experiment_create(self._workspace_id, definition)
        return Experiment(
            self._workspace_id,
            resp["experiment_id"],
            self._workspace_sal,
            self._exp_sal,
        )

    def execute(self, definition):
        """Exceutes an experiment.
        Returns an modelon.impact.client.operations.ExperimentOperation class object.

        Parameters:

            definition --
                An experiment definition class instance of
                modelon.impact.client.experiment_definition.SimpleFMUExperimentDefinition
                or
                modelon.impact.client.experiment_definition.SimpleModelicaExperimentDefinition
                or
                a dictionary object containing the definition.

        Returns:

            experiment_ops --
                An modelon.impact.client.operations.ExperimentOperation class object.

        Example::

            experiment_ops = workspace.execute(definition)
            experiment_ops.cancel()
            experiment_ops.status()
            experiment_ops.wait()
        """
        exp_id = self.create_experiment(definition).id
        return operations.ExperimentOperation(
            self._workspace_id,
            self._exp_sal.experiment_execute(self._workspace_id, exp_id),
            self._workspace_sal,
            self._exp_sal,
        )


class _Parameter:
    _JSON_2_PY_TYPE = {
        "Number": (float, int,),
        "String": (str,),
        "Boolean": (bool,),
        "Enumeration": (str,),
    }

    def __init__(self, name, value, value_type, valid_values):
        self.name = name
        self._value = value
        self._value_type = value_type
        self._valid_values = valid_values

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, self._JSON_2_PY_TYPE[self._value_type]):
            raise ValueError(
                f"Cannot set {self.name} to {value}, its type is {self._value_type}"
            )

        if self._value_type == "Enumeration" and value not in self._valid_values:
            raise ValueError(
                f"Cannot set enumeration '{self.name}' to '{value}', "
                f"must be one of {self._valid_values}"
            )

        self._value = value


class CustomFunction:
    """
    Class containing CustomFunction functionalities.
    """

    def __init__(self, workspace_id, name, parameter_data, custom_function_service):
        self.name = name
        self._workspace_id = workspace_id
        self._parameter_data = parameter_data
        self._param_by_name = {
            p["name"]: _Parameter(
                p["name"], p["defaultValue"], p["type"], p.get("values", []),
            )
            for p in parameter_data
        }
        self._custom_func_sal = custom_function_service

    def __repr__(self):
        return f"Custom function '{self.name}'"

    def __eq__(self, obj):
        return isinstance(obj, CustomFunction) and obj.name == self.name

    def with_parameters(self, **modified):
        """Sets/updates the custom_function parameters for an experiment.

        Parameters:

            parameters --
                A keyworded, variable-length argument list of custom_function
                parameters.

        Example::

            custom_function.with_parameters(start_time=0.0, final_time=2.0)
        """
        new = CustomFunction(
            self._workspace_id, self.name, self._parameter_data, self._custom_func_sal
        )
        for name, value in modified.items():
            if name not in new._param_by_name:
                raise ValueError(
                    f"The custom function '{self.name}' "
                    f"does not have a parameter '{name}'"
                )

            parameter = new._param_by_name[name]
            parameter.value = value

        return new

    @property
    def parameter_values(self):
        """Custom_function parameters and value as a dictionary"""
        return {p.name: p.value for p in self._param_by_name.values()}

    def get_compiler_options(self):
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            compiler_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_compiler_options()
            opts_2 = opts.with_values(c_compiler='gcc')
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self.name
        )
        return ExecutionOptions(options["compiler"], self.name, self._custom_func_sal)

    def get_runtime_options(self):
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            runtime_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_runtime_options()
            opts_2 = opts.with_values(cs_solver=0)
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self.name
        )
        return ExecutionOptions(options["runtime"], self.name, self._custom_func_sal)

    def get_solver_options(self):
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            solver_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_solver_options()
            opts_2 = opts.with_values(rtol=1e-7)
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self.name
        )
        return ExecutionOptions(options["solver"], self.name, self._custom_func_sal)

    def get_simulation_options(self):
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            simulation_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_simulation_options()
            opts_2 = opts.with_values(ncp=500)
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self.name
        )
        return ExecutionOptions(options["simulation"], self.name, self._custom_func_sal)


class Model:
    """
    Class containing Model functionalities.
    """

    def __init__(
        self, class_name, workspace_id, workspace_service=None, model_exe_service=None
    ):
        self._class_name = class_name
        self._workspace_id = workspace_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def __repr__(self):
        return f"Class name '{self.class_name}'"

    def __eq__(self, obj):
        return isinstance(obj, Model) and obj._class_name == self._class_name

    @property
    def name(self):
        """Class name"""
        return self._class_name

    def compile(
        self,
        compiler_options,
        runtime_options=None,
        compiler_log_level="warning",
        fmi_target="me",
        fmi_version="2.0",
        platform="auto",
        force_compilation=False,
    ):
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
                Platform for FMU binary. Supported values are "auto", "win64", "win32"
                or "linux64". Default: 'auto'.

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
        assert_valid_args(
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
                return operations.CachedModelExecutableOperation(
                    self._workspace_id,
                    fmu_id,
                    self._workspace_sal,
                    self._model_exe_sal,
                    None,
                    modifiers,
                )

        # No cached FMU, setup up a new one
        fmu_id, _ = self._model_exe_sal.fmu_setup(self._workspace_id, body, False)

        return operations.ModelExecutableOperation(
            self._workspace_id,
            self._model_exe_sal.compile_model(self._workspace_id, fmu_id),
            self._workspace_sal,
            self._model_exe_sal,
        )

    def new_experiment_definition(
        self,
        custom_function,
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
                Platform for FMU binary. Supported values are "auto", "win64", "win32"
                or "linux64". Default: 'auto'.

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
                dynamic, solver_options=solver_options,
                simulation_options=simulation_options)
            experiment = workspace.execute(experiment_definition).wait()
        """
        return SimpleModelicaExperimentDefinition(
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


class ModelExecutable:
    """
    Class containing ModelExecutable functionalities.
    """

    def __init__(
        self,
        workspace_id,
        fmu_id,
        workspace_service=None,
        model_exe_service=None,
        info=None,
        modifiers=None,
    ):
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service
        self._info = info
        self._modifiers = modifiers

    def __repr__(self):
        return f"FMU with id '{self._fmu_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ModelExecutable) and obj._fmu_id == self._fmu_id

    @property
    def id(self):
        """FMU id"""
        return self._fmu_id

    @property
    def modifiers(self):
        """FMU modifiers"""
        return {} if self._modifiers is None else self._modifiers

    @property
    def info(self):
        """Compilation information as a dictionary"""
        if self._info is None:
            self._info = self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)
        return self._info

    @property
    def metadata(self):
        """FMU metadata"""
        _assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.ss_fmu_metadata_get(self._workspace_id, self._fmu_id)

    def is_successful(self):
        """
        Returns True if the model has compiled successfully.

        Returns:

            True -> If model has compiled successfully.
            False -> If compilation process has failed.

        Raises:

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process was cancelled.

        Example::

            fmu.is_successful()
        """
        _assert_is_complete(
            ModelExecutableStatus(self.info["run_info"]["status"]), "Compilation"
        )
        return (
            ModelExecutableStatus(self.info["run_info"]["status"])
            == ModelExecutableStatus.SUCCESSFUL
        )

    def get_log(self):
        """
        Returns the compilation log object.

        Returns:

            log --
                The compilation log object.

        Raises:

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process was cancelled.

        Example::

            log = fmu.get_log()
            log.show()
        """
        _assert_is_complete(
            ModelExecutableStatus(self.info["run_info"]["status"]), "Compilation"
        )
        return Log(self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id))

    def get_settable_parameters(self):
        """
        Returns a list of settable parameters for the FMU.

        Returns:

            settable_parameters --
                A list of parameters than can be set on the FMU.

        Raises:

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.

        Example::

            fmu.get_settable_parameters()
        """
        _assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )

    def new_experiment_definition(
        self,
        custom_function,
        solver_options=None,
        simulation_options=None,
        simulation_log_level="WARNING",
    ):
        """
        Returns a new experiment definition using this FMU.

        Parameters:

            custom_function --
                The custom function to use for this experiment.
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

            fmu = model.compile().wait()
            dynamic = workspace.get_custom_function('dynamic')
            solver_options = {'atol':1e-8}
            simulation_options = dynamic.get_simulation_options().
            with_values(ncp=500)
            experiment_definition = fmu.new_experiment_definition(
                dynamic, solver_options, simulation_options)
            experiment = workspace.execute(experiment_definition).wait()
        """
        return SimpleFMUExperimentDefinition(
            self,
            custom_function,
            solver_options,
            simulation_options,
            simulation_log_level,
        )

    def download(self, path=None):
        """Downloads an FMU binary that is compiled.
        Returns the local path to the downloaded FMU archive.

        Parameters:

            path --
                The local path to store the downloaded FMU. Default: None.
                If no path is given, FMU will be downloaded in a temporary directory.

        Returns:

            path --
                Local path to the downloaded FMU.

        Example::

            fmu_path = model.compile().wait().download()
            fmu_path = model.compile().wait().download('C:/Downloads')
        """
        data = self._workspace_sal.fmu_download(self._workspace_id, self._fmu_id)
        if path is None:
            path = os.path.join(tempfile.gettempdir(), "impact-downloads")
        os.makedirs(path, exist_ok=True)
        fmu_path = os.path.join(path, self._fmu_id + ".fmu")
        with open(fmu_path, "wb") as f:
            f.write(data)
        return fmu_path


class Experiment:
    """
    Class containing Experiment functionalities.
    """

    def __init__(
        self, workspace_id, exp_id, workspace_service=None, exp_service=None, info=None
    ):
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service
        self._info = info

    def __repr__(self):
        return f"Experiment with id '{self._exp_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Experiment) and obj._exp_id == self._exp_id

    @property
    def id(self):
        """Experiment id"""
        return self._exp_id

    @property
    def info(self):
        """Experiment information as a dictionary"""
        if self._info is None:
            self._info = self._workspace_sal.experiment_get(
                self._workspace_id, self._exp_id
            )
        return self._info

    def is_successful(self):
        """
        Returns True if the FMU has executed successfully.

        Returns:

            True -> If execution process has completed successfully.
            False -> If execution process has failed.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process was cancelled.

        Example::

            experiment.is_successful()
        """
        _assert_is_complete(
            ExperimentStatus(self.info["run_info"]["status"]), "Simulation"
        )
        expected = {"status": "done", "failed": 0, "cancelled": 0}
        return expected.items() <= self.info["run_info"].items()

    def get_variables(self):
        """
        Returns a list of variables available in the result.

        Returns:

            variables --
                An list of result variables.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            experiment.get_variables()
        """
        _assert_is_complete(
            ExperimentStatus(self.info["run_info"]["status"]), "Simulation"
        )
        return self._exp_sal.result_variables_get(self._workspace_id, self._exp_id)

    def get_cases(self):
        """
        Returns a list of case objects for an experiment.

        Returns:

            cases --
                An list of case objects.

        Example::

            experiment.get_cases()
        """
        resp = self._exp_sal.cases_get(self._workspace_id, self._exp_id)
        return [
            Case(
                case["id"],
                self._workspace_id,
                self._exp_id,
                self._exp_sal,
                self._workspace_sal,
                case,
            )
            for case in resp["data"]["items"]
        ]

    def get_case(self, case_id):
        """
        Returns a case object for a given case_id.

        Parameters:

            case_id --
                The case_id for the case.

        Returns:

            cases --
                An case object.

        Example::

            experiment.get_case('case_1')
        """
        resp = self._exp_sal.case_get(self._workspace_id, self._exp_id, case_id)
        return Case(
            resp["id"],
            self._workspace_id,
            self._exp_id,
            self._exp_sal,
            self._workspace_sal,
            resp,
        )

    def get_trajectories(self, variables):
        """
        Returns a dictionary containing the result trajectories
        for a list of result variables for all the cases.

        Parameters:

            variables --
                A list of result variables to fecth trajectories for.

        Returns:

            trajectory --
                A dictionary object containing the result trajectories for all cases.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process was cancelled.
            TypeError if the variable is not a list object.
            ValueError if trajectory variable is not present in the result.

        Example::

            result = experiment.get_trajectories(['h', 'time'])
            height = result['case_1']['h']
            time = result['case_1']['time']
        """
        if not isinstance(variables, list):
            raise TypeError(
                "Please specify the list of result keys for the trajectories of "
                "intrest!"
            )
        _assert_is_complete(
            ExperimentStatus(self.info["run_info"]["status"]), "Simulation"
        )
        _assert_variable_in_result(variables, self.get_variables())

        response = self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, variables
        )

        if response:
            case_nbrs = range(len(response[0]))
        else:
            case_nbrs = range(len(self.get_cases()))

        return {
            f"case_{j + 1}": {
                variable: response[i][j] for i, variable in enumerate(variables)
            }
            for j in case_nbrs
        }


class Case:
    """
    Class containing Case functionalities.
    """

    def __init__(
        self,
        case_id,
        workspace_id,
        exp_id,
        exp_service=None,
        workspace_service=None,
        info=None,
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._exp_sal = exp_service
        self._workspace_sal = workspace_service
        self._info = info

    def __repr__(self):
        return f"Case with id '{self._case_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Case) and obj._case_id == self._case_id

    @property
    def id(self):
        """Case id"""
        return self._case_id

    @property
    def info(self):
        """Case meta-data"""
        if self._info is None:
            self._info = self._exp_sal.case_get(
                self._workspace_id, self._exp_id, self._case_id
            )
        return self._info

    def is_successful(self):
        """
        Returns True if a case has completed successfully.

        Returns:

            True -> If the case has executed successfully.
            False -> If the case has failed execution.

        Example::

            case.is_successful()
        """
        return CaseStatus(self.info["run_info"]["status"]) == CaseStatus.SUCCESSFUL

    def get_log(self):
        """
        Returns the log class object for a finished case.

        Returns:

            log --
                The case execution log class object.

        Example::

            log = case.get_log()
            log.show()
        """
        return Log(
            self._exp_sal.case_get_log(self._workspace_id, self._exp_id, self._case_id)
        )

    def get_result(self):
        """
        Returns the result stream and the file name for a finished case.

        Returns:

            result --
                The result byte stream.

            filename --
                The filename for the result. This name could be used to write the
                result stream.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.
            TypeError if the variable is not a list object.
            ValueError if trajectory variable is not present in the result.

        Example::

            result, file_name = case.get_result()
            with open(file_name, "wb") as f:
                f.write(result)
        """
        _assert_successful_operation(self.is_successful(), self._case_id)
        result, file_name = self._exp_sal.case_result_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        return result, file_name

    def get_trajectories(self):
        """
        Returns result(Mapping) object containing the result trajectories.

        Returns:

            trajectories --
                A result trajectory dictionary object.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process was cancelled.

        Example::

            result = case.get_trajectories()
            result_variables = result.keys()
            height = result['h']
            time = res['time']
        """
        _assert_is_complete(CaseStatus(self.info["run_info"]["status"]), "Simulation")
        return Result(
            self._case_id,
            self._workspace_id,
            self._exp_id,
            self._workspace_sal,
            self._exp_sal,
        )

    def get_artifact(self, artifact_id):
        """
        Returns the artifact stream and the file name for a finished case.

        Parameters:

            artifact_id --
                The ID of the artifact.

        Returns:

            artifact --
                The artifact byte stream.

            filename --
                The filename for the artifact. This name could be used to write the
                artifact stream.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            result, file_name = case.get_artifact("ABCD")
            with open(file_name, "wb") as f:
                f.write(result)
        """
        _assert_successful_operation(self.is_successful(), self._case_id)
        result, file_name = self._exp_sal.case_artifact_get(
            self._workspace_id, self._exp_id, self._case_id, artifact_id
        )

        return result, file_name


class Result(Mapping):
    """
    Result class containing base functionality.
    """

    def __init__(
        self, case_id, workspace_id, exp_id, workspace_service=None, exp_service=None
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service
        self._variables = Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        ).get_variables()

    def __getitem__(self, key):
        _assert_variable_in_result([key], self._variables)
        response = self._exp_sal.case_trajectories_get(
            self._workspace_id, self._exp_id, self._case_id, [key]
        )
        return response[0]

    def __iter__(self):
        data = _create_result_dict(
            self._variables,
            self._workspace_id,
            self._exp_id,
            self._case_id,
            self._exp_sal,
        )
        return data.__iter__()

    def __len__(self):
        return self._variables.__len__()

    def keys(self):
        return self._variables


class Log(str):
    """
    Log class inheriting from string object.
    """

    def show(self):
        """Prints the formatted log."""
        print(self)
