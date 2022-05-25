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
    FAILED = "failed"


class CaseStatus(Enum):
    """
    Class representing an enumeration for the possible
    Case run info states.
    """

    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NOT_STARTED = "not_started"
    STARTED = 'started'


class Workspace:
    """
    Class containing Workspace functionalities.
    """

    def __init__(
        self,
        workspace_id,
        workspace_service=None,
        model_exe_service=None,
        experiment_service=None,
        custom_function_service=None,
    ):
        self._workspace_id = workspace_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service
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

    def upload_result(self, path_to_result, label=None, description=None):
        """Uploads a '.mat' result file to the workspace.

        Parameters:

            path_to_result --
                The path for the result file to be imported.

            label --
                The label of the result file. Default: None.

            description --
                The description of the result file. Default: None.

        Example::

            workspace.upload_result('C:/A.mat')
            workspace.upload_result('C:/B.mat', label = "result_for_PID.mat",
            description = "This is a result file for PID controller")
        """
        resp = self._workspace_sal.result_upload(
            self._workspace_id, path_to_result, label=label, description=description
        )
        return operations.ExternalResultUploadOperation(
            resp["data"]["id"], self._workspace_sal
        )

    def upload_fmu(
        self,
        fmu_path,
        library_path,
        class_name=None,
        overwrite=False,
        include_patterns=None,
        exclude_patterns=None,
        top_level_inputs=None,
        step_size=0.0,
    ):
        """Uploads a FMU to the workspace.

        Parameters:

            fmu_path --
                The path for the FMU to be imported.

            library_path --
                The library identifier, '{name} {version}' or '{name}' if version is
                missing.

            class_name --
                Qualified name of generated class. By default, 'class_name' is
                set to the name of the library followed by a name based
                on the filename of the imported FMU.

            overwrite --
                Determines if any already existing files should be overwritten.
                Default: False.

            include_patterns, exclude_patterns --
                Specifies what variables from the FMU to include and/or exclude in the
                wrapper model. These two arguments are patterns or lists of patterns as
                the same kind as the argument 'filter' for the function
                'get_model_variables' in PyFMI. If both 'include_patterns' and
                'exclude_patterns' are given, then all variables that matches
                'include_patterns' but does not match 'exclude_patterns' are included.
                Derivatives and variables with a leading underscore in the name are
                always excluded.
                Default value: None (which means to include all the variables).

            top_level_inputs --
                Specify what inputs that should be kept as inputs, i.e. with or without
                the input keyword. The argument is a pattern similar to the arguments
                include_patterns and exclude_patterns. Example: If
                top_level_inputs = 'my_inputs*', then all input variables matching the
                pattern 'my_inputs*' will be generated as inputs, and all other inputs
                not matching the pattern as model variables. If top_level_inputs = '',
                then no input is imported as an input.
                Default value: None (which means all inputs are kept as inputs)
                Type: str or a list of strings

            step_size --
                Specify what value to set for the parameter for step size in the
                generated model. By default the parameter is set to zero, which
                inturn means that the step size will be set during simulation based
                on simulation properties such as the time interval.
                This can also be manually set to any real non-negative number.
                The value of the step size parameter can also be set via the function
                set_step_size, which must be invoked before importing the model.
                Default value: 0.0 (which during simulation is set according to the
                description above).
                Type: number

        Example::

            workspace.upload_fmu('C:/A.fmu',"Workspace")
            workspace.upload_fmu('C:/B.fmu',"Workspace",class_name="Workspace.Model")
        """
        resp = self._workspace_sal.fmu_import(
            self._workspace_id,
            fmu_path,
            library_path,
            class_name,
            overwrite,
            include_patterns,
            exclude_patterns,
            top_level_inputs,
            step_size=step_size,
        )

        if resp["importWarnings"]:
            logger.warning(f"Import Warnings: {'. '.join(resp['importWarnings'])}")

        return Model(
            resp['fmuClassPath'],
            self._workspace_id,
            self._workspace_sal,
            self._model_exe_sal,
        )

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
            self._custom_func_sal,
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
                self._workspace_id,
                item["id"],
                self._workspace_sal,
                self._model_exe_sal,
                self._exp_sal,
                item,
            )
            for item in resp["data"]["items"]
        ]

    def get_experiment(self, experiment_id):
        """
        Returns an Experiment class object.

        Parameters:

            experiment_id --
                The ID of the experiment.

        Returns:

            experiment --
                Experiment class object.

        Example::

            workspace.get_experiment(experiment_id)
        """
        resp = self._workspace_sal.experiment_get(self._workspace_id, experiment_id)
        return Experiment(
            self._workspace_id,
            resp["id"],
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
            resp,
        )

    def create_experiment(self, definition, user_data=None):
        """Creates an experiment.
        Returns an Experiment class object.

        Parameters:

            definition --
                An parametrized experiment definition class of type
                modelon.impact.client.experiment_definition.SimpleModelicaExperimentDefinition
                or
                modelon.impact.client.experiment_definition.SimpleFMUExperimentDefinition.
            user_data --
                Optional dictionary object with custom data to attach to the experiment.

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

        resp = self._workspace_sal.experiment_create(
            self._workspace_id, definition, user_data
        )
        return Experiment(
            self._workspace_id,
            resp["experiment_id"],
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
        )

    def execute(self, definition, user_data=None):
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
            user_data --
                Optional dictionary object with custom data to attach to the experiment.


        Returns:

            experiment_ops --
                An modelon.impact.client.operations.ExperimentOperation class object.

        Example::

            experiment_ops = workspace.execute(definition)
            experiment_ops.cancel()
            experiment_ops.status()
            experiment_ops.wait()
        """
        exp_id = self.create_experiment(definition, user_data).id
        return operations.ExperimentOperation(
            self._workspace_id,
            self._exp_sal.experiment_execute(self._workspace_id, exp_id),
            self._workspace_sal,
            self._model_exe_sal,
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
        self._name = name
        self._value = value
        self._value_type = value_type
        self._valid_values = valid_values

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, self._JSON_2_PY_TYPE[self._value_type]):
            raise ValueError(
                f"Cannot set {self._name} to {value}, its type is {self._value_type}"
            )

        if self._value_type == "Enumeration" and value not in self._valid_values:
            raise ValueError(
                f"Cannot set enumeration '{self._name}' to '{value}', "
                f"must be one of {self._valid_values}"
            )

        self._value = value


