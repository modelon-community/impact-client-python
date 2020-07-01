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

    def api_get_metadata(self):
        url = (self._base_uri / "api/").resolve()
        return self._http_client.get_json(url)

    def workspaces_create(self, name):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.post_json(url, {"new": {"name": name}})

    def workspaces_get_all(self):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.get_json(url)


class HTTPClient:
    def __init__(self, context=None):
        self._context = context if context else Context()

    def get_json(self, url):
        request = RequestJSON(self._context, "GET", url)
        return request.execute().data

    def post_json(self, url, body):
        request = RequestJSON(self._context, "POST", url, body)
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


class RequestJSON:
    def __init__(self, context, method, url, body=None):
        self.context = context
        self.method = method
        self.url = url
        self.body = body

    def execute(self, check_return=True):
        try:
            if self.method == "POST":
                logger.debug("POST with JSON body: {}".format(self.body))
                resp = self.context.session.post(self.url, json=self.body)
            elif self.method == "GET":
                resp = self.context.session.get(self.url)
            else:
                raise NotImplementedError()
        except requests.exceptions.RequestException as exce:
            raise exceptions.CommunicationError(
                "Communication when doing a request failed"
            ) from exce

        resp = JSONResponse(resp)
        if check_return and not resp.ok:
            raise exceptions.HTTPError(resp.error.message)

        return resp


class Context:
    def __init__(self):
        self.session = requests.Session()


class JSONResponse:
    def __init__(self, resp_obj):
        self._resp_obj = resp_obj

    def _is_json(self):
        return "application/json" in self._resp_obj.headers.get("content-type")

    @property
    def data(self):
        if not self._resp_obj.ok:
            raise exceptions.HTTPError(self.error.message)

        if not self._is_json():
            raise exceptions.InvalidContentTypeError(
                "Incorrect content type on response, expected JSON"
            )

        return self._resp_obj.json()

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


class ResponseError:
    def __init__(self, message, code):
        self.message = message
        self.code = code
