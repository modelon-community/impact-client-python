"""This module provides an entry-point to the client APIs."""
from __future__ import annotations
import logging
import enum
from typing import List, Optional, Dict, Any, Union, Iterable
from dataclasses import dataclass
from semantic_version import SimpleSpec, Version  # type: ignore
import modelon.impact.client.configuration
import modelon.impact.client.sal.service
import modelon.impact.client.sal.exceptions
import modelon.impact.client.jupyterhub
from modelon.impact.client.credential_manager import CredentialManager
from modelon.impact.client.operations.project_import import ProjectImportOperation
from modelon.impact.client.operations.workspace.imports import WorkspaceImportOperation
from modelon.impact.client.operations.experiment import ExperimentOperation
from modelon.impact.client.operations.model_executable import ModelExecutableOperation
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.project import Project, VcsUri, ProjectType
from modelon.impact.client.entities.workspace import WorkspaceDefinition, Workspace
from modelon.impact.client.operations.workspace.conversion import (
    WorkspaceConversionOperation,
)
from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.context import Context
from modelon.impact.client import exceptions


logger = logging.getLogger(__name__)


@enum.unique
class ExecutionKind(enum.Enum):
    COMPILATION = 'COMPILATION'
    EXPERIMENT = 'EXPERIMENT'


@enum.unique
class PublishedWorkspaceUploadStatus(enum.Enum):
    INITIALIZING = 'initializing'
    CREATED = 'created'
    DELETING = 'deleting'


@dataclass
class PublishedWorkspace:
    id: str
    workspace_id: str
    workspace_name: str
    group: str
    size: int
    status: PublishedWorkspaceUploadStatus

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PublishedWorkspace:
        return cls(
            id=data['id'],
            workspace_id=data['workspaceId'],
            workspace_name=data['displayName'],
            group=data['group'],
            size=data['size'],
            status=PublishedWorkspaceUploadStatus(data['status']),
        )


@dataclass
class Execution:
    kind: ExecutionKind
    workspace_id: str
    id: str

    @classmethod
    def from_dict(cls, execution: Dict[str, Any]) -> Execution:
        kind = ExecutionKind(execution["kind"])
        id = (
            execution["fmu"]["id"]
            if kind == ExecutionKind.COMPILATION
            else execution["experiment"]["id"]
        )
        return cls(
            kind=kind,
            workspace_id=execution["workspace"]["id"],
            id=id,
        )


@dataclass
class Selection:
    entry_id: str
    project: Project

    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.entry_id, 'project': {'id': self.project.id}}


@dataclass
class ProjectMatching:
    entry_id: str
    vcs_uri: str
    projects: List[Project]

    def get_selection(self, index: int) -> Selection:
        """Returns the selection given the index of the selected project.

        Args:
            index: The index of the selected project

        Returns:
            A Selection class object.

        Example::

            matchings = client.get_project_matchings(imported_workspace_definition)
            selection = matchings.entries[0].get_selection(index=0)

        Example::

            client.import_workspace_from_shared_definition(shared_definition).wait()

        """
        return Selection(entry_id=self.entry_id, project=self.projects[index])

    def make_selection_interactive(self) -> Selection:
        """Returns an interactively chosen Selection object.

        Returns:
            A Selection class object.

        Example::

            matchings = client.get_project_matchings(imported_workspace_definition)
            selection = matchings.entries[0].make_selection_interactive()

        """
        if len(self.projects) == 1:
            print(f"Only one project matches the URI {self.vcs_uri}!")
            selection = self.get_selection(index=0)
            print(
                f"Resolving conflict automatically using project with ID: "
                f"{selection.project.id} for repository with URI: {self.vcs_uri}."
            )
            return selection

        print(
            f"\nThe URI {self.vcs_uri} in the workspace definition matched with"
            " multiple projects during import:"
        )
        for i, project in enumerate(self.projects):
            choice = f"[{i}]:"
            vcs_uri = f"{' ' * len(choice)} Project URI: {str(project.vcs_uri)}"
            print("_" * 60)
            print(f"{choice} Project name: {project.definition.name}")
            print(vcs_uri)

        while True:
            try:
                chosen_index = int(input('\nPlease enter one of the above choices:-'))
                selection = self.get_selection(index=chosen_index)
                break
            except (KeyError, ValueError, IndexError):
                allowed_choices = map(str, range(len(self.projects)))
                print(
                    f"Invalid choice. Please select one of {','.join(allowed_choices)}!"
                )

        print(
            f"Resolving conflict using project with ID: {selection.project.id}"
            f" for repository with URI: {self.vcs_uri}."
        )
        return selection