class CustomFunction:
    """
    Class containing CustomFunction functionalities.
    """

    def __init__(self, workspace_id, name, parameter_data, custom_function_service):
        self._name = name
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
        return f"Custom function '{self._name}'"

    def __eq__(self, obj):
        return isinstance(obj, CustomFunction) and obj._name == self._name

    @property
    def name(self):
        "Custom function name"
        return self._name

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
            self._workspace_id, self._name, self._parameter_data, self._custom_func_sal
        )
        for name, value in modified.items():
            if name not in new._param_by_name:
                raise ValueError(
                    f"The custom function '{self._name}' "
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
            self._workspace_id, self._name
        )
        return ExecutionOptions(options["compiler"], self._name, self._custom_func_sal)

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
            self._workspace_id, self._name
        )
        return ExecutionOptions(options["runtime"], self._name, self._custom_func_sal)

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
            self._workspace_id, self._name
        )
        return ExecutionOptions(options["solver"], self._name, self._custom_func_sal)

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
            self._workspace_id, self._name
        )
        return ExecutionOptions(
            options["simulation"], self._name, self._custom_func_sal
        )


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
        return f"Class name '{self._class_name}'"

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


class _ModelExecutableRunInfo:
    def __init__(self, status, errors):
        self._status = status
        self._errors = errors

    @property
    def status(self):
        """Status info for a Model-Executable"""
        return self._status

    @property
    def errors(self):
        """A list of errors. Is empty unless 'status' attribute is 'FAILED'"""
        return self._errors


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

    def __hash__(self) -> int:
        return self._fmu_id.__hash__()

    @property
    def id(self):
        """FMU id"""
        return self._fmu_id

    def _variable_modifiers(self):
        return {} if self._modifiers is None else self._modifiers

    def _get_info(self):
        if self._info is None:
            self._info = self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

        return self._info

    @property
    def info(self):
        """Deprecated, use 'run_info' attribute"""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._get_info()

    @property
    def run_info(self):
        """Compilation run information"""
        run_info = self._get_info()["run_info"]
        status = ModelExecutableStatus(run_info["status"])
        errors = run_info.get("errors", [])
        return _ModelExecutableRunInfo(status, errors)

    @property
    def metadata(self):
        """FMU metadata. Returns the 'iteration_variable_count' and 'residual_variable_count'
        only for steady state model compiled as an FMU"""
        _assert_successful_operation(self.is_successful(), "Compilation")
        parameter_state = {"parameterState": self._variable_modifiers()}
        return self._model_exe_sal.ss_fmu_metadata_get(
            self._workspace_id, self._fmu_id, parameter_state
        )

    def is_successful(self):
        """
        Returns True if the model has compiled successfully.
        Use the 'run_info' attribute to get more info.

        Returns:

            True -> If model has compiled successfully.
            False -> If compilation process has failed, is running or is cancelled.

        Example::

            fmu.is_successful()
        """
        return self.run_info.status == ModelExecutableStatus.SUCCESSFUL

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
        _assert_is_complete(self.run_info.status, "Compilation")
        return Log(self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id))

    def delete(self):
        """Deletes an FMU.

        Example::

            fmu.delete()
        """
        self._model_exe_sal.fmu_delete(self._workspace_id, self._fmu_id)

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


