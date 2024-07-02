from __future__ import annotations

import enum
import json
import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from modelon.impact.client.configuration import Experimental
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.file_uri import ModelicaResourceURI
from modelon.impact.client.entities.interfaces.workspace import WorkspaceInterface
from modelon.impact.client.entities.model import Model
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.project import Project, VcsUri
from modelon.impact.client.exceptions import (
    NoAssociatedPublishedWorkspaceError,
    RemotePublishedWorkspaceLinkError,
)
from modelon.impact.client.experiment_definition.interfaces.definition import (
    BaseExperimentDefinition,
)
from modelon.impact.client.operations.experiment import ExperimentOperation
from modelon.impact.client.operations.external_result_import import (
    ExternalResultImportOperation,
)
from modelon.impact.client.operations.project_import import ProjectImportOperation
from modelon.impact.client.operations.workspace.conversion import (
    WorkspaceConversionOperation,
)
from modelon.impact.client.operations.workspace.exports import (
    Export,
    WorkspaceExportOperation,
)
from modelon.impact.client.operations.workspace.imports import WorkspaceImportOperation
from modelon.impact.client.sal.exceptions import HTTPError
from modelon.impact.client.sal.service import Service

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import BaseOperation

logger = logging.getLogger(__name__)

ExperimentDefinition = Union[
    BaseExperimentDefinition,
    Dict[str, Any],
]


@dataclass
class AccessSettings:
    share_with_own_tenant: bool = True


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
            id=reference.get("id"),
            name=reference.get("name"),
            version=reference.get("version"),
            build=reference.get("build"),
        )
    elif "vcsUri" in reference:
        return VcsReference(id=reference.get("id"), vcs_uri=reference.get("vcsUri"))
    else:
        return Reference(id=reference.get("id"))


class ProjectEntry:
    def __init__(self, data: Any) -> None:
        self._data = data

    @property
    def reference(self) -> Union[ReleasedProjectReference, VcsReference, Reference]:
        return _get_project_entry_reference(self._data.get("reference"))

    @property
    def id(self) -> str:
        return self.reference.id

    @property
    def disabled(self) -> bool:
        return self._data.get("disabled")

    @property
    def disabled_content(self) -> bool:
        return self._data.get("disabledContent")


@enum.unique
class PublishedWorkspaceType(enum.Enum):
    APP_MODE = "APP_MODE"
    ARCHIVE = "ARCHIVE"


@enum.unique
class PublishedWorkspaceUploadStatus(enum.Enum):
    INITIALIZING = "initializing"
    CREATED = "created"
    DELETING = "deleting"


@dataclass
class AppMode:
    model: str


@dataclass
class PublishedWorkspaceDefinition:
    name: str
    tenant_id: str
    size: int
    status: PublishedWorkspaceUploadStatus
    owner_username: str
    created_at: int
    app_mode: Optional[AppMode] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PublishedWorkspaceDefinition:
        return cls(
            name=data["workspaceName"],
            tenant_id=data["tenantId"],
            size=data["size"],
            status=PublishedWorkspaceUploadStatus(data["status"]),
            owner_username=data["ownerUsername"],
            created_at=data["createdAt"],
            app_mode=AppMode(data["appMode"]["model"]) if data.get("appMode") else None,
        )


@dataclass
class PublishedWorkspaceRequester:
    id: str
    username: str

    @classmethod
    def from_dict(cls, userdata: Dict[str, Any]) -> PublishedWorkspaceRequester:
        return cls(id=userdata["id"], username=userdata["username"])


@dataclass
class PublishedWorkspaceACL:
    role_names: List[str]
    group_names: List[str]
    shared_with: List[PublishedWorkspaceRequester]
    requested_by: List[PublishedWorkspaceRequester]

    @classmethod
    def from_dict(cls, acl: Dict[str, Any]) -> PublishedWorkspaceACL:
        return cls(
            role_names=acl["roleNames"],
            group_names=acl["groupNames"],
            shared_with=[
                PublishedWorkspaceRequester.from_dict(requester)
                for requester in acl["sharedWith"]
            ],
            requested_by=[
                PublishedWorkspaceRequester.from_dict(requester)
                for requester in acl["requestedBy"]
            ],
        )


