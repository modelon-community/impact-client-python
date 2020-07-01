import logging
import modelon.impact.client.entities
import modelon.impact.client.sal.service
from semantic_version import SimpleSpec, Version
import modelon.impact.client.exceptions as exceptions
import modelon.impact.client.sal.exceptions

logger = logging.getLogger(__name__)

_SUPPORTED_VERSION_RANGE = '>=1.1.0,<2.0.0'


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
                f'No response from url {url}, please verify that the URL is correct'
            ) from exce
        _sem_ver_check(version, _SUPPORTED_VERSION_RANGE)

    def get_workspace(self, workspace_id):
        # TODO: should have an endpoint for getting a single workspace
        return modelon.impact.client.entities.Workspace(workspace_id)

    def get_workspaces(self):
        resp = self._sal.workspaces_get_all()
        return [
            modelon.impact.client.entities.Workspace(item["id"])
            for item in resp["data"]["items"]
        ]

    def create_workspace(self, name):
        resp = self._sal.workspaces_create(name)
        return modelon.impact.client.entities.Workspace(resp["id"])
