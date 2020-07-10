import logging
import modelon.impact.client.entities
import modelon.impact.client.sal.service
from semantic_version import SimpleSpec, Version  # type: ignore
import modelon.impact.client.exceptions as exceptions
import modelon.impact.client.sal.exceptions

logger = logging.getLogger(__name__)

_SUPPORTED_VERSION_RANGE = ">=1.2.1,<2.0.0"


def _sem_ver_check(version, supported_version_range):
    supported_versions = SimpleSpec(supported_version_range)
    if Version(version) not in supported_versions:
        raise exceptions.UnsupportedSemanticVersionError(
            f"Version '{version}' of the HTTP REST API is not supported, must be in the"
            f" range '{supported_version_range}'! Updgrade or downgrade this package to"
            f" a version that supports version '{version}' of the HTTP REST API."
        )


class Client:
    def __init__(self, url=None, context=None):
        if url is None:
            url = "http://localhost:8080/"
            logger.warning("No URL for client was specified, will use: {}".format(url))

        uri = modelon.impact.client.sal.service.URI(url)
        self._sal = modelon.impact.client.sal.service.Service(uri, context)
        try:
            version = self._sal.api_get_metadata()["version"]
        except modelon.impact.client.sal.exceptions.CommunicationError as exce:
            raise modelon.impact.client.sal.exceptions.NoResponseFetchVersionError(
                f"No response from url {url}, please verify that the URL is correct"
            ) from exce
        _sem_ver_check(version, _SUPPORTED_VERSION_RANGE)

    def get_workspace(self, workspace_id):
        resp = self._sal.workspace.workspaces_get(workspace_id)
        return modelon.impact.client.entities.Workspace(
            resp["id"],
            self._sal.workspace,
            self._sal.model_executable,
            self._sal.experiment,
            self._sal.custom_function,
        )

    def get_workspaces(self):
        resp = self._sal.workspace.workspaces_get_all()
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
        resp = self._sal.workspace.workspaces_create(workspace_id)
        return modelon.impact.client.entities.Workspace(
            resp["id"],
            self._sal.workspace,
            self._sal.model_executable,
            self._sal.experiment,
            self._sal.custom_function,
        )

    def upload_workspace(self, workspace_id, path_to_workspace):
        resp = self._sal.workspace.workspaces_upload(workspace_id, path_to_workspace)
        return modelon.impact.client.entities.Workspace(
            resp["id"],
            self._sal.workspace,
            self._sal.model_executable,
            self._sal.experiment,
            self._sal.custom_function,
        )