class PublishedWorkspace:
    """Class containing published workspace functionalities."""

    def __init__(
        self,
        id: str,
        definition: PublishedWorkspaceDefinition,
        service: Service,
    ):
        self._id = id
        self._definition = definition
        self._sal = service

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, PublishedWorkspace) and obj._id == self._id

    def __repr__(self) -> str:
        return f"Published Workspace with id '{self._id}'"

    @property
    def definition(self) -> PublishedWorkspaceDefinition:
        """Published workspace definition."""
        return self._definition

    @property
    def name(self) -> str:
        """Get or set the name for the published workspace.

        Example::

            # Get the published workspace name
            name = published_workspace.name

            # Set the published workspace name
            published_workspace.name = 'My workspace'

        """
        return self._definition.name

    @name.setter
    def name(self, workspace_name: str) -> None:
        self._sal.workspace.rename_published_workspace(self._id, workspace_name)
        data = self._sal.workspace.get_published_workspace(self._id)
        self._definition = PublishedWorkspaceDefinition.from_dict(data)

    @property
    def id(self) -> str:
        """Published Workspace id."""
        return self._id

    @property
    def created_at(self) -> int:
        """Published Workspace timestamp."""
        return self._definition.created_at

    def delete(self) -> None:
        """Deletes the published workspace.

        Example::

            published_workspace.delete()

        """
        self._sal.workspace.delete_published_workspace(self._id)

    @Experimental
    def grant_user_access(self, username: str) -> None:
        """Grant access for the published workspace to the requester.

        Args:
            username: Username of the user to grant access rights to.

        Example::

            published_workspace.grant_user_access('sasuke')

        """
        self._sal.workspace.grant_user_access(self._id, username)

    @Experimental
    def revoke_user_access(self, username: str) -> None:
        """Revoke access for the published workspace.

        Args:
            username: Username of the user to revoke access rights from.

        Example::

            published_workspace.revoke_user_access('naruto')

        """
        self._sal.workspace.revoke_user_access(self._id, username)

    @Experimental
    def grant_group_access(self, group_name: Optional[str] = None) -> None:
        """Grant group access for the published workspace.

        Args:
            group_name: Name of the group to grant access rights to. If not
            specified, the workspace is shared with the group the published workspace
            owner belongs to.

        Example::

            published_workspace.grant_group_access('impact-tenant-org1')

        """
        self._sal.workspace.grant_group_access(self._id, group_name)

    @Experimental
    def revoke_group_access(self, group_name: str) -> None:
        """Revoke group access for the published workspace.

        Args:
            group_name: Name of the group to revoke access rights from.

        Example::

            published_workspace.revoke_group_access('impact-tenant-org1')

        """
        self._sal.workspace.revoke_group_access(self._id, group_name)

    @Experimental
    def grant_community_access(self) -> None:
        """Grant community access for the published workspace.

        Example::

            published_workspace.grant_community_access()

        """
        self._sal.workspace.grant_community_access(self._id)

    @Experimental
    def revoke_community_access(self) -> None:
        """Revoke community access for the published workspace.

        Example::

            published_workspace.revoke_community_access()

        """
        self._sal.workspace.revoke_community_access(self._id)

    def _get_latest_local_workspace(self) -> Optional[Workspace]:
        resp = self._sal.workspace.workspaces_get(sharing_id=self._id)
        workspaces = [
            Workspace(item["id"], self._sal) for item in resp["data"]["items"]
        ]
        if not workspaces:
            return None
        if len(workspaces) > 1:
            logger.warning(
                "Multiple local copies of workspace with the same "
                "sharing ID exist. Picking the latest."
            )
            return sorted(
                workspaces,
                key=lambda x: x.definition.received_from.created_at,  # type: ignore
            )[-1]
        return workspaces[0]

    def import_to_userspace(self, update_if_available: bool = False) -> Workspace:
        """Imports a published workspace to userspace.

        Args:
            update_if_available: If true, the workspace is updated with the
            latest copy from the cloud. Default is False.

        Returns:
            The workspace class object.

        Example::
            pw_client = client.get_published_workspaces_client()
            published_workspace = pw_client.find(owner="sasuke", name="A workspace")[0]
            workspace = published_workspace.import_to_userspace()

        """
        local_workspace = self._get_latest_local_workspace()
        if local_workspace:
            logger.info(
                f"Local imports of workspace with sharing ID {self._id} exists."
            )
            local_ws_recieved_from = local_workspace.definition.received_from
            local_ws_created_at = local_ws_recieved_from.created_at  # type: ignore
            if self.created_at != local_ws_created_at:
                if not update_if_available:
                    logger.warning(
                        "A new update is available for the workspace with ID "
                        f'{local_workspace.id}. Set "update_if_available" to True '
                        "if you wish to update the workspace!"
                    )
                    return local_workspace
                logger.info("Updating the workspace to the latest published workspace.")
                updated_workspace = self._import_to_userspace(
                    overwrite_workspace_id=local_workspace.id
                )
                return updated_workspace
            else:
                logger.info(
                    f"Returning the local workspace with ID {local_workspace.id}."
                )
                return local_workspace

        logger.info(
            f"No local imports of workspace with sharing ID {self._id} exist."
            "Importing the published workspace to userspace."
        )
        return self._import_to_userspace()

    def _import_to_userspace(
        self, overwrite_workspace_id: Optional[str] = None
    ) -> Workspace:
        resp = self._sal.workspace.import_from_cloud(self._id, overwrite_workspace_id)
        return WorkspaceImportOperation[Workspace](
            resp["data"]["location"], self._sal, Workspace.from_import_operation
        ).wait()

    @Experimental
    def get_access_control_list(self) -> PublishedWorkspaceACL:
        """Returns the access control list for the published workspace.

        Returns:
            The PublishedWorkspaceACL class object.

        Example::

            pw_client = client.get_published_workspaces_client()
            published_workspace = pw_client.find(owner="sasuke", name="A workspace")[0]
            published_workspace_acl = published_workspace.get_access_control_list()

            published_workspace_shared_with = published_workspace_acl.shared_with
            published_workspace_requested_by = published_workspace_acl.requested_by

        """
        data = self._sal.workspace.get_published_workspace_acl(self.id)
        return PublishedWorkspaceACL.from_dict(data)


