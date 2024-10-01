"""HTTP client class."""
from typing import Any, Dict, Optional

from modelon.impact.client.sal.context import Context
from modelon.impact.client.sal.request import (
    RequestCSV,
    RequestFileStream,
    RequestJSON,
    RequestMatStream,
    RequestOctetStream,
    RequestText,
    RequestXML,
    RequestZip,
)
from modelon.impact.client.sal.response import (
    CSVResponse,
    FileResponse,
    JSONResponse,
    MatStreamResponse,
    OctetStreamResponse,
)


class HTTPClient:
    def __init__(
        self, api_key: Optional[str] = None, context: Optional[Context] = None
    ):
        self._context = context if context else Context()
        if api_key:
            self._context.session.headers["impact-api-key"] = api_key

    def get_json(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.get_json_response(url, headers=headers, params=params).data

    def get_json_response(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        request = RequestJSON(self._context, "GET", url, headers=headers, params=params)
        return request.execute()

    def get_text(self, url: str) -> str:
        request = RequestText(self._context, "GET", url)
        return request.execute().data

    def get_csv(
        self, url: str, headers: Optional[Dict[str, Any]] = None
    ) -> CSVResponse:
        request = RequestCSV(self._context, "GET", url, headers=headers)
        return request.execute()

    def get_xml(self, url: str, headers: Optional[Dict[str, Any]] = None) -> str:
        request = RequestXML(self._context, "GET", url, headers=headers)
        return request.execute().data

    def get_mat(
        self, url: str, headers: Optional[Dict[str, Any]] = None
    ) -> MatStreamResponse:
        request = RequestMatStream(self._context, "GET", url, headers=headers)
        return request.execute()

    def get_octet_response(self, url: str) -> OctetStreamResponse:
        request = RequestOctetStream(self._context, "GET", url)
        return request.execute()

    def get_file_response(self, url: str) -> FileResponse:
        request = RequestFileStream(self._context, "GET", url)
        return request.execute()

    def get_zip(self, url: str) -> bytes:
        request = RequestZip(self._context, "GET", url)
        return request.execute().data

    def post_json(
        self,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        request = RequestJSON(self._context, "POST", url, body, files, headers=headers)
        return request.execute().data

    def post_json_no_response_body(
        self, url: str, body: Optional[Dict[str, Any]] = None
    ) -> None:
        RequestJSON(self._context, "POST", url, body).execute()

    def patch_json_no_response_body(
        self, url: str, body: Optional[Dict[str, Any]] = None
    ) -> None:
        RequestJSON(self._context, "PATCH", url, body).execute()

    def delete_json(self, url: str, body: Optional[Dict[str, Any]] = None) -> None:
        RequestJSON(self._context, "DELETE", url, body).execute()

    def put_json_no_response_body(
        self, url: str, body: Optional[Dict[str, Any]] = None
    ) -> None:
        RequestJSON(self._context, "PUT", url, body).execute()

    def put_json(
        self,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        request = RequestJSON(self._context, "PUT", url, body, headers=headers)
        return request.execute().data
