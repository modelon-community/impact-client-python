"""Service class"""
import inspect
import logging
from typing import Optional

from modelon.impact.client.sal import exceptions
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.sal.project import ProjectService
from modelon.impact.client.sal.custom_function import CustomFunctionService
from modelon.impact.client.sal.model_executable import ModelExecutableService
from modelon.impact.client.sal.experiment import ExperimentService
from modelon.impact.client.sal.users import UsersService
from modelon.impact.client.sal.context import Context
from modelon.impact.client.sal.uri import URI

logger = logging.getLogger(__name__)


def _decorate_all_methods(cls, decorator):
    for method_name, method in inspect.getmembers(cls, lambda x: inspect.ismethod(x)):
        setattr(cls, method_name, decorator(method))

    return cls


class Service:
    _JUPYTERHUB_VERSION_HEADER = 'x-jupyterhub-version'

    def __init__(self, uri: URI, context: Optional[Context] = None):
        self._base_uri = uri
        self._http_client = HTTPClient(context)
        self.workspace = WorkspaceService(self._base_uri, self._http_client)
        self.project = ProjectService(self._base_uri, self._http_client)
        self.model_executable = ModelExecutableService(
            self._base_uri, self._http_client
        )
        self.experiment = ExperimentService(self._base_uri, self._http_client)
        self.custom_function = CustomFunctionService(self._base_uri, self._http_client)
        self.users = UsersService(self._base_uri, self._http_client)

    def add_login_retry_with(self, api_key: Optional[str] = None):
        def retry_with_login_decorator(func):
            def wrapped(*args, **kwargs):
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

    def api_get_metadata(self):
        url = (self._base_uri / "api/").resolve()
        response = self._http_client.get_json_response(url)
        if self._JUPYTERHUB_VERSION_HEADER in response.headers:
            raise exceptions.AccessingJupyterHubError(
                f"API response indicates that the URL '{self._base_uri}' "
                "hosts a JupyterHub."
            )

        return response.data

    def api_login(self, api_key: Optional[str] = None):
        login_data = {"secretKey": api_key} if api_key else {}
        url = (self._base_uri / "api/login").resolve()
        return self._http_client.post_json(url, login_data)
