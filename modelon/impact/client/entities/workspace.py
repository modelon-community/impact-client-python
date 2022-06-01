import logging
import os
from typing import Any, List, Dict, Optional, Union
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.sal.model_executable import ModelExecutableService
from modelon.impact.client.sal.experiment import ExperimentService
from modelon.impact.client.sal.custom_function import CustomFunctionService
from modelon.impact.client.experiment_definition.base import (
    SimpleModelicaExperimentDefinition,
    SimpleFMUExperimentDefinition,
)
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.operations.experiment import ExperimentOperation
from modelon.impact.client.operations.external_result import (
    ExternalResultUploadOperation,
)
from modelon.impact.client.entities.model import Model
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.experiment import Experiment


logger = logging.getLogger(__name__)

ExperimentDefinition = Union[
    SimpleModelicaExperimentDefinition, SimpleFMUExperimentDefinition, Dict[str, Any],
]


class Workspace:
    """
    Class containing Workspace functionalities.
    """

    def __init__(
        self,
        workspace_id: str,
        workspace_service: WorkspaceService,
        model_exe_service: ModelExecutableService,
        experiment_service: ExperimentService,
        custom_function_service: CustomFunctionService,
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
    def id(self) -> str:
        """Workspace id"""
        return self._workspace_id

    def get_custom_function(self, name: str) -> CustomFunction:
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

    def get_custom_functions(self) -> List[CustomFunction]:
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

    def upload_model_library(self, path_to_lib: str):
        """Uploads a modelica library or a modelica model to the workspace.

        Parameters:

            path_to_lib --
                The path for the library to be imported.

        Example::

            workspace.upload_model_library('C:/A.mo')
            workspace.upload_model_library('C:/B.mol')
        """
        self._workspace_sal.library_import(self._workspace_id, path_to_lib)

    def upload_result(
        self,
        path_to_result: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ExternalResultUploadOperation:
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
        return ExternalResultUploadOperation(resp["data"]["id"], self._workspace_sal)

    def upload_fmu(
        self,
        fmu_path: str,
        library_path: str,
        class_name: Optional[str] = None,
        overwrite: bool = False,
        include_patterns: Optional[Union[str, List[str]]] = None,
        exclude_patterns: Optional[Union[str, List[str]]] = None,
        top_level_inputs: Optional[Union[str, List[str]]] = None,
        step_size: float = 0.0,
    ) -> Model:
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

    def download(self, options: Dict[str, Any], path: str) -> str:
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

    def clone(self) -> 'Workspace':
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

    def get_model(self, class_name: str) -> Model:
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

    def get_fmus(self) -> List[ModelExecutable]:
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

    def get_fmu(self, fmu_id: str) -> ModelExecutable:
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

    def get_experiments(self) -> List[Experiment]:
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

    def get_experiment(self, experiment_id: str) -> Experiment:
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

    def create_experiment(
        self,
        definition: ExperimentDefinition,
        user_data: Optional[Dict[str, Any]] = None,
    ) -> Experiment:
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
        if isinstance(
            definition,
            (SimpleFMUExperimentDefinition, SimpleModelicaExperimentDefinition),
        ):
            definition_as_dict = definition.to_dict()
        elif isinstance(definition, dict):
            definition_as_dict = definition
        else:
            raise TypeError(
                "Definition object must either be a dictionary or an instance of either"
                "modelon.impact.client.experiment_definition."
                "SimpleModelicaExperimentDefinition class or modelon.impact.client."
                "experiment_definition.SimpleFMUExperimentDefinition.!"
            )
        resp = self._workspace_sal.experiment_create(
            self._workspace_id, definition_as_dict, user_data
        )
        return Experiment(
            self._workspace_id,
            resp["experiment_id"],
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
        )

    def execute(
        self,
        definition: ExperimentDefinition,
        user_data: Optional[Dict[str, Any]] = None,
    ) -> ExperimentOperation:
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
        return ExperimentOperation(
            self._workspace_id,
            self._exp_sal.experiment_execute(self._workspace_id, exp_id),
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
        )
