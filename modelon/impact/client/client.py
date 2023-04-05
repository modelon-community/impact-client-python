"""This module provides an entry-point to the client APIs."""
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from semantic_version import SimpleSpec, Version  # type: ignore
import modelon.impact.client.configuration
import modelon.impact.client.sal.service
import modelon.impact.client.sal.exceptions
import modelon.impact.client.jupyterhub
from modelon.impact.client.credential_manager import CredentialManager
from modelon.impact.client.operations.project_import import ProjectImportOperation
from modelon.impact.client.operations.workspace.imports import WorkspaceImportOperation
from modelon.impact.client.entities.project import Project, VcsUri
from modelon.impact.client.entities.workspace import WorkspaceDefinition, Workspace
from modelon.impact.client.operations.workspace.conversion import (
    WorkspaceConversionOperation,
)
from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.context import Context
from modelon.impact.client import exceptions


logger = logging.getLogger(__name__)


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
        return Selection(entry_id=self.entry_id, project=self.projects[index])

    def make_selection_interactive(self) -> Selection:
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
        return [e.make_selection_interactive() for e in self.entries]


class Client:
    """This Class contains methods to authenticate logins, create new
    workspaces and upload or fetch existing workspaces.

    Args:

        url:
            The URL for Modelon Impact client host. Defaults to the value specified
            by env variable 'MODELON_IMPACT_CLIENT_URL' if set else uses the URL
            'http://localhost:8080/'.

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

    Examples::
        from modelon.impact.client import Client

        client = Client(url=impact_url)
        client = Client(url=impact_url, interactive=True)

    """

    _SUPPORTED_VERSION_RANGE = ">=4.0.0-beta.25,<5.0.0"

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
            # running interactively and login was successfuly
            self._credential_manager.write_key_to_file(api_key)

        return api_key

    def get_workspace(self, workspace_id: str) -> Workspace:
        """Returns a Workspace class object.

        Args:

            workspace_id:
                The name of the workspace.

        Returns:

            workspace:
                Workspace class object.

        Example::

            client.get_workspace('my_workspace')

        """
        resp = self._sal.workspace.workspace_get(workspace_id)
        return Workspace(resp["id"], resp["definition"], self._sal)

    def get_workspaces(self) -> List[Workspace]:
        """Returns a list of Workspace class object.

        Returns:

            workspace:
                A list of Workspace class objects.

        Example::

            client.get_workspaces()

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
            workspace_id (str): The ID of the workspace to convert to the latest
            backup_name (Optional[str], optional): If given then a backup will be
            created with this name. Defaults to None.

        Returns:
            WorkspaceConversionOperation: The workspace conversion operation

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

            project_id:
                The id of the project.

        Returns:

            project:
                Project class objects.

        Example::

            client.get_project('hcbhsb11313321')

        """
        resp = self._sal.project.project_get(project_id, vcs_info)
        return Project(
            resp["id"],
            resp["definition"],
            resp["projectType"],
            VcsUri.from_dict(resp["vcsUri"]) if resp.get("vcsUri") else None,
            self._sal,
        )

    def get_projects(self, vcs_info: bool = True) -> List[Project]:
        """Returns a list of project class object.

        Args:

            vcs_info:
                If True, the versioning details are returned for the
                projects under version control.

        Returns:

            project:
                A list of Project class objects.

        Example::

            client.get_projects()

        """
        resp = self._sal.project.projects_get(vcs_info=vcs_info)
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

    def create_workspace(self, workspace_id: str) -> Workspace:
        """Creates and returns a Workspace. Returns a workspace class object.

        Args:

            workspace_id:
                The name of the workspace to create.

        Returns:

            workspace:
                The created workspace class object.

        Example::

            client.create_workspace('my_workspace')

        """
        resp = self._sal.workspace.workspace_create(workspace_id)
        return Workspace(resp["id"], resp["definition"], self._sal)

    def upload_workspace(self, path_to_workspace: str) -> Workspace:
        """Imports a Workspace from a compressed(.zip) workspace file. Returns
        the workspace class object of the imported workspace. Similar to
        :obj:`~modelon.impact.client.Client.import_workspace_from_zip`, but
        does the import in one go.

        Args:

            path_to_workspace:
                The path for the compressed workspace(.zip) to be uploaded.

        Returns:

            workspace:
                Workspace class object.

        Example::

            client.upload_workspace(path_to_workspace)

        """
        return self.import_workspace_from_zip(path_to_workspace).wait()

    def import_workspace_from_zip(
        self, path_to_workspace: str
    ) -> WorkspaceImportOperation:
        """Imports a Workspace from a compressed(.zip) workspace file.
        Similar to
        :obj:`~modelon.impact.client.Client.upload_workspace`,
        but gives more control for getting the workspace async.
        Returns an modelon.impact.client.operations.workspace.imports
        .WorkspaceImportOperation class object.

        Args:

            path_to_workspace:
                The path for the compressed workspace(.zip) to be uploaded.

        Returns:

            WorkspaceImportOperation:
                An modelon.impact.client.operations.workspace.imports.
                WorkspaceImportOperation class object.

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
        resp = self._sal.workspace.import_from_shared_definition(
            {"definition": shared_definition.to_dict()},
            selected_matchings=[selection.to_dict() for selection in selections]
            if selections
            else None,
        )
        return WorkspaceImportOperation[Workspace](
            resp["data"]["location"], self._sal, Workspace.from_import_operation
        )

    def get_project_matchings(
        self, shared_definition: WorkspaceDefinition
    ) -> ProjectMatchings:
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

            path_to_project:
                The path for the compressed project(.zip) to be uploaded.

        Returns:

            ProjectImportOperation:
                An modelon.impact.client.operations.project_import.
                ProjectImportOperation class object.

        Example::

            client.import_project_from_zip(path_to_project).wait()

        """
        resp = self._sal.project.import_from_zip(path_to_project)
        return ProjectImportOperation[Project](
            resp["data"]["location"], self._sal, Project.from_operation
        )
