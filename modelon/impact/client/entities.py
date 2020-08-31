import os
from modelon.impact.client import operations

from modelon.impact.client.experiment_definition import SimpleExperimentDefinition
from collections.abc import Mapping
from modelon.impact.client.options import ExecutionOption
from modelon.impact.client import exceptions
from enum import Enum


def _assert_successful_operation(is_successful, operation_name="Operation"):
    if not is_successful:
        raise exceptions.OperationFailureError(
            f"{operation_name} failed! See the log for more info!"
        )


def _assert_is_complete(status, operation_name="Operation"):
    if status not in (ModelExecutableStatus.SUCCESSFUL, ExperimentStatus.DONE):
        if status in (ModelExecutableStatus.NOTSTARTED, ExperimentStatus.NOTSTARTED):
            raise exceptions.OperationNotCompleteError(
                f"{operation_name} is still in progress! Status : {status}."
                f" Please call the wait() method on the {operation_name} operation"
                " to wait until completion!"
            )
        elif status in (ModelExecutableStatus.CANCELLED, ExperimentStatus.CANCELLED):
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

        Parameters::

            name --
                The name of the custom function.

        Returns::

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

        Returns::

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

    def import_library(self, path_to_lib):
        """Imports a library to the workspace.

        Parameters::

            path_to_lib --
                The path for the library to be imported.

        Example::

            workspace.import_library('C:/A.mo')
            workspace.import_library('C:/B.mol')
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
        # TO DO: Needs to be tested
        """Downloads the workspace as a binary compressed archive.
        Returns the local path to the downloaded workspace archive.

        Parameters::

            options --
                The specification of what workspace resources to include when
                exporting the workspace.

            path --
                The local path to store the downloaded workspace.

        Returns::

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

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(data)
        return path

    def clone(self):
        """Clones the workspace.
        Returns a clone Workspace class object.

        Returns::

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

        Parameters::

            class_name --
                The modelica class path of the model.

        Returns::

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

        Returns::

            FMUs --
                List of ModelExecutable class objects.

        Example::

            workspace.get_fmus()
        """
        resp = self._workspace_sal.fmus_get(self._workspace_id)
        return [
            ModelExecutable(
                self._workspace_id, item["id"], self._workspace_sal, self._model_exe_sal
            )
            for item in resp["data"]["items"]
        ]

    def get_fmu(self, fmu_id):
        """
        Returns a ModelExecutable class object.

        Returns::

            FMU --
                ModelExecutable class object.

        Example::

            workspace.get_fmu(fmu_id)
        """
        resp = self._workspace_sal.fmu_get(self._workspace_id, fmu_id)
        return ModelExecutable(
            self._workspace_id, resp["id"], self._workspace_sal, self._model_exe_sal
        )

    def get_experiments(self):
        """
        Returns a list of Experiment class objects.

        Returns::

            experiment --
                List of Experiment class objects.

        Example::

            workspace.get_experiments()
        """
        resp = self._workspace_sal.experiments_get(self._workspace_id)
        return [
            Experiment(
                self._workspace_id, item["id"], self._workspace_sal, self._exp_sal
            )
            for item in resp["data"]["items"]
        ]

    def get_experiment(self, experiment_id):
        """
        Returns an Experiment class object.

        Parameters::

            class_name --
                The modelica class path of the model.

        Returns::

            experiment --
                Experiment class object.

        Example::

            workspace.get_experiment(experiment_id)
        """
        resp = self._workspace_sal.experiment_get(self._workspace_id, experiment_id)
        return Experiment(
            self._workspace_id, resp["id"], self._workspace_sal, self._exp_sal
        )

    def create_experiment(self, spec):
        """Creates an experiment.
        Returns an Experiment class object.

        Parameters::

            spec --
                An parametrized experiment specification class of type
                modelon.impact.client.experiment_definition.SimpleExperimentDefinition.

        Returns::

            experiment --
                Experiment class object.

        Example::

            workspace.create_experiment(specification)
        """
        if isinstance(spec, SimpleExperimentDefinition):
            options = spec.to_dict()
        else:
            options = spec
        resp = self._workspace_sal.experiment_create(self._workspace_id, options)
        return Experiment(
            self._workspace_id,
            resp["experiment_id"],
            self._workspace_sal,
            self._exp_sal,
        )

    def execute(self, specification):
        """Exceutes an experiment.
        Returns an modelon.impact.client.operations.ExperimentOperation class object.

        Parameters::

            spec --
                An parametrized experiment specification class of type
                modelon.impact.client.experiment_definition.SimpleExperimentDefinition.

        Returns::

            experiment_ops --
                An modelon.impact.client.operations.ExperimentOperation class object.

        Example::

            experiment_ops = workspace.execute(specification)
            experiment_ops.cancel()
            experiment_ops.status()
            experiment_ops.wait()
        """
        exp_id = self.create_experiment(specification).id
        return operations.ExperimentOperation(
            self._workspace_id,
            self._exp_sal.experiment_execute(self._workspace_id, exp_id),
            self._workspace_sal,
            self._exp_sal,
        )


