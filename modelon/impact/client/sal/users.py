"""Users service module"""
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class UsersService:
    def __init__(self, uri: URI, HTTPClient: HTTPClient):
        self._base_uri = uri
        self._http_client = HTTPClient

    def get_me(self):
        url = (self._base_uri / "api/users/me").resolve()
        return self._http_client.get_json(url)
