import sys
import os
import json
import re
import logging
import requests
import urllib.parse
from modelon.impact.client.sal import exceptions


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

    def api_login(self, login_data):
        url = (self._base_uri / "api/login").resolve()
        return self._http_client.post_json(url, login_data)


class WorkspaceService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def workspace_create(self, name):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.post_json(url, body={"new": {"name": name}})

    def workspace_delete(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        self._http_client.delete_json(url)

    def workspaces_get(self):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.get_json(url)

    def workspace_get(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        return self._http_client.get_json(url)

    def library_import(self, workspace_id, path_to_lib):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/libraries").resolve()
        with open(path_to_lib, "rb") as f:
            self._http_client.post_json(url, files={"file": f})

    def fmu_import(
        self,
        workspace_id,
        fmu_path,
        library,
        class_name=None,
        overwrite=False,
        include_patterns=None,
        exclude_patterns=None,
        top_level_inputs=None,
        step_size=0.0,
    ):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/libraries/{library}/models"
        ).resolve()
        default_class_name = ".".join(
            [library, os.path.split(fmu_path)[-1].strip('.fmu')]
        )
        options = {
            "className": class_name if class_name else default_class_name,
            "overwrite": overwrite,
            "stepSize": step_size,
        }

        if include_patterns:
            options["includePatterns"] = include_patterns
        if exclude_patterns:
            options["excludePatterns"] = exclude_patterns
        if top_level_inputs:
            options["topLevelInputs"] = top_level_inputs

        with open(fmu_path, "rb") as f:
            multipart_form_data = {
                'file': f,
                'options': json.dumps(options),
            }
            return self._http_client.post_json(url, files=multipart_form_data)

    def workspace_upload(self, path_to_workspace):
        url = (self._base_uri / "api/workspaces").resolve()
        with open(path_to_workspace, "rb") as f:
            return self._http_client.post_json(url, files={"file": f})

    def result_upload(self, workspace_id, path_to_result, label=None, description=None):
        url = (self._base_uri / "api/uploads/results").resolve()
        options = {
            "context": {"workspaceId": workspace_id},
        }
        if label:
            options["name"] = label
        if description:
            options["description"] = description
        with open(path_to_result, "rb") as f:
            multipart_form_data = {
                'file': f,
                'options': json.dumps(options),
            }
            return self._http_client.post_json(url, files=multipart_form_data)

    def get_result_upload_status(self, upload_id):
        url = (self._base_uri / f"api/uploads/results/{upload_id}").resolve()
        return self._http_client.get_json(url)

    def get_uploaded_result_meta(self, upload_id):
        url = (self._base_uri / f"api/external-result/{upload_id}").resolve()
        return self._http_client.get_json(url)

    def delete_uploaded_result(self, upload_id):
        url = (self._base_uri / f"api/external-result/{upload_id}").resolve()
        return self._http_client.delete_json(url)

    def _workspace_get_export_id(self, workspace_id, options):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/exports").resolve()
        return self._http_client.post_json(url, body=options)["export_id"]

    def workspace_download(self, workspace_id, options):
        export_id = self._workspace_get_export_id(workspace_id, options)
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

    def fmus_get(self, workspace_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables"
        ).resolve()
        return self._http_client.get_json(url)

    def fmu_get(self, workspace_id, fmu_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
        ).resolve()
        return self._http_client.get_json(url)

    def fmu_download(self, workspace_id, fmu_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/binary"
        ).resolve()
        return self._http_client.get_zip(url)

    def experiments_get(self, workspace_id):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        return self._http_client.get_json(
            url, headers={"Accept": "application/vnd.impact.experiment.v2+json"}
        )

    def experiment_get(self, workspace_id, experiment_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}"
        ).resolve()
        return self._http_client.get_json(
            url, headers={"Accept": "application/vnd.impact.experiment.v2+json"}
        )

    def experiment_create(self, workspace_id, definition):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        return self._http_client.post_json(url, body=definition)


class ModelExecutableService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def fmu_setup(self, workspace_id, options, get_cached):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables"
            f"?getCached={'true' if get_cached else 'false'}"
        ).resolve()
        resp = self._http_client.post_json(url, body=options)
        return resp["id"], resp["parameters"]

    def compile_model(self, workspace_id, fmu_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation"
        ).resolve()
        self._http_client.post_json_no_response_body(url)
        return fmu_id

    def compile_log(self, workspace_id, fmu_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation/"
            "log"
        ).resolve()
        return self._http_client.get_text(url)

    def fmu_delete(self, workspace_id, fmu_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
        ).resolve()
        self._http_client.delete_json(url)

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

    def ss_fmu_metadata_get(self, workspace_id, fmu_id, parameter_state):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
            "/steady-state-metadata"
        ).resolve()
        return self._http_client.post_json(url, body=parameter_state)


