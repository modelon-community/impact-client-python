"""Request class"""
import logging
from typing import Callable, Dict, Optional, Any
import requests
from modelon.impact.client.sal import exceptions
from modelon.impact.client.sal.response import (
    JSONResponse,
    ZIPResponse,
    TextResponse,
    CSVResponse,
    OctetStreamResponse,
    MatStreamResponse,
)
from modelon.impact.client.sal.context import Context

logger = logging.getLogger(__name__)


class Request:
    def __init__(
        self,
        context: Context,
        method: str,
        url: str,
        request_type: Callable,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        self.context = context
        self.method = method
        self.url = url
        self.body = body
        self.files = files
        self.request_type = request_type
        self.headers = headers

    def execute(self, check_return: bool = True):
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
            raise exceptions.HTTPError(resp.error.message, resp.status_code)

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


class RequestCSV(Request):
    def __init__(self, context, method, url, body=None, files=None, headers=None):
        super().__init__(context, method, url, CSVResponse, body, files, headers)


class RequestOctetStream(Request):
    def __init__(self, context, method, url, body=None, files=None, headers=None):
        super().__init__(
            context, method, url, OctetStreamResponse, body, files, headers
        )


class RequestMatStream(Request):
    def __init__(self, context, method, url, body=None, files=None, headers=None):
        super().__init__(context, method, url, MatStreamResponse, body, files, headers)