class OwnerData:
    def __init__(self, data: Any) -> None:
        self._data = data

    @property
    def username(self) -> str:
        return self._data["username"]

    @property
    def tenant_id(self) -> str:
        return self._data["tenantId"]


class ReceivedFrom:
    def __init__(self, data: Any) -> None:
        self._data = data

    @property
    def sharing_id(self) -> str:
        return self._data["sharingId"]

    @property
    def workspace_name(self) -> str:
        return self._data["workspaceName"]

    @property
    def owner(self) -> OwnerData:
        return OwnerData(self._data["owner"])

    @property
    def created_at(self) -> int:
        return self._data["createdAt"]


class ReceivedFromWorkspace:
    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace
        self._received_from = self._workspace.definition.received_from
        if not self._received_from:
            raise NoAssociatedPublishedWorkspaceError(
                "The workspace has no link to a published workspace."
            )

    @property
    def metadata(self) -> ReceivedFrom:
        """Reference metadata for the published workspace."""
        assert self._received_from
        return self._received_from

    def get_workspace(self) -> Optional[PublishedWorkspace]:
        """Return the published workspace from which the workspace was imported from.
        Returns None if workspace is not linked to any published workspace.

        Returns:
            An PublishedWorkspace class object.

        Example::

            published_ws = workspace.received_from.get_workspace()

        """
        try:
            sharing_id = self.metadata.sharing_id
            data = self._workspace._sal.workspace.get_published_workspace(sharing_id)
        except HTTPError as e:
            logger.warning(
                f"Published workspace with ID: {sharing_id} doesn't exist. Cause{e}"
            )
            return None
        definition = PublishedWorkspaceDefinition.from_dict(data)
        return PublishedWorkspace(
            data["id"], definition=definition, service=self._workspace._sal
        )

    def has_updates(self) -> Optional[bool]:
        """Return True if there are updates available for the published workspace
        corresponding to the local workspace(if any) else False.

        Example::

            has_updates = workspace.received_from.has_updates()

        """
        pw = self.get_workspace()
        if not pw:
            return None
        local_ws_created_at = self.metadata.created_at  # type: ignore
        return pw.created_at != local_ws_created_at

    def _import_to_userspace(self, sharing_id: str) -> Workspace:
        resp = self._workspace._sal.workspace.import_from_cloud(
            sharing_id, self._workspace.id
        )
        return WorkspaceImportOperation[Workspace](
            resp["data"]["location"],
            self._workspace._sal,
            Workspace.from_import_operation,
        ).wait()

    def update_userspace(self) -> Workspace:
        """Returns the workspaces updated from the latest published one.

        Example::

            updated_workspace = workspace.received_from.update_userspace()

        """
        logger.info("Updating the workspace to the latest published workspace.")
        pub_ws = self.get_workspace()
        if not pub_ws:
            raise NoAssociatedPublishedWorkspaceError(
                "No published workspace found that are "
                f"associated with local workspace with ID: {self._workspace.id}"
            )
        return self._import_to_userspace(sharing_id=pub_ws.id)