class ExperimentService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def experiment_execute(self, workspace_id, exp_id, case_ids=None):
        body = {"includeCases": {"ids": case_ids}} if case_ids is not None else None
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{exp_id}/execution"
        ).resolve()
        self._http_client.post_json_no_response_body(url, body=body)
        return exp_id

    def experiment_delete(self, workspace_id, exp_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/experiments/{exp_id}"
        ).resolve()
        self._http_client.delete_json(url)

    def experiment_set_label(self, workspace_id, exp_id, label):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/experiments/{exp_id}"
        ).resolve()
        return self._http_client.put_json_no_response_body(url, body={"label": label})

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

    def cases_get(self, workspace_id, experiment_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases"
        ).resolve()
        return self._http_client.get_json(url)

    def case_get(self, workspace_id, experiment_id, case_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}"
        ).resolve()
        return self._http_client.get_json(url)

    def case_put(self, workspace_id, experiment_id, case_id, case_data):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}"
        ).resolve()
        return self._http_client.put_json(url, body=case_data)

    def case_get_log(self, workspace_id, experiment_id, case_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/log"
        ).resolve()
        return self._http_client.get_text(url)

    def case_result_get(self, workspace_id, experiment_id, case_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/result"
        ).resolve()
        resp = self._http_client.get_octet_response(url)
        return resp.stream, resp.file_name

    def case_trajectories_get(self, workspace_id, experiment_id, case_id, variables):
        body = {"variable_names": variables}
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/trajectories"
        ).resolve()
        return self._http_client.post_json(url, body=body)

    def case_artifact_get(self, workspace_id, experiment_id, case_id, artifact_id):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/custom-artifacts/{artifact_id}"
        ).resolve()
        resp = self._http_client.get_octet_response(url)
        return resp.stream, resp.file_name


class CustomFunctionService:
    def __init__(self, uri, HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def custom_function_get(self, workspace_id, custom_function):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/custom-functions/{custom_function}"
        ).resolve()
        return self._http_client.get_json(url)

    def custom_functions_get(self, workspace_id):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/custom-functions"
        ).resolve()
        return self._http_client.get_json(url)

    def custom_function_default_options_get(self, workspace_id, custom_function):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/custom-functions/{custom_function}"
            "/default-options"
        ).resolve()
        return self._http_client.get_json(url)

    def custom_function_options_get(self, workspace_id, custom_function):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/custom-functions/{custom_function}"
            "/options"
        ).resolve()
        return self._http_client.get_json(url)


class HTTPClient:
    def __init__(self, context=None):
        self._context = context if context else Context()

    def get_json(self, url, headers=None):
        request = RequestJSON(self._context, "GET", url, headers=headers)
        return request.execute().data

    def get_text(self, url):
        request = RequestText(self._context, "GET", url)
        return request.execute().data

    def get_octet_response(self, url):
        request = RequestOctetStream(self._context, "GET", url)
        return request.execute()

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

    def put_json_no_response_body(self, url, body=None):
        RequestJSON(self._context, "PUT", url, body).execute()

    def put_json(self, url, body=None):
        request = RequestJSON(self._context, "PUT", url, body)
        return request.execute().data


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

    def __repr__(self):
        return self.content


class Request:
    def __init__(
        self, context, method, url, request_type, body=None, files=None, headers=None
    ):
        self.context = context
        self.method = method
        self.url = url
        self.body = body
        self.files = files
        self.request_type = request_type
        self.headers = headers

    def execute(self, check_return=True):
        try:
            if self.method == "POST":
                logger.debug("POST with JSON body: {}".format(self.body))
                resp = self.context.session.post(
                    self.url, json=self.body, files=self.files
                )
            elif self.method == "GET":
                resp = self.context.session.get(self.url, headers=self.headers)
            elif self.method == "PUT":
                resp = self.context.session.put(
                    self.url, json=self.body, headers=self.headers
                )
            elif self.method == "DELETE":
                resp = self.context.session.delete(self.url, json=self.body)
            else:
                raise NotImplementedError()
        except requests.exceptions.SSLError as exce:
            raise exceptions.SSLError(
                "SSL error, could not verify connection. Please check that "
                "certificates are setup correctly for the Modelon Impact server"
            ) from exce
        except requests.exceptions.RequestException as exce:
            raise exceptions.CommunicationError(
                "Communication when doing a request failed"
            ) from exce

        resp = self.request_type(resp)
        if check_return and not resp.ok:
            raise exceptions.HTTPError(resp.error.message)

        return resp


class RequestJSON(Request):
    def __init__(self, context, method, url, body=None, files=None, headers=None):
        super().__init__(context, method, url, JSONResponse, body, files, headers)


class RequestZip(Request):
    def __init__(self, context, method, url, body=None, files=None, headers=None):
        super().__init__(context, method, url, ZIPResponse, body, files, headers)


class RequestText(Request):
    def __init__(self, context, method, url, body=None, files=None, headers=None):
        super().__init__(context, method, url, TextResponse, body, files, headers)


class RequestOctetStream(Request):
    def __init__(self, context, method, url, body=None, files=None, headers=None):
        super().__init__(
            context, method, url, OctetStreamResponse, body, files, headers
        )


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


class TextResponse(Response):
    def __init__(self, resp_obj):
        super().__init__(resp_obj)

    def _is_txt(self):
        return "text/plain" in self._resp_obj.headers.get("content-type")

    @property
    def data(self):
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message)

        if not self._is_txt():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected text"
            )

        return self._resp_obj.text


class OctetStreamResponse(Response):
    def __init__(self, resp_obj):
        super().__init__(resp_obj)

    def _is_octet_stream(self):
        return "application/octet-stream" in self._resp_obj.headers.get("content-type")

    @property
    def stream(self):
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message)

        if not self._is_octet_stream():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected octet-stream"
            )

        return self._resp_obj.content

    @property
    def headers(self):
        return self._resp_obj.headers

    @property
    def file_name(self):
        d = self.headers["content-disposition"]
        return re.findall("filename=(.+)", d)[0].strip('"')


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