@dataclass
class ProjectMatchings:
    entries: List[ProjectMatching]

    def make_selections_interactive(self) -> List[Selection]:
        """Returns a list of Selection class objects based on interactive input from
        users. As import will fail if there are multiple possible matchings of local
        projects for a project, this method is used to resolve to an unequivocal
        'selection'. The list of preferred Selection objects could be specified
        during workspace import in the
        :obj:`~modelon.impact.client.Client.import_workspace_from_shared_definition`
        method.

        Returns:
            A a list of Selection class objects.

        Example::

            # Interactive workflow
            matchings = client.get_project_matchings(shared_definition)
            selections = matchings.make_selections_interactive()
            imported_workspace = client.import_workspace_from_shared_definition(
                shared_definition, selections
            ).wait()

        """
        return [e.make_selection_interactive() for e in self.entries]


def _bool_to_str(boolean: bool) -> str:
    return "true" if boolean else "false"


class Client:
    """This Class contains methods to authenticate logins, create new
    workspaces and upload or fetch existing workspaces.

    Args:
        url:
            The URL for Modelon Impact client host. Defaults to the value specified
            by environment variable 'MODELON_IMPACT_CLIENT_URL' if set else uses the URL
            'https://impact.modelon.cloud/'.
        interactive:
            If True the client will prompt for an API key if no other login information
            can be found. An API key entered for this prompt will be saved to disk
            and re-used next time the Client is instantiated. If False no prompt will
            be given if no other login information can be found and login will be done
            as if no API key was given (anonymous login).

            For scripts and notebooks that are running interactively by a user in
            a shell it is recommended to use interactive=True. For scripts or
            applications that are automated or for other reasons won't have a user
            ready to enter an API key it is recommended to use interactive=False.

            Default is False. It is possible to change the default value through
            the environment variable 'MODELON_IMPACT_CLIENT_INTERACTIVE'.
        credential_manager:
            Help class for managing credentials for the Impact server. Default is None
            and then the default credential manager is used.
        context:
            Request contexts to pass data alongside a HTTP request. Default is None and
            then the default context is used.

    Example::

        from modelon.impact.client import Client

        client = Client(url=impact_url)
        client = Client(url=impact_url, interactive=True)

    """

    _SUPPORTED_VERSION_RANGE = ">=4.0.0,<5.0.0"

    def __init__(
        self,
        url: Optional[str] = None,
        interactive: Optional[bool] = None,
        credential_manager: Optional[CredentialManager] = None,
        context: Optional[Context] = None,
        jupyterhub_credential_manager: Optional[CredentialManager] = None,
    ):
        if url is None:
            url = modelon.impact.client.configuration.get_client_url()

        if interactive is None:
            interactive = modelon.impact.client.configuration.get_client_interactive()

        self._uri = URI(url)
        self._sal = modelon.impact.client.sal.service.Service(self._uri, context)

        if self._sal.is_jupyterhub_url():
            logger.info(
                "API response indicates that the URL '%s' hosts a JupyterHub.",
                str(self._uri),
            )
            self._uri, jupyter_context = modelon.impact.client.jupyterhub.authorize(
                self._uri,
                interactive,
                context,
                jupyterhub_credential_manager,
            )
            self._sal = modelon.impact.client.sal.service.Service(
                self._uri, jupyter_context
            )

        self._validate_compatible_api_version()

        if credential_manager is None:
            help_hint = f"can be generated at {self._uri / 'admin/keys'}"
            help_text = f"Enter Modelon Impact API key ({help_hint}):"
            credential_manager = CredentialManager(interactive_help_text=help_text)
        self._credential_manager = credential_manager

        try:
            api_key = self._authenticate_against_api(interactive)
        except modelon.impact.client.sal.exceptions.HTTPError:
            if interactive:
                logger.warning(
                    "The provided Modelon Impact API key is not valid, "
                    "please enter a new key"
                )
                api_key = self._credential_manager.get_key_from_prompt()
                api_key = self._authenticate_against_api(interactive, api_key=api_key)
            else:
                raise

        self._sal.add_login_retry_with(api_key)

        resp = self._sal.users.get_me()
        if 'license' not in resp['data']:
            raise exceptions.NoAssignedLicenseError(
                "No assigned license during login. Either out of floating Deployment "
                "Add-on licenses or your assigned user license could not be validated"
            )

    def _validate_compatible_api_version(self) -> None:
        try:
            version = self._sal.api_get_metadata()["version"]
        except modelon.impact.client.sal.exceptions.CommunicationError as exce:
            raise modelon.impact.client.sal.exceptions.NoResponseFetchVersionError(
                f"No response from url {self._uri}, "
                "please verify that the URL is correct"
            ) from exce

        if Version(version) not in SimpleSpec(self._SUPPORTED_VERSION_RANGE):
            raise exceptions.UnsupportedSemanticVersionError(
                f"Version '{version}' of the HTTP REST API is not supported, "
                f"must be in the range '{self._SUPPORTED_VERSION_RANGE}'! "
                "Updgrade or downgrade this package to a version "
                f"that supports version '{version}' of the HTTP REST API."
            )

    def _authenticate_against_api(
        self, interactive: bool, api_key: Optional[str] = None
    ) -> Optional[str]:
        if not api_key:
            api_key = self._credential_manager.get_key(interactive=interactive)

        if not api_key:
            logger.warning(
                "No Modelon Impact API key could be found, "
                "will log in as anonymous user. Permissions may be limited"
            )

        self._sal.api_login(api_key=api_key)
        if api_key and interactive:
            # Save the api_key for next time if
            # running interactively and login was successfully
            self._credential_manager.write_key_to_file(api_key)

        return api_key

    def get_workspace(self, workspace_id: str) -> Workspace:
        """Returns a Workspace class object.

        Args:
            workspace_id: The ID of the workspace.

        Returns:
            Workspace class object.

        Example::

            client.get_workspace('my_workspace')

        """
        resp = self._sal.workspace.workspace_get(workspace_id, size_info=False)
        return Workspace(resp["id"], resp["definition"], self._sal)

    def get_workspace_by_name(self, workspace_name: str) -> List[Workspace]:
        """Returns a list of Workspace class objects with the given name.

        Args:
            workspace_name: The name of the workspace.

        Returns:
            A list of workspace class objects with the given name.

        Example::

            workspaces = client.get_workspace_by_name('TestWorkspace')

        """
        resp = self._sal.workspace.workspaces_get()
        return [
            Workspace(item["id"], item["definition"], self._sal)
            for item in resp["data"]["items"]
            if item['definition']['name'] == workspace_name
        ]

    def get_workspaces(self) -> List[Workspace]:
        """Returns a list of Workspace class object.

        Returns:
            A list of Workspace class objects.

        Example::

            workspaces = client.get_workspaces()

        """
        resp = self._sal.workspace.workspaces_get()
        return [
            Workspace(item["id"], item["definition"], self._sal)
            for item in resp["data"]["items"]
        ]

    def convert_workspace(
        self, workspace_id: str, backup_name: Optional[str] = None
    ) -> WorkspaceConversionOperation:
        """Converts a workspace of an old version up to the new version the
        server is using.

        Args:
            workspace_id: The ID of the workspace to convert to the latest
            backup_name: If given then a backup will be created with this
            name. Defaults to None.

        Returns:
            The workspace conversion operation

        Example::

            workspace = client.convert_workspace(workspace_id, backup_name='old save')
            .wait()

        """
        resp = self._sal.workspace.workspace_conversion_setup(workspace_id, backup_name)
        return WorkspaceConversionOperation[Workspace](
            resp["data"]["location"], self._sal, Workspace.from_conversion_operation
        )

    def get_project(self, project_id: str, vcs_info: bool = True) -> Project:
        """Returns a project class object.

        Args:
            project_id: The id of the project.
            vcs_info: If True, the versioning details are returned for the
                project(if under version control).

        Returns:
            Project class objects.

        Example::

            client.get_project('hcbhsb11313321')

        """
        resp = self._sal.project.project_get(
            project_id, vcs_info=vcs_info, size_info=False
        )
        return Project(
            resp["id"],
            resp["definition"],
            resp["projectType"],
            VcsUri.from_dict(resp["vcsUri"]) if resp.get("vcsUri") else None,
            self._sal,
        )

    def get_projects(
        self, vcs_info: bool = True, project_type: Optional[ProjectType] = None
    ) -> List[Project]:
        """Returns a list of project class object.

        Args:
            vcs_info: If True, the versioning details are returned for the
                projects under version control.
            type: Used to filter so only projects of a specified projectType
                are returned. If not given all project types are returned.

        Returns:
            A list of Project class objects.

        Example::

            client.get_projects()

        """
        resp = self._sal.project.projects_get(
            vcs_info=vcs_info, project_type=project_type
        )
        return [
            Project(
                item["id"],
                item["definition"],
                item["projectType"],
                VcsUri.from_dict(item["vcsUri"]) if item.get("vcsUri") else None,
                self._sal,
            )
            for item in resp["data"]["items"]
        ]

    def create_workspace(self, workspace_name: str) -> Workspace:
        """Creates and returns a Workspace. Returns a workspace class object.

        Args:
            workspace_name: The name of the workspace to create.

        Returns:
            The created workspace class object.

        Example::

            workspace = client.create_workspace('my_workspace')

        """
        resp = self._sal.workspace.workspace_create(workspace_name)
        return Workspace(resp["id"], resp["definition"], self._sal)

    def upload_workspace(self, path_to_workspace: str) -> Workspace:
        """Imports a Workspace from a compressed(.zip) workspace file. Returns
        the workspace class object of the imported workspace. Similar to
        :obj:`~modelon.impact.client.Client.import_workspace_from_zip`, but
        does the import in one go.

        Args:
            path_to_workspace: The path for the compressed workspace(.zip)
            to be uploaded.

        Returns:
            Workspace class object.

        Example::

            workspace = client.upload_workspace(path_to_workspace)

        """
        return self.import_workspace_from_zip(path_to_workspace).wait()

    def import_workspace_from_zip(
        self, path_to_workspace: str
    ) -> WorkspaceImportOperation:
        """Imports a Workspace from a compressed(.zip) workspace file.
        Similar to
        :obj:`~modelon.impact.client.Client.upload_workspace`,
        but gives more control for getting the workspace async.
        Returns an WorkspaceImportOperation class object.

        Args:
            path_to_workspace: The path for the compressed
            workspace(.zip) to be uploaded.

        Returns:
            A WorkspaceImportOperation class object.

        Example::

            client.import_workspace_from_zip(path_to_workspace).wait()
        """
        resp = self._sal.workspace.import_from_zip(path_to_workspace)
        return WorkspaceImportOperation[Workspace](
            resp["data"]["location"], self._sal, Workspace.from_import_operation
        )

    def import_workspace_from_shared_definition(
        self,
        shared_definition: WorkspaceDefinition,
        selections: Optional[List[Selection]] = None,
    ) -> WorkspaceImportOperation:
        """Imports a Workspace from a shared workspace definition.

        Args:
            shared_definition: The workspace definition for the shared workspace
            selection: Optional list of Selection class objects. This can be specified
            if there are multiple existing projects with the same version control URI.

        Returns:
            A WorkspaceImportOperation class object.

        Example::

            # Import with no conflicts
            client.import_workspace_from_shared_definition(shared_definition).wait()

            # Import with conflicts(Multiple existing projects matches the URI)
            # Programatic workflow to resolve conflicts

            matchings = client.get_project_matchings(shared_definition)
            # Assume the first in list of matchings is good enough:
            selections = [entry.get_selection(index=0) for entry in matchings.entries]
            imported_workspace = client.import_workspace_from_shared_definition(
                shared_definition, selections
            ).wait()

            # Interactive workflow
            matchings = client.get_project_matchings(shared_definition)
            selections = matchings.make_selections_interactive()
            imported_workspace = client.import_workspace_from_shared_definition(
                shared_definition, selections
            ).wait()

        """
        resp = self._sal.workspace.import_from_shared_definition(
            {"definition": shared_definition.to_dict()},
            selected_matchings=[selection.to_dict() for selection in selections]
            if selections
            else None,
        )
        return WorkspaceImportOperation[Workspace](
            resp["data"]["location"], self._sal, Workspace.from_import_operation
        )

    def import_published_workspace(self, sharing_id: str) -> WorkspaceImportOperation:
        """Imports a published workspace via sharing ID.

        Args:
            sharing_id: The ID of the published workspace.

        Returns:
            A WorkspaceImportOperation class object.

        Example::

            client.import_published_workspace("1cdddcdddk545gy").wait()

        """
        resp = self._sal.workspace.import_from_blob(sharing_id)
        return WorkspaceImportOperation[Workspace](
            resp["data"]["location"], self._sal, Workspace.from_import_operation
        )

    def get_project_matchings(
        self, shared_definition: WorkspaceDefinition
    ) -> ProjectMatchings:
        """Returns all projects matchings that would happen during a workspace import.
        As import will fail if there are multiple possible matchings of local projects
        for a project, this method is used to get these matchings which can be
        resolved to an unequivocal 'selection'. Selections are used as (optional) input
        to the
        :obj:`~modelon.impact.client.Client.import_workspace_from_shared_definition`
        method.

        Args:
            shared_definition: The workspace definition for the shared workspace

        Returns:
            A ProjectMatchings class object.

        Example::

            # Import with conflicts(Multiple existing projects matches the URI)
            # Programatic workflow to resolve conflicts
            matchings = client.get_project_matchings(shared_definition)
            # Assume the first in list of matchings is good enough:
            selections = [entry.get_selection(index=0) for entry in matchings.entries]
            imported_workspace = client.import_from_shared_definition(
                shared_definition, selections
            ).wait()

            # Interactive workflow
            matchings = client.get_project_matchings(shared_definition)
            selections = matchings.make_selections_interactive()
            imported_workspace = client.import_workspace_from_shared_definition(
                shared_definition, selections
            ).wait()

        """
        project_matchings = []
        matchings = self._sal.workspace.get_project_matchings(
            {"definition": shared_definition.to_dict()}
        )['data']['vcs']
        for entry in matchings:
            projects = [
                Project(
                    project["id"],
                    project["definition"],
                    project["projectType"],
                    VcsUri.from_dict(project["vcsUri"]),
                    self._sal,
                )
                for project in entry['projects']
            ]

            project_matchings.append(
                ProjectMatching(
                    entry["entryId"], str(VcsUri.from_dict(entry["uri"])), projects
                )
            )
        return ProjectMatchings(project_matchings)

    def import_project_from_zip(self, path_to_project: str) -> ProjectImportOperation:
        """Imports a Project from a compressed(.zip) project file. Returns the
        project class object.

        Args:
            path_to_project: The path for the compressed project(.zip)
            to be uploaded.

        Returns:
            A ProjectImportOperation class object.

        Example::

            client.import_project_from_zip(path_to_project).wait()

        """
        resp = self._sal.project.import_from_zip(path_to_project)
        return ProjectImportOperation[Project](
            resp["data"]["location"], self._sal, Project.from_operation
        )

    def _experiment_operation_from_execution(
        self, execution: Execution
    ) -> ExperimentOperation:
        return ExperimentOperation[Experiment](
            execution.workspace_id,
            execution.id,
            self._sal,
            Experiment.from_operation,
        )

    def _model_executable_operation_from_execution(
        self, execution: Execution
    ) -> ModelExecutableOperation:
        return ModelExecutableOperation[ModelExecutable](
            execution.workspace_id,
            execution.id,
            self._sal,
            ModelExecutable.from_operation,
        )

    def _operation_from_execution(
        self, execution: Execution
    ) -> Optional[Union[ExperimentOperation, ModelExecutableOperation]]:
        if execution.kind == ExecutionKind.EXPERIMENT:
            return self._experiment_operation_from_execution(execution)
        return self._model_executable_operation_from_execution(execution)

    def get_executions(
        self, workspace_id: Optional[str] = None
    ) -> Iterable[Optional[Union[ExperimentOperation, ModelExecutableOperation]]]:
        """Yields running/active executions.

        Args:
            workspace_id: The id of the workspace.

        Yields:
            An ExperimentOperation or a ModelExecutableOperation class.

        Example::

            list(client.get_executions())

        """
        executions = self._sal.get_executions()["data"]["items"]
        for execution in executions:
            execution = Execution.from_dict(execution)
            if workspace_id and execution.workspace_id != workspace_id:
                continue
            yield self._operation_from_execution(execution)

    def get_published_workspaces(
        self,
        *,
        workspace_id: str = "",
        only_latest: bool = False,
        first: int = 0,
        maximum: int = 20,
        has_data: bool = False,
        only_mine: bool = True,
    ) -> List[PublishedWorkspace]:
        """Returns a list of published workspaces. The snapshots could be
        filtered based on the key-worded arguments.

        Args:
            workspace_id: ID of the workspace.
            only_latest: If true, then only returns the latest version for
            each "workspace_id".
            first: Index of first matching resource to return.
            maximum: Maximum number of resources to return.
            has_data: If true, filters with
            status==PublishedWorkspaceUploadStatus.CREATED. If false
            returns everything.
            only_mine: If true, only workspaces published by the logged
            in user are listed.

        Returns:
            A list of published workspace class objects.

        Example::

            client.get_published_workspaces()

        """
        query = {}
        if workspace_id:
            query["workspaceId"] = workspace_id
        if only_latest:
            query["onlyLatest"] = _bool_to_str(only_latest)
        if has_data:
            query["hasData"] = _bool_to_str(has_data)
        if first > 0:
            query["first"] = str(first)
        if maximum >= 0:
            query["max"] = str(maximum)
        if only_mine:
            query["onlyMine"] = _bool_to_str(only_mine)
        query_args = '&'.join(f'{key}={value}' for key, value in query.items())
        data = self._sal.get_published_workspaces(query_args)["data"]["items"]
        return [PublishedWorkspace.from_dict(item) for item in data]

    def get_published_workspace(self, sharing_id: str) -> PublishedWorkspace:
        """Returns the published workspace class object with the given ID.

        Args:
            sharing_id: ID of the published workspace.

        Returns:
            The published workspace class object.

        Example::

            client.get_published_workspace("2h98hciwsniucwincj")

        """
        data = self._sal.get_published_workspace(sharing_id)
        return PublishedWorkspace.from_dict(data)

    def rename_published_workspace(
        self, sharing_id: str, workspace_id: str, workspace_name: str
    ) -> None:
        """Rename the published workspace class object with the given name and
        display name.

        Args:
            sharing_id: ID of the published workspace.
            workspace_id:  Name of the published workspace.
            workspace_name:  Display name of the published workspace

        Example::

            client.rename_published_workspace("2h98hciwsniucwincj", "my workspace",
            "my_workspace")

        """
        self._sal.rename_published_workspace(sharing_id, workspace_id, workspace_name)

    def request_published_workspace_access(self, sharing_id: str) -> None:
        """Send access request for the published workspace with the given ID to
        the creator.

        Args:
            sharing_id: ID of the workspace snapshot.

        Example::

            client.request_snapshot_access("2h98hciwsniucwincj")

        """
        self._sal.request_published_workspace_access(sharing_id)

    def delete_published_workspace(
        self, published_workspace: PublishedWorkspace
    ) -> None:
        """Deletes the published workspace with the given ID.

        Example::

            client.delete_published_workspace("2839283ur8ewjfuehfu")

        """
        self._sal.delete_published_workspace(published_workspace.id)