class _ExperimentRunInfo:
    def __init__(self, status, errors, failed, successful, cancelled, not_started):
        self._status = status
        self._errors = errors
        self._failed = failed
        self._successful = successful
        self._cancelled = cancelled
        self._not_started = not_started

    @property
    def status(self):
        """Status info for an Experiment"""
        return self._status

    @property
    def errors(self):
        """A list of errors. Is empty unless 'status' attribute is 'FAILED'"""
        return self._errors

    @property
    def successful(self):
        """Number of cases in experiment that are successful"""
        return self._successful

    @property
    def failed(self):
        """Number of cases in experiment thar have failed"""
        return self._failed

    @property
    def cancelled(self):
        """Number of cases in experiment that are cancelled"""
        return self._cancelled

    @property
    def not_started(self):
        """Number of cases in experiment that have not yet started"""
        return self._not_started


class _ExperimentMetaData:
    def __init__(self, user_data):
        self._user_data = user_data

    @property
    def user_data(self):
        """User data dictionary object attached to experiment, if any"""
        return self._user_data


class Experiment:
    """
    Class containing Experiment functionalities.
    """

    def __init__(
        self,
        workspace_id,
        exp_id,
        workspace_service=None,
        model_exe_service=None,
        exp_service=None,
        info=None,
    ):
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service
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

    def _get_info(self):
        if self._info is None:
            self._info = self._workspace_sal.experiment_get(
                self._workspace_id, self._exp_id
            )

        return self._info

    @property
    def run_info(self):
        """Experiment run information"""
        run_info = self._get_info()["run_info"]

        status = ExperimentStatus(run_info["status"])
        errors = run_info.get("errors", [])
        failed = run_info.get("failed", 0)
        successful = run_info.get("successful", 0)
        cancelled = run_info.get("cancelled", 0)
        not_started = run_info.get("not_started", 0)
        return _ExperimentRunInfo(
            status, errors, failed, successful, cancelled, not_started
        )

    @property
    def metadata(self):
        """Experiment metadata. Returns custom user_data dictionary object attached
        to the experiment, if any."""

        info = self._get_info()
        meta_data = info.get("meta_data")
        if meta_data is not None:
            user_data = meta_data.get("user_data")
            if user_data is not None:
                return _ExperimentMetaData(user_data)

        return None

    @property
    def info(self):
        """Deprecated, use 'run_info' attribute"""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._get_info()

    def execute(self, with_cases=None, sync_case_changes=True):
        """Exceutes an experiment.
        Returns an modelon.impact.client.operations.ExperimentOperation class object.

        Parameters:

            with_cases --
                A list of cases objects to execute.
            sync_case_changes --
                Boolean specifying if to sync the cases given with the 'with_cases'
                argument against the server before executing the experiment.
                Default is True.

        Returns:

            experiment_ops --
                An modelon.impact.client.operations.ExperimentOperation class object.

        Example::
            experiment = workspace.create_experiment(experiment_definition)
            experiment_ops = experiment.execute()
            experiment_ops.cancel()
            experiment_ops.status()
            experiment_ops.wait()

            generate_cases = experiment.execute(with_cases=[]).wait()
            cases_to_execute =  generate_cases.get_case('case_2')
            experiment = experiment.execute(with_cases=[cases_to_execute]).wait()
        """
        if sync_case_changes and with_cases is not None:
            for case in with_cases:
                case.sync()

        case_ids = [case.id for case in with_cases] if with_cases is not None else None
        return operations.ExperimentOperation(
            self._workspace_id,
            self._exp_sal.experiment_execute(
                self._workspace_id, self._exp_id, case_ids
            ),
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
        )

    def is_successful(self):
        """
        Returns True if the Experiment is done and no cases has failed.
        Use the 'run_info' attribute to get more info.

        Returns:

            True -> If execution process has completed successfully.
            False -> If execution process has failed, is cancelled or still running.

        Example::

            experiment.is_successful()
        """
        return (
            self.run_info.status == ExperimentStatus.DONE
            and self.run_info.failed == 0
            and self.run_info.cancelled == 0
        )

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
        _assert_is_complete(self.run_info.status, "Simulation")
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
                self._model_exe_sal,
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
        case_data = self._exp_sal.case_get(self._workspace_id, self._exp_id, case_id)
        return Case(
            case_data["id"],
            self._workspace_id,
            self._exp_id,
            self._exp_sal,
            self._model_exe_sal,
            self._workspace_sal,
            case_data,
        )

    def get_cases_with_label(self, case_label):
        """
        Returns a list of case objects for an experiment with the label.

        Parameters:

            case_label --
                The case_label for the case.

        Returns:

            cases --
                An list of case objects.

        Example::

            experiment.get_cases_with_label('Cruise condition')
        """
        return [case for case in self.get_cases() if case.meta.label == case_label]

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
        _assert_is_complete(self.run_info.status, "Simulation")
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

    def delete(self):
        """Deletes an experiment.

        Example::

            experiment.delete()
        """
        self._exp_sal.experiment_delete(self._workspace_id, self._exp_id)

    def set_label(self, label):
        """Sets a label (string) for an experiment to distinguish it.

        Example::

            experiment.set_label("Engine run with Oil type B")
        """
        self._exp_sal.experiment_set_label(self._workspace_id, self._exp_id, label)


