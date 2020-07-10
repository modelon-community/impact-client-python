import sys
import logging
import requests
import urllib.parse
import modelon.impact.client.sal.exceptions as exceptions


logger = logging.getLogger(__name__)


class Service:
    def __init__(self, uri, context=None, check_return=True):
        self._base_uri = uri
        self._http_client = HTTPClient(context)
        self.workspace = WorkspaceService(self._base_uri, self._http_client)
        self.model_executable = ModelExecutableService(
            self._base_uri, self._http_client
        )
        self.experiment = ExperimentService(self._base_uri, self._http_client)
        self.custom_function = CustomFunctionService(self._base_uri, self._http_client)

    def api_get_metadata(self):
        url = (self._base_uri / "api/").resolve()
        return self._http_client.get_json(url)


class WorkspaceService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def workspaces_create(self, name):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.post_json(url, body={"new": {"name": name}})

    def workspaces_delete(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        self._http_client.delete_json(url)

    def workspaces_get_all(self):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.get_json(url)

    def workspaces_get(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        return self._http_client.get_json(url)

    def library_import(self, workspace_id, path_to_lib):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/libraries").resolve()
        with open(path_to_lib, "rb") as f:
            return self._http_client.post_json(url, files={"file": f})

    def workspaces_upload(self, path_to_workspace):
        url = (self._base_uri / "api/workspaces").resolve()
        with open(path_to_workspace, "rb") as f:
            return self._http_client.post_json(url, files={"file": f})

    def workspaces_get_export_id(self, workspace_id, options):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/exports").resolve()
        return self._http_client.post_json(url, body=options)["export_id"]

    def workspaces_download(self, workspace_id, options):
        export_id = self.workspaces_get_export_id(workspace_id, options)
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/exports/{export_id}"
        ).resolve()
        return self._http_client.get_zip(url)

    def workspace_lock(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/lock").resolve()
        self._http_client.post_json_no_response_body(url)

    def workspace_unlock(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/lock").resolve()
        self._http_client.delete_json(url)

    def workspace_clone(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/clone").resolve()
        return self._http_client.post_json(url)

    def fmu_get_all(self, workspace_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables"
        ).resolve()
        return self._http_client.get_json(url)

    def fmu_get(self, workspace_id, fmu_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
        ).resolve()
        return self._http_client.get_json(url)

    def ss_fmu_meta_get(self, workspace_id, fmu_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
            "/steady-state-metadata"
        ).resolve()
        return self._http_client.get_json(url)

    def experiment_get_all(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        return self._http_client.get_json(url)

    def experiment_get(self, workspace_id, experiment_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}"
        ).resolve()
        return self._http_client.get_json(url)

    def setup_experiment(self, workspace_id, spec):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        return self._http_client.post_json(url, body=spec)["experiment_id"]

    def execute_experiment(self, workspace_id, exp_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{exp_id}/execution"
        ).resolve()
        self._http_client.post_json_no_response_body(url)
        return exp_id


class ModelExecutableService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def setup_fmu(self, workspace_id, options):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables"
        ).resolve()
        return self._http_client.post_json(url, body=options)["id"]

    def compile_model(self, workspace_id, options):
        fmuId = self.setup_fmu(workspace_id, options)
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmuId}/compilation"
        ).resolve()
        self._http_client.post_json_no_response_body(url)
        return fmuId

    def compile_log(self, workspace_id, fmuId):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmuId}/compilation/log"
        ).resolve()
        return self._http_client.get_json(url)

    def compile_status(self, workspace_id, fmu_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation"
        ).resolve()
        return self._http_client.get_json(url)

    def compile_cancel(self, workspace_id, fmu_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation"
        ).resolve()
        return self._http_client.delete_json(url)

    def settable_parameters_get(self, workspace_id, fmu_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/"
            "settable-parameters"
        ).resolve()
        return self._http_client.get_json(url)


class ExperimentService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def execute_status(self, workspace_id, experiment_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/execution"
        ).resolve()
        return self._http_client.get_json(url)

    def execute_cancel(self, workspace_id, experiment_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/execution"
        ).resolve()
        return self._http_client.delete_json(url)

    def result_variables_get(self, workspace_id, experiment_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/variables"
        ).resolve()
        return self._http_client.get_json(url)

    def trajectories_get(self, workspace_id, experiment_id, variables):
        body = {"variable_names": variables}
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/trajectories"
        ).resolve()
        return self._http_client.post_json(url, body=body)


