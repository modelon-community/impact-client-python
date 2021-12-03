"""This module provides an entry-point to the client APIs."""
import logging
import modelon.impact.client.configuration
import modelon.impact.client.entities
import modelon.impact.client.exceptions
import modelon.impact.client.sal.service
import modelon.impact.client.sal.exceptions
import modelon.impact.client.credential_manager
import modelon.impact.client.jupyterhub

from semantic_version import SimpleSpec, Version  # type: ignore
from modelon.impact.client import exceptions


logger = logging.getLogger(__name__)


class Client:
    """This Class contains methods to authenticate logins, create new workspaces and
    upload or fetch existing workspaces.

    Parameters:

        url --
            The URL for Modelon Impact client host. Defaults to the value specified
            by env variable 'MODELON_IMPACT_CLIENT_URL' if set else uses the URL
            'http://localhost:8080/'.

        interactive --
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

        credential_manager --
            Help class for managing credentials for the Impact server. Default is None
            and then the default credential manager is used.

        context --
            Request contexts to pass data alongside a HTTP request. Default is None and
            then the default context is used.

    Examples::
        from modelon.impact.client import Client

        client = Client(url=impact_url)
        client = Client(url=impact_url, interactive=True)
    """

    _SUPPORTED_VERSION_RANGE = ">=1.21.0,<2.0.0"

    def __init__(
        self,
        url=None,
        interactive=None,
        credential_manager=None,
        context=None,
        jupyterhub_credential_manager=None,
    ):
        if url is None:
            url = modelon.impact.client.configuration.get_client_url()

        if interactive is None:
            interactive = modelon.impact.client.configuration.get_client_interactive()

        if credential_manager is None:
            credential_manager = (
                modelon.impact.client.credential_manager.CredentialManager()
            )

        self._uri = modelon.impact.client.sal.service.URI(url)
        self._sal = modelon.impact.client.sal.service.Service(self._uri, context)
        self._credential_manager = credential_manager

        try:
            self._validate_compatible_api_version()
        except modelon.impact.client.sal.exceptions.AccessingJupyterHubError:
            self._uri, context = modelon.impact.client.jupyterhub.authorize(
                self._uri, interactive, context, jupyterhub_credential_manager,
            )
            self._sal = modelon.impact.client.sal.service.Service(self._uri, context)
            self._validate_compatible_api_version()

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

    def _validate_compatible_api_version(self):
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

    def _authenticate_against_api(self, interactive, api_key=None):
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

    def get_workspace(self, workspace_id):
        """
        Returns a Workspace class object.

        Parameters:

            workspace_id --
                The name of the workspace.

        Returns:

            workspace --
                Workspace class object.

        Example::

            client.get_workspace('my_workspace')
        """
        resp = self._sal.workspace.workspace_get(workspace_id)
        return modelon.impact.client.entities.Workspace(
            resp["id"],
            self._sal.workspace,
            self._sal.model_executable,
            self._sal.experiment,
            self._sal.custom_function,
        )

    def get_workspaces(self):
        """
        Returns a list of Workspace class object.

        Returns:

            workspace --
                A list of Workspace class objects.

        Example::

            client.get_workspaces()
        """
        resp = self._sal.workspace.workspaces_get()
        return [
            modelon.impact.client.entities.Workspace(
                item["id"],
                self._sal.workspace,
                self._sal.model_executable,
                self._sal.experiment,
                self._sal.custom_function,
            )
            for item in resp["data"]["items"]
        ]

    def create_workspace(self, workspace_id):
        """Creates and returns a Workspace.
        Returns a workspace class object.

        Parameters:

            workspace_id --
                The name of the workspace to create.

        Returns:

            workspace --
                The created workspace class object.

        Example::

            client.create_workspace('my_workspace')
        """
        resp = self._sal.workspace.workspace_create(workspace_id)
        return modelon.impact.client.entities.Workspace(
            resp["id"],
            self._sal.workspace,
            self._sal.model_executable,
            self._sal.experiment,
            self._sal.custom_function,
        )

    def upload_workspace(self, path_to_workspace):
        """Uploads a Workspace
        Returns the workspace class object of the imported workspace.

        Parameters:

            path_to_workspace --
                The path for the compressed workspace(.zip) to be uploaded.

        Returns:

            workspace --
                Workspace class object.

        Example::

            client.upload_workspace(path_to_workspace)
        """
        resp = self._sal.workspace.workspace_upload(path_to_workspace)
        return modelon.impact.client.entities.Workspace(
            resp["id"],
            self._sal.workspace,
            self._sal.model_executable,
            self._sal.experiment,
            self._sal.custom_function,
        )