class _Parameter:
    _JSON_2_PY_TYPE = {
        "Number": float,
        "String": str,
        "Boolean": bool,
        "Enumeration": str,
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

        Parameters::

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

    def options(self):
        """
        Return an modelon.impact.client.options.ExecutionOption object.

        Returns::

            options --
                An modelon.impact.client.options.ExecutionOption object.

        Example::

            custom_function.options()
            custom_function.options().with_simulation_options(ncp=500)
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self.name
        )
        return ExecutionOption(
            self._workspace_id, options, self.name, self._custom_func_sal
        )


class Model:
    """
    Class containing Model functionalities.
    """

    def __init__(
        self, class_name, workspace_id, workspace_service=None, model_exe_service=None
    ):
        self.class_name = class_name
        self._workspace_id = workspace_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def __repr__(self):
        return f"Class name '{self.class_name}'"

    def __eq__(self, obj):
        return isinstance(obj, Model) and obj.class_name == self.class_name

    def compile(
        self,
        options,
        compiler_log_level="info",
        fmi_target="me",
        fmi_version="2.0",
        platform="auto",
    ):
        """Compiles the model to an FMU.
        Returns an modelon.impact.client.operations.ModelExecutableOperation class
        object.

        Returns::

            modelexecutableoperation --
                An modelon.impact.client.operations.ModelExecutableOperation class
                object.

        Example::

            compile_ops=model.compile(options)
            compile_ops.cancel()
            compile_ops.status()
            model.compile(options).wait()
        """
        if not isinstance(options, ExecutionOption):
            raise TypeError("Options must be an instance of ExecutionOption class")

        body = {
            "input": {
                "class_name": self.class_name,
                "compiler_options": options.to_dict()["compiler"],
                "runtime_options": options.to_dict()["runtime"],
                "compiler_log_level": compiler_log_level,
                "fmi_target": fmi_target,
                "fmi_version": fmi_version,
                "platform": platform,
            }
        }
        return operations.ModelExecutableOperation(
            self._workspace_id,
            self._model_exe_sal.compile_model(self._workspace_id, body),
            self._workspace_sal,
            self._model_exe_sal,
        )


class ModelExecutable:
    """
    Class containing ModelExecutable functionalities.
    """

    def __init__(
        self, workspace_id, fmu_id, workspace_service=None, model_exe_service=None,
    ):
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def __repr__(self):
        return f"FMU with id '{self._fmu_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ModelExecutable) and obj._fmu_id == self._fmu_id

    @property
    def id(self):
        """FMU id"""
        return self._fmu_id

    @property
    def info(self):
        """Compilation information as a dictionary"""
        return self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

    @property
    def metadata(self):
        """FMU metadata"""
        _assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.ss_fmu_metadata_get(self._workspace_id, self._fmu_id)

    def is_successful(self):
        """
        Returns True if the model has compiled successfully.

        Returns::

            True -> If model has compiled successfully.
            False -> If compilation process has failed.

        Raises::

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

    def log(self):
        """
        Returns compilation log if the model has compiled.

        Returns::

            log --
                The model executable compilation log.

        Raises::

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process was cancelled.

        Example::

            print(fmu.log())
        """
        _assert_is_complete(
            ModelExecutableStatus(self.info["run_info"]["status"]), "Compilation"
        )
        return self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id)

    def settable_parameters(self):
        """
        Returns a list of settable parameters for the FMU.

        Returns::

            settable_parameters --
                A list of parameters than can be set on the FMU.

        Raises::

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.

        Example::

            fmu.settable_parameters()
        """
        _assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )


