from __future__ import annotations
from dataclasses import dataclass
import logging
import os
import json
from typing import Any, List, Dict, Optional, Union, TYPE_CHECKING
from modelon.impact.client.sal.service import Service
from modelon.impact.client.experiment_definition.base import (
    SimpleModelicaExperimentDefinition,
    SimpleFMUExperimentDefinition,
)
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.operations.workspace.exports import (
    WorkspaceExportOperation,
    Export,
)
from modelon.impact.client.operations.workspace.imports import WorkspaceImportOperation
from modelon.impact.client.operations.workspace.conversion import (
    WorkspaceConversionOperation,
)
from modelon.impact.client.operations.project_import import ProjectImportOperation
from modelon.impact.client.operations.experiment import ExperimentOperation
from modelon.impact.client.operations.external_result_import import (
    ExternalResultImportOperation,
)
import modelon.impact.client.entities.model
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.entities.project import Project, VcsUri

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import BaseOperation

logger = logging.getLogger(__name__)

ExperimentDefinition = Union[
    SimpleModelicaExperimentDefinition,
    SimpleFMUExperimentDefinition,
    Dict[str, Any],
]


@dataclass
class Reference:
    id: str


@dataclass
class ReleasedProjectReference:
    id: str
    name: str
    version: Optional[str] = None
    build: Optional[str] = None


@dataclass
class VcsReference:
    id: str
    vcs_uri: str


def _get_project_entry_reference(
    reference: Any,
) -> Union[ReleasedProjectReference, VcsReference, Reference]:
    if "name" in reference:
        return ReleasedProjectReference(
            id=reference.get('id'),
            name=reference.get('name'),
            version=reference.get('version'),
            build=reference.get('build'),
        )
    elif "vcsUri" in reference:
        return VcsReference(id=reference.get('id'), vcs_uri=reference.get('vcsUri'))
    else:
        return Reference(id=reference.get('id'))


class ProjectEntry:
    def __init__(self, data: Any) -> None:
        self._data = data

    @property
    def reference(self) -> Union[ReleasedProjectReference, VcsReference, Reference]:
        return _get_project_entry_reference(self._data.get('reference'))

    @property
    def id(self) -> str:
        return self.reference.id

    @property
    def disabled(self) -> bool:
        return self._data.get('disabled')

    @property
    def disabled_content(self) -> bool:
        return self._data.get('disabledContent')


class WorkspaceDefinition:
    def __init__(self, data: Any) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return self._data.get('name')

    @property
    def format(self) -> str:
        return self._data.get('format')

    @property
    def description(self) -> str:
        return self._data.get('description')

    @property
    def created_by(self) -> str:
        return self._data.get('createdBy')

    @property
    def default_project_id(self) -> str:
        return self._data.get('defaultProjectId')

    @property
    def projects(self) -> List[ProjectEntry]:
        projects = self._data.get('projects', [])
        return [ProjectEntry(project) for project in projects]

    @property
    def dependencies(self) -> List[ProjectEntry]:
        dependencies = self._data.get('dependencies', [])
        return [ProjectEntry(dependency) for dependency in dependencies]

    def to_file(self, path: str) -> str:
        os.makedirs(path, exist_ok=True)
        definition_path = os.path.join(path, self.name + ".json")
        with open(definition_path, "w", encoding='utf-8') as f:
            json.dump(self._data, f, indent=4)
        return definition_path

    @classmethod
    def from_file(cls, path: str) -> WorkspaceDefinition:
        with open(path) as json_file:
            data = json.load(json_file)
        return cls(data)

    def to_dict(self) -> Dict[str, Any]:
        return self._data