class _CaseRunInfo:
    """
    Class containing Case run info.
    """

    def __init__(self, status, consistent):
        self._status = status
        self._consistent = consistent

    @property
    def status(self):
        """Status info for a Case, its type is CaseStatus."""
        return self._status

    @property
    def consistent(self):
        """True if the case has not been synced since it was executed,
        false otherwise."""
        return self._consistent


class _ExternalResultMetaData:
    """
    Class containing external result metadata.
    """

    def __init__(self, id, name, description, workspace_id):
        self._id = id
        self._name = name
        self._description = description
        self._workspace_id = workspace_id

    @property
    def id(self):
        """Result id"""
        return self._id

    @property
    def name(self):
        """Label for result"""
        return self._name

    @property
    def description(self):
        """Description of the result"""
        return self._description

    @property
    def workspace_id(self):
        """Name of workspace"""
        return self._workspace_id


class _CaseAnalysis:
    """
    Class containing Case analysis configuration.
    """

    def __init__(self, analysis):
        self._analysis = analysis

    @property
    def analysis_function(self):
        """The name of the custom function"""
        return self._analysis['analysis_function']

    @property
    def parameters(self):
        """Parameters to the custom function

        Example::
            {
                "start_time": 0,
                "final_time": 1
            }
        """
        return self._analysis['parameters']

    @parameters.setter
    def parameters(self, parameters):
        self._analysis['parameters'] = parameters

    @property
    def simulation_options(self):
        """Key-value pairs of simulation options"""
        return self._analysis['simulation_options']

    @simulation_options.setter
    def simulation_options(self, simulation_options):
        self._analysis['simulation_options'] = simulation_options

    @property
    def solver_options(self):
        """Key-value pairs of solver options"""
        return self._analysis['solver_options']

    @solver_options.setter
    def solver_options(self, solver_options):
        self._analysis['solver_options'] = solver_options

    @property
    def simulation_log_level(self):
        """The simulation log level"""
        return self._analysis['simulation_log_level']

    @simulation_log_level.setter
    def simulation_log_level(self, simulation_log_level):
        self._analysis['simulation_log_level'] = simulation_log_level


