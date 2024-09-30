"""Request class."""
import logging
from typing import Any, Callable, Dict, Optional

import requests

from modelon.impact.client.sal import exceptions
from modelon.impact.client.sal.response import (
    CSVResponse,
    FileResponse,
    JSONResponse,
    MatStreamResponse,
    OctetStreamResponse,
    TextResponse,
    XMLResponse,
    ZIPResponse,
)

logger = logging.getLogger(__name__)


class Request:
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        request_type: Callable,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        self.context = context
        self.method = method
        self.url = url
        self.body = body
        self.files = files
        self.request_type = request_type
        self.headers = headers
        self.params = params

    def execute(self, check_return: bool = True) -> Any:
        try:
            extra_headers = self.headers or {}
            headers = {**self.context.session.headers, **extra_headers}
            if self.method == "POST":
                logger.debug("POST with JSON body: {}".format(self.body))
                resp = self.context.session.post(
                    self.url,
                    json=self.body,
                    files=self.files,
                    headers=headers,
                )
            elif self.method == "GET":
                resp = self.context.session.get(
                    self.url,
                    headers=headers,
                    params=self.params,
                )
            elif self.method == "PUT":
                resp = self.context.session.put(
                    self.url,
                    json=self.body,
                    headers=headers,
                )
            elif self.method == "PATCH":
                resp = self.context.session.patch(
                    self.url,
                    json=self.body,
                    headers=headers,
                )
            elif self.method == "DELETE":
                resp = self.context.session.delete(
                    self.url, json=self.body, headers=headers
                )
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
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            context, method, url, JSONResponse, body, files, headers, params
        )


class RequestZip(Request):
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(context, method, url, ZIPResponse, body, files, headers)


class RequestText(Request):
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(context, method, url, TextResponse, body, files, headers)


class RequestXML(Request):
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(context, method, url, XMLResponse, body, files, headers)


class RequestCSV(Request):
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(context, method, url, CSVResponse, body, files, headers)


class RequestOctetStream(Request):
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            context, method, url, OctetStreamResponse, body, files, headers
        )


class RequestMatStream(Request):
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(context, method, url, MatStreamResponse, body, files, headers)


class RequestFileStream(Request):
    def __init__(
        self,
        context: Any,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(context, method, url, FileResponse, body, files, headers)
