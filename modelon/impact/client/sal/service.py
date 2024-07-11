"""Service class."""
import logging
from typing import Any, Dict, Optional

from modelon.impact.client.sal import exceptions
from modelon.impact.client.sal.context import Context
from modelon.impact.client.sal.custom_function import CustomFunctionService
from modelon.impact.client.sal.experiment import ExperimentService
from modelon.impact.client.sal.exports import ExportService
from modelon.impact.client.sal.external_result import ExternalResultService
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.imports import ImportService
from modelon.impact.client.sal.model_executable import ModelExecutableService
from modelon.impact.client.sal.project import ProjectService
from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.users import UsersService
from modelon.impact.client.sal.workspace import WorkspaceService

logger = logging.getLogger(__name__)


def _get_impact_base_uri(uri: URI, http_client: HTTPClient) -> URI:
    url = (uri / "hub/api/user").resolve()
    server_url = http_client.get_json(url)["server"]
    return uri / f"{server_url}/impact"


def is_jupyterhub_url(uri: URI, context: Optional[Context] = None) -> bool:
    _JUPYTERHUB_VERSION_HEADER = "x-jupyterhub-version"
    url = (uri / "hub/api/").resolve()

    try:
        http_client = HTTPClient(context=context)
        response = http_client.get_json_response(url)
    except (
        exceptions.CommunicationError,
        exceptions.SSLError,
        exceptions.HTTPError,
        exceptions.ErrorBodyIsNotJSONError,
    ):
        return False
    except Exception:
        logger.warning(
            "Unknown exception trying to determine if URL is to JupyterHub or "
            "Modelon Impact, will assume the URL goes directly to the "
            "Modelon Impact API"
        )
        return False
    return _JUPYTERHUB_VERSION_HEADER in response.headers


class Service:
    def __init__(self, uri: URI, api_key: str, context: Optional[Context] = None):
        self._http_client = HTTPClient(api_key, context)
        self._base_uri = (
            _get_impact_base_uri(uri, self._http_client)
            if is_jupyterhub_url(uri, context)
            else uri
        )
        self.workspace = WorkspaceService(self._base_uri, self._http_client)
        self.project = ProjectService(self._base_uri, self._http_client)
        self.model_executable = ModelExecutableService(
            self._base_uri, self._http_client
        )
        self.experiment = ExperimentService(self._base_uri, self._http_client)
        self.custom_function = CustomFunctionService(self._base_uri, self._http_client)
        self.external_result = ExternalResultService(self._base_uri, self._http_client)
        self.users = UsersService(self._base_uri, self._http_client)
        self.exports = ExportService(self._base_uri, self._http_client)
        self.imports = ImportService(self._base_uri, self._http_client)

    def api_get_metadata(self) -> Dict[str, Any]:
        url = (self._base_uri / "api/").resolve()
        response = self._http_client.get_json_response(url)

        return response.data

    def get_executions(self) -> Dict[str, Any]:
        url = (self._base_uri / "api/executions").resolve()
        resp = self._http_client.get_json_response(url)
        return resp.data
