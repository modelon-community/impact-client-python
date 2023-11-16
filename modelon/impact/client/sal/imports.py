"""Import service module."""
from typing import Any, Dict

from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class ImportService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def get_import_status(self, location: str) -> Dict[str, Any]:
        url = (self._base_uri / location).resolve()
        return self._http_client.get_json(url)