class Workspace:
    """Class containing Workspace functionalities."""

    def __init__(
        self,
        workspace_id: str,
        workspace_definition: Union[WorkspaceDefinition, Dict[str, Any]],
        service: Service,
    ):
        self._workspace_id = workspace_id
        self._workspace_definition = (
            WorkspaceDefinition(workspace_definition)
            if isinstance(workspace_definition, dict)
            else workspace_definition
        )
        self._sal = service

    def __repr__(self) -> str:
        return f"Workspace with id '{self._workspace_id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Workspace) and obj._workspace_id == self._workspace_id

    @property
    def id(self) -> str:
        """Workspace id."""
        return self._workspace_id

    @property
    def definition(self) -> WorkspaceDefinition:
        return self._workspace_definition

    def get_custom_function(self, name: str) -> CustomFunction:
        """Returns a CustomFunction class object.

        Args:

            name:
                The name of the custom function.

        Returns:

            custom_function:
                The CustomFunction class object.

        Example::

            workspace.get_custom_function('dynamic')

        """
        custom_function = self._sal.custom_function.custom_function_get(
            self._workspace_id, name
        )
        return CustomFunction(
            self._workspace_id,
            custom_function["name"],
            custom_function["parameters"],
            self._sal,
        )

    def get_custom_functions(self) -> List[CustomFunction]:
        """Returns a list of CustomFunctions class objects.

        Returns:

            custom_functions:
                A list of CustomFunction class objects.

        Example::

            workspace.get_custom_functions()

        """
        custom_functions = self._sal.custom_function.custom_functions_get(
            self._workspace_id
        )
        return [
            CustomFunction(
                self._workspace_id,
                custom_function["name"],
                custom_function["parameters"],
                self._sal,
            )
            for custom_function in custom_functions["data"]["items"]
        ]

    def delete(self) -> None:
        """Deletes a workspace.

        Example::

            workspace.delete()

        """
        self._sal.workspace.workspace_delete(self._workspace_id)

    def upload_result(
        self,
        path_to_result: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ExternalResultImportOperation:
        """Uploads a '.mat' result file to the workspace.

        Args:

            path_to_result:
                The path for the result file to be imported.

            label:
                The label of the result file. Default: None.

            description:
                The description of the result file. Default: None.

        Example::

            workspace.upload_result('C:/A.mat')
            workspace.upload_result('C:/B.mat', label = "result_for_PID.mat",
            description = "This is a result file for PID controller")

        """
        resp = self._sal.external_result.result_upload(
            self._workspace_id, path_to_result, label=label, description=description
        )
        return ExternalResultImportOperation[ExternalResult](
            resp["data"]["location"], self._sal, ExternalResult.from_operation
        )

    def export(self) -> WorkspaceExportOperation:
        """Exports the workspace as a binary compressed archive. Similar to
        :obj:`~modelon.impact.client.entities.workspace.Workspace.download`,
        but gives more control for getting the workspace async.
        Returns an modelon.impact.client.operations.workspace.exports
        .WorkspaceExportOperation class object.

        Returns:

            WorkspaceExportOperation:
                An modelon.impact.client.operations.workspace.exports.
                WorkspaceExportOperation class object.

        Example::

            path = workspace.export().wait().download_as('/home/workspace.zip')
        """
        resp = self._sal.workspace.workspace_export_setup(self._workspace_id)
        return WorkspaceExportOperation[Workspace](
            resp["data"]["location"], self._sal, Export.from_operation
        )

    def download(self, path: str) -> str:
        """Downloads the workspace as a binary compressed archive. Returns the
        local path to the downloaded workspace archive. Similar to
        :obj:`~modelon.impact.client.entities.workspace.Workspace.export`, but
        does the entire setup and download in one go.

        Args:

            path:
                The local path to store the downloaded workspace.

        Returns:

            path:
                Local path to the downloaded workspace archive.

        Example::

            workspace.download(path)

        """
        ws_path = os.path.join(path, self._workspace_id + ".zip")
        ops = self.export().wait()
        return ops.download_as(ws_path)

    def clone(self) -> Workspace:
        """Clones the workspace. Returns a clone Workspace class object.

        Returns:

            workspace_clone:
                Clones workspace class object.

        Example::

            workspace.clone()

        """
        resp = self._sal.workspace.workspace_clone(self._workspace_id)
        return Workspace(resp["workspace_id"], resp["definition"], self._sal)

    def get_model(
        self, class_name: str, project: Optional[Project] = None
    ) -> modelon.impact.client.entities.model.Model:
        """Returns a Model class object.

        Args:

            class_name:
                The Modelica class path of the model.

            project:
                Project class object

        Returns:

            model:
                Model class object.

        Example::

            workspace.get_model(class_name)

        """
        project = project or self.get_default_project()
        return modelon.impact.client.entities.model.Model(
            class_name, self._workspace_id, project.id, self._sal
        )

    def get_fmus(self) -> List[ModelExecutable]:
        """Returns a list of ModelExecutable class objects.

        Returns:

            FMUs:
                List of ModelExecutable class objects.

        Example::

            workspace.get_fmus()

        """
        resp = self._sal.workspace.fmus_get(self._workspace_id)
        return [
            ModelExecutable(self._workspace_id, item["id"], self._sal, item)
            for item in resp["data"]["items"]
        ]

    def get_fmu(self, fmu_id: str) -> ModelExecutable:
        """Returns a ModelExecutable class object.

        Returns:

            FMU:
                ModelExecutable class object.

        Example::

            workspace.get_fmu(fmu_id)

        """
        resp = self._sal.workspace.fmu_get(self._workspace_id, fmu_id)
        return ModelExecutable(self._workspace_id, resp["id"], self._sal, resp)

    def get_experiments(self) -> List[Experiment]:
        """Returns a list of Experiment class objects.

        Returns:

            experiment:
                List of Experiment class objects.

        Example::

            workspace.get_experiments()

        """
        resp = self._sal.workspace.experiments_get(self._workspace_id)
        return [
            Experiment(self._workspace_id, item["id"], self._sal, item)
            for item in resp["data"]["items"]
        ]

    def get_experiment(self, experiment_id: str) -> Experiment:
        """Returns an Experiment class object.

        Args:

            experiment_id:
                The ID of the experiment.

        Returns:

            experiment:
                Experiment class object.

        Example::

            workspace.get_experiment(experiment_id)

        """
        resp = self._sal.workspace.experiment_get(self._workspace_id, experiment_id)
        return Experiment(self._workspace_id, resp["id"], self._sal, resp)

    def create_experiment(
        self,
        definition: ExperimentDefinition,
        user_data: Optional[Dict[str, Any]] = None,
    ) -> Experiment:
        """Creates an experiment. Returns an Experiment class object.

        Args:

            definition:
                An parametrized experiment definition class of type
                modelon.impact.client.experiment_definition.base.SimpleModelicaExperimentDefinition
                or
                modelon.impact.client.experiment_definition.base.SimpleFMUExperimentDefinition.
            user_data:
                Optional dictionary object with custom data to attach to the experiment.

        Returns:

            experiment:
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
                "modelon.impact.client.experiment_definition.base."
                "SimpleModelicaExperimentDefinition class or modelon.impact.client."
                "experiment_definition.base.SimpleFMUExperimentDefinition.!"
            )
        resp = self._sal.workspace.experiment_create(
            self._workspace_id, definition_as_dict, user_data
        )
        return Experiment(self._workspace_id, resp["experiment_id"], self._sal)

    def execute(
        self,
        definition: ExperimentDefinition,
        user_data: Optional[Dict[str, Any]] = None,
    ) -> ExperimentOperation:
        """Exceutes an experiment. Returns an
        modelon.impact.client.operations.experiment.ExperimentOperation class
        object.

        Args:

            definition:
                An experiment definition class instance of
                modelon.impact.client.experiment_definition.base.SimpleFMUExperimentDefinition
                or
                modelon.impact.client.experiment_definition.base.SimpleModelicaExperimentDefinition
                or
                a dictionary object containing the definition.
            user_data:
                Optional dictionary object with custom data to attach to the experiment.


        Returns:

            experiment_ops:
                An modelon.impact.client.operations.experiment.ExperimentOperation
                class object.

        Example::

            experiment_ops = workspace.execute(definition)
            experiment_ops.cancel()
            experiment_ops.status()
            experiment_ops.wait()

        """
        exp_id = self.create_experiment(definition, user_data).id
        return ExperimentOperation[Experiment](
            self._workspace_id,
            self._sal.experiment.experiment_execute(self._workspace_id, exp_id),
            self._sal,
            Experiment.from_operation,
        )

    def get_projects(
        self, vcs_info: bool = True, include_disabled: bool = False
    ) -> List[Project]:
        """Return the list of projects for a workspace.

        Returns:

            projects:
                A list of modelon.impact.client.entities.project.Project
                class object.

        Example::

            projects = workspace.get_projects()

        """
        resp = self._sal.workspace.projects_get(
            self._workspace_id, vcs_info=vcs_info, include_disabled=include_disabled
        )
        projects = [
            Project(
                item["id"],
                item['definition'],
                item["projectType"],
                VcsUri.from_dict(item["vcsUri"]) if item.get("vcsUri") else None,
                self._sal,
            )
            for item in resp["data"]["items"]
        ]
        return projects

    def get_dependencies(
        self, vcs_info: bool = True, include_disabled: bool = False
    ) -> List[Project]:
        """Return the list of project dependencies for a workspace.

        Returns:

            dependencies:
                A list of modelon.impact.client.entities.project.Project
                class object.

        Example::

            dependencies = workspace.get_dependencies()

        """
        resp = self._sal.workspace.dependencies_get(
            self._workspace_id, vcs_info, include_disabled
        )
        return [
            Project(
                item["id"],
                item['definition'],
                item["projectType"],
                VcsUri.from_dict(item["vcsUri"]) if item.get("vcsUri") else None,
                self._sal,
            )
            for item in resp["data"]["items"]
        ]

    def create_project(self, name: str) -> Project:
        """Creates a new project in the workspace.

        Returns:

            project:
                An modelon.impact.client.entities.project.Project
                class object.

        Example::

            project = workspace.create_project("test")

        """
        resp = self._sal.workspace.project_create(self._workspace_id, name)
        return Project(
            resp["id"],
            resp['definition'],
            resp["projectType"],
            VcsUri.from_dict(resp["vcsUri"]) if resp.get("vcsUri") else None,
            self._sal,
        )

    def get_default_project(self) -> Project:
        """Return the default project for a workspace.

        Returns:

            project:
                An modelon.impact.client.entities.project.Project
                class object.

        Example::

            project = workspace.get_default_project()

        """
        if not self._workspace_definition.default_project_id:
            raise ValueError(
                f'No default project exists for the workspace {self._workspace_id}!'
            )
        resp = self._sal.project.project_get(
            self._workspace_definition.default_project_id, vcs_info=True
        )
        return Project(
            resp["id"],
            resp["definition"],
            resp["projectType"],
            VcsUri.from_dict(resp["vcsUri"]) if resp.get("vcsUri") else None,
            self._sal,
        )

    def get_shared_definition(self, strict: bool = False) -> WorkspaceDefinition:
        return WorkspaceDefinition(
            self._sal.workspace.shared_definition_get(
                self._workspace_id, strict=strict
            )["definition"]
        )

    def import_project_from_zip(self, path_to_project: str) -> ProjectImportOperation:
        """Imports a Project from a compressed(.zip) project file and adds it
        to the workspace. Returns the project class object.

        Args:

            path_to_project:
                The path for the compressed project(.zip) to be uploaded.

        Returns:

            ProjectImportOperation:
                An modelon.impact.client.operations.project_import.
                ProjectImportOperation class object.

        Example::

            workspace.import_project_from_zip(path_to_project).wait()

        """
        resp = self._sal.workspace.import_project_from_zip(
            self._workspace_id, path_to_project
        )
        return ProjectImportOperation[Project](
            resp["data"]["location"], self._sal, Project.from_operation
        )

    def import_dependency_from_zip(
        self, path_to_dependency: str
    ) -> ProjectImportOperation:
        """Imports a Project dependency from a compressed(.zip) project file
        and adds it to the workspace. Returns the project class object.

        Args:

            path_to_dependency:
                The path for the compressed project(.zip) to be uploaded.

        Returns:

            ProjectImportOperation:
                An modelon.impact.client.operations.project_import.
                ProjectImportOperation class object.

        Example::

            workspace.import_dependency_from_zip(path_to_project).wait()

        """
        resp = self._sal.workspace.import_dependency_from_zip(
            self._workspace_id, path_to_dependency
        )
        return ProjectImportOperation[Project](
            resp["data"]["location"], self._sal, Project.from_operation
        )

    @classmethod
    def from_import_operation(
        cls, operation: BaseOperation[Workspace], **kwargs: Any
    ) -> Workspace:
        assert isinstance(operation, WorkspaceImportOperation)
        return cls(**kwargs, service=operation._sal)

    @classmethod
    def from_conversion_operation(
        cls, operation: BaseOperation[Workspace], **kwargs: Any
    ) -> Workspace:
        assert isinstance(operation, WorkspaceConversionOperation)
        return cls(**kwargs, service=operation._sal)
