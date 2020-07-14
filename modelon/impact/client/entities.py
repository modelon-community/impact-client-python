import os
from modelon.impact.client.experiment_definition import SimpleExperimentDefinition

from modelon.impact.client.operations import (
    ModelExecutbleOperation,
    ExperimentOperation,
)


class Workspace:
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
        return self._workspace_id

    def get_custom_function(self, name):
        custom_function = self._custom_func_sal.custom_function_get(
            self._workspace_id, name
        )
        return CustomFunction(custom_function["name"], custom_function["parameters"])

    def get_custom_functions(self):
        custom_functions = self._custom_func_sal.custom_functions_get(
            self._workspace_id
        )
        return [
            CustomFunction(custom_function["name"], custom_function["parameters"])
            for custom_function in custom_functions["data"]["items"]
        ]

    def get_options(self, custom_function):
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, custom_function
        )
        return ExecutionOption(self._workspace_id, options)

    def set_options(self, custom_function, options):
        opts = options.to_dict if isinstance(options, ExecutionOption) else options
        self._custom_func_sal.custom_function_options_set(
            self._workspace_id, custom_function, opts
        )

    def delete_options(self, custom_function, options):
        opts = options.to_dict if isinstance(options, ExecutionOption) else options
        self._custom_func_sal.custom_function_options_delete(
            self._workspace_id, custom_function, opts
        )

    def delete(self):
        self._workspace_sal.workspace_delete(self._workspace_id)

    def get_model(self, class_name):
        return Model(
            class_name, self._workspace_id, self._workspace_sal, self._model_exe_sal
        )

    def import_library(self, path_to_lib):
        return self._workspace_sal.library_import(self._workspace_id, path_to_lib)

    def lock(self):
        self._workspace_sal.workspace_lock(self._workspace_id)

    def unlock(self):
        self._workspace_sal.workspace_unlock(self._workspace_id)

    def download(self, options, path):
        # TO DO: Needs to be tested
        data = self._workspace_sal.workspace_download(self._workspace_id, options, path)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(data)
        return path

    def clone(self):
        resp = self._workspace_sal.workspace_clone(self._workspace_id)
        return Workspace(
            resp["workspace_id"],
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
        )

    def get_fmus(self):
        resp = self._workspace_sal.fmus_get(self._workspace_id)
        return [
            ModelExecutable(
                self._workspace_id, item["id"], self._workspace_sal, self._model_exe_sal
            )
            for item in resp["data"]["items"]
        ]

    def get_fmu(self, fmu_id):
        resp = self._workspace_sal.fmu_get(self._workspace_id, fmu_id)
        return ModelExecutable(
            self._workspace_id, resp["id"], self._workspace_sal, self._model_exe_sal
        )

    def get_experiments(self):
        resp = self._workspace_sal.experiments_get(self._workspace_id)
        return [
            Experiment(
                self._workspace_id, item["id"], self._workspace_sal, self._exp_sal
            )
            for item in resp["data"]["items"]
        ]

    def get_experiment(self, experiment_id):
        resp = self._workspace_sal.experiment_get(self._workspace_id, experiment_id)
        return Experiment(
            self._workspace_id, resp["id"], self._workspace_sal, self._exp_sal
        )

    def create_experiment(self, spec):
        if isinstance(spec, SimpleExperimentDefinition):
            options = spec.to_dict
        else:
            options = spec
        resp = self._workspace_sal.experiment_create(self._workspace_id, options)
        return Experiment(self._workspace_id, resp, self._workspace_sal, self._exp_sal)


class Model:
    def __init__(
        self, class_name, workspace_id, workspace_service=None, model_exe_service=None
    ):
        self._workspace_id = workspace_id
        self._class_name = class_name
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def __repr__(self):
        return f"Class name'{self._class_name}'"

    def __eq__(self, obj):
        return isinstance(obj, Model) and obj._class_name == self._class_name

    def compile(self, options):
        return ModelExecutbleOperation(
            self._workspace_id,
            self._model_exe_sal.compile_model(self._workspace_id, options),
            self._workspace_sal,
            self._model_exe_sal,
        )


class ModelExecutable:
    def __init__(
        self,
        workspace_id,
        fmu_id,
        workspace_service=None,
        model_executable_service=None,
    ):
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_executable_service

    def __repr__(self):
        return f"FMU with id '{self._fmu_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ModelExecutable) and obj._fmu_id == self._fmu_id

    @property
    def id(self):
        return self._fmu_id

    @property
    def log(self):
        return self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id)

    @property
    def settable_parameters(self):
        return self._model_exe_sal.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )

    @property
    def info(self):
        return self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

    @property
    def metadata(self):
        return self._workspace_sal.ss_fmu_metadata_get(self._workspace_id, self._fmu_id)


class Experiment:
    def __init__(
        self,
        workspace_id,
        experiment_id,
        workspace_service=None,
        experiment_service=None,
    ):
        self._workspace_id = workspace_id
        self._exp_id = experiment_id
        self._exp_sal = experiment_service
        self._workspace_sal = workspace_service

    def __repr__(self):
        return f"Experiment with id '{self._exp_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Experiment) and obj._exp_id == self._exp_id

    @property
    def id(self):
        return self._exp_id

    @property
    def variables(self):
        return self._exp_sal.result_variables_get(self._workspace_id, self._exp_id)

    @property
    def info(self):
        return self._workspace_sal.experiment_get(self._workspace_id, self._exp_id)

    @property
    def execute(self):
        return ExperimentOperation(
            self._workspace_id,
            self._workspace_sal.experiment_execute(self._workspace_id, self._exp_id),
            self._workspace_sal,
            self._exp_sal,
        )

    def get_trajectories(self, variables):
        return self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, variables
        )


class ExecutionOption:
    def __init__(
        self, workspace_id, options,
    ):
        self._workspace_id = workspace_id
        self._options = options

    def __repr__(self):
        return f"Execution option for '{self._custom_function}'"

    @property
    def to_dict(self):
        return self._options


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
    def __init__(self, name, parameter_data):
        self.name = name
        self._parameter_data = parameter_data
        self._param_by_name = {
            p["name"]: _Parameter(
                p["name"], p["defaultValue"], p["type"], p.get("values", []),
            )
            for p in parameter_data
        }

    def with_parameters(self, **modified):
        new = CustomFunction(self.name, self._parameter_data)
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
        return {p.name: p.value for p in self._param_by_name.values()}