class Experiment:
    """
    Class containing Experiment functionalities.
    """

    def __init__(
        self, workspace_id, exp_id, workspace_service=None, exp_service=None,
    ):
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service

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
        return self._workspace_sal.experiment_get(self._workspace_id, self._exp_id)

    def is_successful(self):
        """
        Returns True if the FMU has executed successfully.

        Returns::

            True -> If execution process has completed successfully.
            False -> If execution process has failed.

        Raises::

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

    def variables(self):
        """
        Returns a list of variables available in the result.

        Returns::

            variables --
                An list of result variables.

        Raises::

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            experiment.variables()
        """
        _assert_successful_operation(self.is_successful(), "Simulation")
        return self._exp_sal.result_variables_get(self._workspace_id, self._exp_id)

    def cases(self):
        """
        Returns a list of case objects for an experiment.

        Returns::

            cases --
                An list of case objects.

        Example::

            experiment.cases()
        """
        resp = self._exp_sal.cases_get(self._workspace_id, self._exp_id)
        return [
            Case(
                case["id"],
                self._workspace_id,
                self._exp_id,
                self._exp_sal,
                self._workspace_sal,
            )
            for case in resp["data"]["items"]
        ]

    def case(self, case_id):
        """
        Returns a case object for a given case_id.

        Parameters::

            case_id --
                The case_id for the case.

        Returns::

            cases --
                An case object.

        Example::

            experiment.case('case_1')
        """
        resp = self._exp_sal.case_get(self._workspace_id, self._exp_id, case_id)
        return Case(
            resp["id"],
            self._workspace_id,
            self._exp_id,
            self._exp_sal,
            self._workspace_sal,
        )

    def trajectories(self, variables):
        """
        Returns a dictionary containing the result trajectories
        for a list of result variables for all the cases.

        Parameters::

            variables --
                A list of result variables to fecth trajectories for.

        Example::

            result = experiment.trajectories(['h', 'time'])
            height = result['case_1']['h']
            time = result['case_1']['time']
        """
        if not isinstance(variables, list):
            raise TypeError(
                "Please specify the list of result keys for the trajectories of "
                "intrest!"
            )
        _assert_successful_operation(self.is_successful(), "Simulation")
        _assert_variable_in_result(variables, self.variables())

        response = self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, variables
        )
        return {
            case.id: {variable: response[i][j] for i, variable in enumerate(variables)}
            for j, case in enumerate(self.cases())
        }


class Case:
    """
    Class containing Case functionalities.
    """

    def __init__(
        self, case_id, workspace_id, exp_id, exp_service=None, workspace_service=None
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._exp_sal = exp_service
        self._workspace_sal = workspace_service

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
        return self._exp_sal.case_get(self._workspace_id, self._exp_id, self._case_id)

    def is_successful(self):
        """
        Returns True if a case has completed successfully.

        Returns::

            True -> If the case has executed successfully.
            False -> If the case has failed execution.

        Example::

            case.is_successful()
        """
        return CaseStatus(self.info["run_info"]["status"]) == CaseStatus.SUCCESSFUL

    def log(self):
        """
        Returns the log for a finished case.

        Example::

            print(case.log())
        """
        return self._exp_sal.case_get_log(
            self._workspace_id, self._exp_id, self._case_id
        )

    def result(self):
        """
        Returns the result stream and the file name for a finished case.

        Example::

            result, file_name = case.result()
            with open(file_name, "wb") as f:
                f.write(result)
        """
        _assert_successful_operation(self.is_successful(), self._case_id)
        result, file_name = self._exp_sal.case_result_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        return result, file_name

    def trajectories(self):
        """
        Returns result(Mapping) object containing the result trajectories.

        Example::

            result = case.trajectories()
            height = result['h']
            time = res['time']
        """
        _assert_successful_operation(self.is_successful(), self._case_id)
        return Result(
            self._case_id,
            self._workspace_id,
            self._exp_id,
            self._workspace_sal,
            self._exp_sal,
        )


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
        ).variables()

    def __getitem__(self, key):
        _assert_variable_in_result([key], self._variables)
        response = self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, [key]
        )
        case_index = int(self._case_id.split("_")[1])
        return response[0][case_index - 1]

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
