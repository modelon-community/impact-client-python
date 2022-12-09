"""Export service module"""
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class ExportService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def export_download(self, location):
        url = (self._base_uri / location).resolve()
        return self._http_client.get_zip(url)