class WorkspaceDefinition:
    def __init__(self, data: Any) -> None:
        self._data = data

    @property
    def name(self) -> str:
        """Workspace name."""
        return self._data.get("name")

    @property
    def format(self) -> str:
        """Workspace definition format."""
        return self._data.get("format")

    @property
    def description(self) -> str:
        """Workspace description."""
        return self._data.get("description")

    @property
    def created_by(self) -> str:
        """User ID of the workspace creator."""
        return self._data.get("createdBy")

    @property
    def default_project_id(self) -> str:
        """Project ID of the default workspace project."""
        return self._data.get("defaultProjectId")

    @property
    def received_from(self) -> Optional[ReceivedFrom]:
        """Received from information for the workspace, if imported from cloud."""
        return (
            ReceivedFrom(self._data.get("receivedFrom"))
            if self._data.get("receivedFrom")
            else None
        )

    @property
    def projects(self) -> List[ProjectEntry]:
        """List of workspace projects."""
        projects = self._data.get("projects", [])
        return [ProjectEntry(project) for project in projects]

    @property
    def dependencies(self) -> List[ProjectEntry]:
        """List of workspace dependencies."""
        dependencies = self._data.get("dependencies", [])
        return [ProjectEntry(dependency) for dependency in dependencies]

    def to_file(self, path: str) -> str:
        """Writes the workspace definition as a JSON file.

        Args:
            path: The path of the folder to store the file at.

        Returns:
            The file path of the created JSON file.

        Example::

            file = workspace.to_file('/home/workspace/definition')

        """
        os.makedirs(path, exist_ok=True)
        definition_path = os.path.join(path, self.name + ".json")
        with open(definition_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)
        return definition_path

    @classmethod
    def from_file(cls, path: str) -> WorkspaceDefinition:
        """Constructs WorkspaceDefinition class from JSON file.

        Args:
            path: The path of the JSON file.

        Returns:
            The WorkspaceDefinition class object.

        Example::

            definition = workspace.from_file('/home/definition.json')

        """
        with open(path) as json_file:
            data = json.load(json_file)
        return cls(data)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the workspace definition as a dict."""
        return self._data


class Workspace(WorkspaceInterface):
    """Class containing Workspace functionalities."""

    def __init__(
        self,
        workspace_id: str,
        service: Service,
    ):
        self._workspace_id = workspace_id
        self._sal = service

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Workspace) and obj._workspace_id == self._workspace_id

    def __repr__(self) -> str:
        return f"Workspace with id '{self._workspace_id}'"

    @property
    def id(self) -> str:
        """Workspace id."""
        return self._workspace_id

    @property
    def size(self) -> float:
        """Workspace size in bytes."""
        return self._sal.workspace.workspace_get(workspace_id=self.id, size_info=True)[
            "sizeInfo"
        ]["total"]

    @property
    def definition(self) -> WorkspaceDefinition:
        """Workspace definition."""
        definition = self._sal.workspace.workspace_get(
            workspace_id=self.id, size_info=False
        )["definition"]
        return WorkspaceDefinition(definition)

    @property
    def name(self) -> str:
        """Workspace name."""
        return self.definition.name

    def rename(self, new_name: str) -> None:
        """Renames a workspace.

        Args:
            name: The new name for the workspace.

        Example::

            workspace.rename('renamed workspace')

        """
        workspace_data = self._sal.workspace.workspace_get(
            workspace_id=self.id, size_info=False
        )
        workspace_data["definition"]["name"] = new_name
        self._sal.workspace.update_workspace(self.id, workspace_data)

    def get_custom_function(self, name: str) -> CustomFunction:
        """Returns a CustomFunction class object.

        Args:
            name: The name of the custom function.

        Returns:
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
            path_to_result: The path for the result file to be imported.
            label: The label of the result file. Default: None.
            description: The description of the result file. Default: None.

        Example::

            workspace.upload_result('A.mat')
            workspace.upload_result('B.mat', label = "result_for_PID.mat",
            description = "This is a result file for PID controller")

        """
        resp = self._sal.external_result.result_upload(
            self._workspace_id, path_to_result, label=label, description=description
        )
        return ExternalResultImportOperation[ExternalResult](
            resp["data"]["location"], self._sal, ExternalResult.from_operation
        )

    def export(
        self,
        publish: bool = False,
        class_path: Optional[str] = None,
        access: Optional[AccessSettings] = None,
    ) -> WorkspaceExportOperation:
        """Exports the workspace as a binary compressed archive. Similar to
        :obj:`~modelon.impact.client.entities.workspace.Workspace.download`, but gives
        more control for getting the workspace async. Returns an
        modelon.impact.client.operations.workspace.exports .WorkspaceExportOperation
        class object. The binary archive is stored to cloud storage if the publish
        argument is set to True.

        Args:
            publish: To export the workspace and save it to cloud storage.
            class_path: The Modelica class path of the model. If specified,
                the workspace is exported in app mode.
            access: The access control settings for the workspace.

        Returns:
            An WorkspaceExportOperation class object.

        Example::

            path = workspace.export().wait().download_as('/home/workspace.zip')

            # Publish a workspace
            workspace.export(publish=True,
                class_path='Modelica.Blocks.Examples.PID_Controller').wait()

            # Publish a workspace without sharing with own tenant
            from modelon.impact.client import AccessSettings

            workspace.export(
                publish=True,
                class_path='Modelica.Blocks.Examples.PID_Controller',
                access=AccessSettings(share_with_own_tenant=False)
            ).wait()

        """
        if access:
            access_settings = {"shareWithOwnTenant": access.share_with_own_tenant}
        else:
            access_settings = None
        resp = self._sal.workspace.workspace_export_setup(
            self._workspace_id,
            publish,
            class_path,
            access_settings,
        )
        return WorkspaceExportOperation[Workspace](
            resp["data"]["location"], self._sal, Export.from_operation
        )

    def download(self, path: str) -> str:
        """Downloads the workspace as a binary compressed archive. Returns the local
        path to the downloaded workspace archive. Similar to
        :obj:`~modelon.impact.client.entities.workspace.Workspace.export`, but does the
        entire setup and download in one go.

        Args:

            path: The local path to store the downloaded workspace.

        Returns:
            Local path to the downloaded workspace archive.

        Example::

            workspace.download(path)

        """
        ws_path = os.path.join(path, self._workspace_id + ".zip")
        ops = self.export().wait()
        return ops.download_as(ws_path)

    def get_model(self, class_name: str, project: Optional[Project] = None) -> Model:
        """Returns a Model class object.

        Args:
            class_name: The Modelica class path of the model.
            project: Project class object

        Returns:
            Model class object.

        Example::

            workspace.get_model(class_name)

        """
        project = project or self.get_default_project()
        return Model(class_name, self._workspace_id, project.id, self._sal)

    def get_fmus(self) -> List[ModelExecutable]:
        """Returns a list of ModelExecutable class objects.

        Returns:
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
            ModelExecutable class object.

        Example::

            workspace.get_fmu(fmu_id)

        """
        resp = self._sal.workspace.fmu_get(self._workspace_id, fmu_id)
        return ModelExecutable(self._workspace_id, resp["id"], self._sal, resp)

    def get_experiments(self, class_path: Optional[str] = None) -> List[Experiment]:
        """Returns a list of Experiment class objects.

        Parameters:

            class_path --
                The modelica class path. If given, only the experiments
                generated for model with the specified class path
                are returned.

        Returns:
            List of Experiment class objects.

        Example::

            workspace.get_experiments()

        """
        resp = self._sal.workspace.experiments_get(self._workspace_id, class_path)
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
            definition: A parametrized experiment definition class of type
                SimpleModelicaExperimentDefinition or SimpleFMUExperimentDefinition.
            user_data:
                Optional dictionary object with custom data to attach to the experiment.

        Returns:
            Experiment class object.

        Example::

            workspace.create_experiment(definition)

        """
        if isinstance(
            definition,
            BaseExperimentDefinition,
        ):
            definition_as_dict = definition.to_dict()
        elif isinstance(definition, dict):
            definition_as_dict = definition
        else:
            raise TypeError(
                "Definition object must either be a dictionary or an instance of either"
                " SimpleModelicaExperimentDefinition or SimpleFMUExperimentDefinition"
                " class!"
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
        """Executes an experiment.

        Args:
            definition:
                An experiment definition class instance of
                SimpleFMUExperimentDefinition
                or SimpleModelicaExperimentDefinition
                or a dictionary object containing the definition.
            user_data:
                Optional dictionary object with custom data to attach to the experiment.


        Returns:
            An ExperimentOperation class object.

        Example::

            experiment_ops = workspace.execute(definition)
            experiment_ops.cancel()
            experiment_ops.status
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

        Args:
            vcs_info: If True, the versioning details are returned for the
            project(if under version control).
            include_disabled: If True, projects disabled in the workspace
            are also listed.

        Returns:
            A list of Project class objects.

        Example::

            projects = workspace.get_projects()

        """
        resp = self._sal.workspace.projects_get(
            self._workspace_id, vcs_info=vcs_info, include_disabled=include_disabled
        )
        projects = [
            Project(
                item["id"],
                item["projectType"],
                item["storageLocation"],
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

        Args:
            vcs_info: If True, the versioning details are returned for the
            project(if under version control).
            include_disabled: If True, projects disabled in the workspace
            are also listed.

        Returns:
            A list of Project class object.

        Example::

            dependencies = workspace.get_dependencies()

        """
        resp = self._sal.workspace.dependencies_get(
            self._workspace_id, vcs_info, include_disabled
        )
        return [
            Project(
                item["id"],
                item["projectType"],
                item["storageLocation"],
                VcsUri.from_dict(item["vcsUri"]) if item.get("vcsUri") else None,
                self._sal,
            )
            for item in resp["data"]["items"]
        ]

    def create_project(self, name: str) -> Project:
        """Creates a new project in the workspace.

        Returns:
            A Project class object.

        Example::

            project = workspace.create_project("test")

        """
        resp = self._sal.workspace.project_create(self._workspace_id, name)
        return Project(
            resp["id"],
            resp["projectType"],
            resp["storageLocation"],
            VcsUri.from_dict(resp["vcsUri"]) if resp.get("vcsUri") else None,
            self._sal,
        )

    def get_default_project(self) -> Project:
        """Return the default project for a workspace.

        Returns:
            An Project class object.

        Example::

            project = workspace.get_default_project()

        """
        default_project_id = self.definition.default_project_id
        if not default_project_id:
            raise ValueError(
                f"No default project exists for the workspace {self._workspace_id}!"
            )
        resp = self._sal.project.project_get(
            default_project_id,
            vcs_info=True,
            size_info=False,
        )
        return Project(
            resp["id"],
            resp["projectType"],
            resp["storageLocation"],
            VcsUri.from_dict(resp["vcsUri"]) if resp.get("vcsUri") else None,
            self._sal,
        )

    def get_shared_definition(self, strict: bool = False) -> WorkspaceDefinition:
        """Return the shared definition for a workspace.

        Args:
            strict: If True, the version control URIs for workspace projects and
                dependencies are to specific commits or not.

        Returns:
            An WorkspaceDefinition class object.

        Example::

            definition = workspace.get_shared_definition()

        """
        return WorkspaceDefinition(
            self._sal.workspace.shared_definition_get(
                self._workspace_id, strict=strict
            )["definition"]
        )

    def import_project_from_zip(self, path_to_project: str) -> ProjectImportOperation:
        """Imports a Project from a compressed(.zip) project file and adds it to the
        workspace. Returns the project class object.

        Args:
            path_to_project: The path for the compressed project(.zip) to be uploaded.

        Returns:
            A ProjectImportOperation class object.

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
        """Imports a Project dependency from a compressed(.zip) project file and adds it
        to the workspace. Returns the project class object.

        Args:
            path_to_dependency: The path for the compressed project(.zip) to be
            uploaded.

        Returns:
            An ProjectImportOperation class object.

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

    @property
    def received_from(self) -> ReceivedFromWorkspace:
        """Returns an instance of ReceivedFromWorkspace class."""
        return ReceivedFromWorkspace(self)

    def get_published_workspace(
        self, model_name: Optional[str] = None
    ) -> Optional[PublishedWorkspace]:
        """Returns the published workspace with the name matching this workspace.

        Args:
            model_name: Class path of the Modelica model. If specified,
             an app mode published workspace corresponding to the local workspace
             is returned(if it exists).

        Returns:
            An PublishedWorkspace class object.

        Example::

            published_ws = workspace.get_published_workspace()

        """
        recieved_from = self.definition.received_from
        if recieved_from:
            raise RemotePublishedWorkspaceLinkError(
                "This workspace is imported from published workspace with ID:"
                f"{recieved_from.sharing_id}. Use received_from.get_workspace()"
                " to retrieve the information"
            )
        user = self._sal.users.get_me()["data"]
        published_workspaces = self._sal.workspace.get_published_workspaces(
            name=self.name,
            owner_username=user["username"],
            type=PublishedWorkspaceType.APP_MODE.value
            if model_name
            else PublishedWorkspaceType.ARCHIVE.value,
        )["data"]["items"]
        if model_name:
            published_workspaces = [
                pw
                for pw in published_workspaces
                if pw.get("appMode", {}).get("model") == model_name
            ]
        if not published_workspaces:
            logger.warning(
                "No published workspace corresponding to the local workspace with"
                f" ID: {self.id} exist!"
            )
            return None
        return PublishedWorkspace(
            published_workspaces[0]["id"],
            definition=PublishedWorkspaceDefinition.from_dict(published_workspaces[0]),
            service=self._sal,
        )

    def get_modelica_resource_uri(
        self, library: str, resource_path: str
    ) -> ModelicaResourceURI:
        """Returns a ModelicaResourceURI class.

        Returns:
            The ModelicaResourceURI class object.

        Example::

            modelica_resource_ref = workspace.get_modelica_resource_uri(
                library,
                resource_path
            )

        """
        return ModelicaResourceURI(library=library, resource_path=resource_path)
