"""Service class."""
import inspect
import logging
from typing import Optional, Union, Dict, Any, Callable

from modelon.impact.client.sal import exceptions
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.sal.project import ProjectService
from modelon.impact.client.sal.custom_function import CustomFunctionService
from modelon.impact.client.sal.model_executable import ModelExecutableService
from modelon.impact.client.sal.experiment import ExperimentService
from modelon.impact.client.sal.external_result import ExternalResultService
from modelon.impact.client.sal.users import UsersService
from modelon.impact.client.sal.exports import ExportService
from modelon.impact.client.sal.imports import ImportService
from modelon.impact.client.sal.context import Context
from modelon.impact.client.sal.uri import URI
from modelon.impact.client.jupyterhub.sal import JupyterContext

logger = logging.getLogger(__name__)


def _decorate_all_methods(cls: Any, decorator: Callable) -> Any:
    for method_name, method in inspect.getmembers(cls, lambda x: inspect.ismethod(x)):
        setattr(cls, method_name, decorator(method))

    return cls


class Service:
    _JUPYTERHUB_VERSION_HEADER = 'x-jupyterhub-version'

    def __init__(
        self, uri: URI, context: Optional[Union[Context, JupyterContext]] = None
    ):
        self._base_uri = uri
        self._http_client = HTTPClient(context)
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

    def add_login_retry_with(self, api_key: Optional[str] = None) -> None:
        def retry_with_login_decorator(func: Callable) -> Callable:
            def wrapped(*args: Any, **kwargs: Any) -> Callable:
                try:
                    return func(*args, **kwargs)
                except exceptions.HTTPError as e:
                    if e.status_code != 401:
                        raise

                    self.api_login(api_key=api_key)
                    return func(*args, **kwargs)

            return wrapped

        self.workspace = _decorate_all_methods(
            self.workspace, retry_with_login_decorator
        )
        self.project = _decorate_all_methods(self.project, retry_with_login_decorator)
        self.model_executable = _decorate_all_methods(
            self.model_executable, retry_with_login_decorator
        )
        self.experiment = _decorate_all_methods(
            self.experiment, retry_with_login_decorator
        )
        self.custom_function = _decorate_all_methods(
            self.custom_function, retry_with_login_decorator
        )
        self.users = _decorate_all_methods(self.users, retry_with_login_decorator)
        self.exports = _decorate_all_methods(self.exports, retry_with_login_decorator)
        self.imports = _decorate_all_methods(self.imports, retry_with_login_decorator)
        self.external_result = _decorate_all_methods(
            self.external_result, retry_with_login_decorator
        )

    def is_jupyterhub_url(self) -> bool:
        url = (self._base_uri / "hub/api/").resolve()

        try:
            response = self._http_client.get_json_response(url)
        except (
            exceptions.CommunicationError,
            exceptions.SSLError,
            exceptions.HTTPError,
            exceptions.ErrorBodyIsNotJSONError,
        ):
            return False
        except Exception:
            logger.warning(
                'Unknown exception trying to determine if URL is to JupyterHub or '
                'Modelon Impact, will assume the URL goes directly to the '
                'Modelon Impact API'
            )
            return False
        return self._JUPYTERHUB_VERSION_HEADER in response.headers

    def api_get_metadata(self) -> Dict[str, Any]:
        url = (self._base_uri / "api/").resolve()
        response = self._http_client.get_json_response(url)

        return response.data

    def api_login(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        login_data = {"secretKey": api_key} if api_key else {}
        url = (self._base_uri / "api/login").resolve()
        return self._http_client.post_json(url, login_data)