class CustomFunctionService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def execution_options_get(self, workspace_id, custom_function):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/custom-functions/{custom_function}"
            "/options"
        ).resolve()
        return self._http_client.get_json(url)

    def execution_options_set(self, workspace_id, custom_function, options):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/custom-functions/{custom_function}"
            "/options"
        ).resolve()
        self._http_client.post_json_no_response_body(url, body=options)

    def execution_options_delete(self, workspace_id, custom_function, options):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/custom-functions/{custom_function}"
            "/options"
        ).resolve()
        self._http_client.delete_json(url, body=options)


class HTTPClient:
    def __init__(self, context=None):
        self._context = context if context else Context()

    def get_json(self, url):
        request = RequestJSON(self._context, "GET", url)
        return request.execute().data

    def get_zip(self, url):
        request = RequestZip(self._context, "GET", url)
        return request.execute().data

    def post_json(self, url, body=None, files=None):
        request = RequestJSON(self._context, "POST", url, body, files)
        return request.execute().data

    def post_json_no_response_body(self, url, body=None):
        RequestJSON(self._context, "POST", url, body).execute()

    def delete_json(self, url, body=None):
        RequestJSON(self._context, "DELETE", url, body).execute()


class URI:
    def __init__(self, content):
        # If running on Windows you can get a lot of overhead using 'localhost'
        if sys.platform.startswith("win32") and content.startswith("http://localhost:"):
            content = content.replace("http://localhost:", "http://127.0.0.1:")

        self.content = content

    def resolve(self, **kwargs):
        return self.content.format(**kwargs)

    def _with_path(self, path):
        return URI(urllib.parse.urljoin(self.content + "/", path))

    def __floordiv__(self, other):
        return self._with_path(other)

    def __truediv__(self, other):
        return self._with_path(other)


class Request:
    def __init__(self, context, method, url, request_type, body=None, files=None):
        self.context = context
        self.method = method
        self.url = url
        self.body = body
        self.files = files
        self.request_type = request_type

    def execute(self, check_return=True):
        try:
            if self.method == "POST":
                logger.debug("POST with JSON body: {}".format(self.body))
                resp = self.context.session.post(
                    self.url, json=self.body, files=self.files
                )
            elif self.method == "GET":
                resp = self.context.session.get(self.url)
            elif self.method == "DELETE":
                resp = self.context.session.delete(self.url, json=self.body)
            else:
                raise NotImplementedError()
        except requests.exceptions.RequestException as exce:
            raise exceptions.CommunicationError(
                "Communication when doing a request failed"
            ) from exce

        resp = self.request_type(resp)
        if check_return and not resp.ok:
            raise exceptions.HTTPError(resp.error.message)

        return resp


class RequestJSON(Request):
    def __init__(self, context, method, url, body=None, files=None):
        super().__init__(context, method, url, JSONResponse, body, files)


class RequestZip(Request):
    def __init__(self, context, method, url, body=None, files=None):
        super().__init__(context, method, url, ZIPResponse, body, files)


class Context:
    def __init__(self):
        self.session = requests.Session()


class Response:
    def __init__(self, resp_obj):
        self._resp_obj = resp_obj

    def _is_json(self):
        return "application/json" in self._resp_obj.headers.get("content-type")

    @property
    def status_code(self):
        return self._resp_obj.status_code

    @property
    def ok(self):
        return self._resp_obj.ok

    @property
    def error(self):
        if self._resp_obj.ok:
            raise ValueError("This request was successfull!")

        if not self._is_json():
            raise exceptions.ErrorBodyIsNotJSONError(
                f"Error response was not JSON: {self._resp_obj.content}"
            )

        json = self._resp_obj.json()
        if "error" not in json:
            raise exceptions.ErrorJSONInvalidFormatError(
                f"Error response JSON format unknown: {self._resp_obj.content}"
            )

        error = json["error"]
        return ResponseError(error["message"], error["code"])


class JSONResponse(Response):
    def __init__(self, resp_obj):
        super().__init__(resp_obj)

    @property
    def data(self):
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message)

        if not self._is_json():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected JSON"
            )

        return self._resp_obj.json()


class ZIPResponse(Response):
    def __init__(self, resp_obj):
        super().__init__(resp_obj)

    def _is_zip(self):
        return "application/zip" in self._resp_obj.headers.get("content-type")

    @property
    def data(self):
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message)

        if not self._is_zip():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected a Binary "
                "compressed archive"
            )

        return self._resp_obj.content


class ResponseError:
    def __init__(self, message, code):
        self.message = message
        self.code = code
