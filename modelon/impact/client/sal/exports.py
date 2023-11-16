"""Export service module."""
from typing import Any, Dict

from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class ExportService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def export_download(self, location: str) -> bytes:
        url = (self._base_uri / location).resolve()
        return self._http_client.get_zip(url)

    def get_export_status(self, location: str) -> Dict[str, Any]:
        url = (self._base_uri / location).resolve()
        return self._http_client.get_json(url)