class _CaseMeta:
    """
    Class containing Case meta
    """

    def __init__(self, data):
        self._data = data

    @property
    def label(self):
        """Label for the case."""
        return self._data['label']

    @label.setter
    def label(self, label):
        self._data['label'] = label


class _CaseInput:
    """
    Class containing Case input
    """

    def __init__(self, data):
        self._data = data

    @property
    def analysis(self):
        return _CaseAnalysis(self._data['analysis'])

    @property
    def parametrization(self):
        """
        Parameterization of the case, a list of key value pairs where key
        is variable name and value is the value to use for that variable.
        """
        return self._data['parametrization']

    @parametrization.setter
    def parametrization(self, parameterization):
        self._data['parametrization'] = parameterization

    @property
    def fmu_id(self):
        """Reference ID to the compiled model used running the case."""
        return self._data['fmu_id']

    @property
    def structural_parametrization(self):
        """
        Structural parameterization of the case, a list of key value pairs where
        key is variable name and value is the value to use for that variable.
        These are values that cannot be applied to the FMU/Model after compilation.
        """
        return self._data['structural_parametrization']

    @property
    def fmu_base_parametrization(self):
        """
        This is some base parametrization that must be applied to the FMU for
        it to be valid running this case. It often comes as a result from of
        caching to reuse the FMU.
        """
        return self._data['fmu_base_parametrization']


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
        model_exe_service=None,
        workspace_service=None,
        info=None,
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._exp_sal = exp_service
        self._model_exe_sal = model_exe_service
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
    def experiment_id(self):
        """Experiment id"""
        return self._exp_id

    @property
    def info(self):
        """Deprecated, use 'run_info' attribute"""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._info

    @property
    def run_info(self):
        """Case run information"""
        run_info = self._info["run_info"]
        return _CaseRunInfo(CaseStatus(run_info["status"]), run_info["consistent"])

    @property
    def input(self):
        """Case input attributes

        Example::

         case.input.analysis.parameters = {'start_time': 0, 'final_time': 90}
         case.input.analysis.simulation_options = {'ncp': 600}
         case.input.analysis.solver_options = {'atol': 1e-8}
         case.input.parametrization = {'PI.k': 120}
         case.sync()

         help(case.input.analysis) # See help for attribute
         dir(case.input) # See nested attributes
        """
        return _CaseInput(self._info['input'])

    @property
    def meta(self):
        """Case meta attributes

        Example::

         case.meta.label = 'Cruise condition'
         case.sync()

         help(case.meta) # See help for attribute
         dir(case.input) # See nested attributes
        """
        return _CaseMeta(self._info['meta'])

    @property
    def initialize_from_case(self):
        init_from_dict = self._info['input'].get('initialize_from_case')
        if init_from_dict is None:
            return None

        experiment_id = init_from_dict.get('experimentId')
        case_id = init_from_dict.get('caseId')

        case_data = self._exp_sal.case_get(self._workspace_id, experiment_id, case_id)
        return Case(
            case_data["id"],
            self._workspace_id,
            experiment_id,
            self._exp_sal,
            self._model_exe_sal,
            self._workspace_sal,
            case_data,
        )

    @initialize_from_case.setter
    def initialize_from_case(self, case):
        if not isinstance(case, Case):
            raise TypeError(
                "The value must be an instance of modelon.impact.client.entities.Case"
            )
        self._assert_unique_case_initialization('initialize_from_external_result')
        self._info['input']['initialize_from_case'] = {
            'experimentId': case.experiment_id,
            'caseId': case.id,
        }

    @property
    def initialize_from_external_result(self):
        init_from_dict = self._info['input'].get('initialize_from_external_result')

        if init_from_dict is None:
            return None

        result_id = init_from_dict.get('uploadId')

        return ExternalResult(result_id, self._workspace_sal)

    @initialize_from_external_result.setter
    def initialize_from_external_result(self, result):
        if not isinstance(result, ExternalResult):
            raise TypeError(
                "The value must be an instance of "
                "modelon.impact.client.entities.ExternalResult"
            )
        self._assert_unique_case_initialization('initialize_from_case')
        self._info['input']['initialize_from_external_result'] = {"uploadId": result.id}

    def is_successful(self):
        """
        Returns True if a case has completed successfully.

        Returns:

            True -> If the case has executed successfully.
            False -> If the case has failed execution.

        Example::

            case.is_successful()
        """
        return self.run_info.status == CaseStatus.SUCCESSFUL

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
        _assert_is_complete(self.run_info.status, "Simulation")
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

    def get_fmu(self):
        """
        Returns the ModelExecutable class object simulated for the case.

        Returns:

            FMU --
                ModelExecutable class object.

        Example::

            case = experiment.get_case('case_1')
            fmu = case.get_fmu()
            fmus = set(case.get_fmu() for case in exp.get_cases())
        """
        fmu_id = self.input.fmu_id

        return ModelExecutable(
            self._workspace_id, fmu_id, self._workspace_sal, self._model_exe_sal
        )

    def sync(self):
        """Sync case state against server, pushing any changes that has been
        done to the object client side.

        Example::
            case.input.parametrization = {'PI.k': 120}
            case.sync()
        """
        self._info = self._exp_sal.case_put(
            self._workspace_id, self._exp_id, self._case_id, self._info
        )

    def execute(self, sync_case_changes=True):
        """Exceutes a case.
        Returns an modelon.impact.client.operations.CaseOperation class object.

        Parameters:

            sync_case_changes --
                Boolean specifying if to sync case changes against the server
                before executing the case. Default is True.


        Returns:

            case_ops --
                An modelon.impact.client.operations.CaseOperation class object.

        Example::
            case = experiment.get_case('case_1')
            case.input.parametrization = {'PI.k': 120}
            case.sync()
            case_ops = case.execute()
            case_ops.cancel()
            case_ops.status()
            case_ops.wait()
        """
        if sync_case_changes:
            self.sync()

        return operations.CaseOperation(
            self._workspace_id,
            self._exp_sal.experiment_execute(
                self._workspace_id, self._exp_id, [self._case_id]
            ),
            self._case_id,
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
        )

    def _assert_unique_case_initialization(self, unsupported_init):
        if self._info['input'][unsupported_init]:
            raise ValueError(
                "A case cannot use both 'initialize_from_case' and "
                "'initialize_from_external_result' to specify what to initialize from! "
                f"To resolve this, set the '{unsupported_init}' attribute "
                "to None and re-try."
            )


class Result(Mapping):
    """
    Result class containing base functionality.
    """

    def __init__(
        self, case_id, workspace_id, exp_id, workspace_service=None, exp_service=None,
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service
        self._variables = Experiment(
            self._workspace_id,
            self._exp_id,
            self._workspace_sal,
            exp_service=self._exp_sal,
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


class ExternalResult:
    """
    Class containing  external result.
    """

    def __init__(self, result_id, workspace_service=None):
        self._result_id = result_id
        self._workspace_sal = workspace_service

    def __repr__(self):
        return f"Result id '{self._result_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ExternalResult) and obj._result_id == self._result_id

    @property
    def id(self):
        """Result id"""
        return self._result_id

    @property
    def metadata(self):
        """External result metadata."""
        upload_meta = self._workspace_sal.get_uploaded_result_meta(self._result_id)[
            "data"
        ]
        id = upload_meta.get("id")
        name = upload_meta.get("name")
        description = upload_meta.get("description")
        workspace_id = upload_meta.get("workspaceId")
        return _ExternalResultMetaData(id, name, description, workspace_id)

    def delete(self):
        self._workspace_sal.delete_uploaded_result(self._result_id)


class Log(str):
    """
    Log class inheriting from string object.
    """

    def show(self):
        """Prints the formatted log."""
        print(self)
