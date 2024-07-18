"""Workspace service module."""
from typing import Any, Dict, List

from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class WhitelistService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def whitelist_get(self) -> Dict[str, Any]:
        url = (self._base_uri / "api/whitelist").resolve()
        return self._http_client.get_json(url)

    def whitelist_append(self, users: List[str], groups: List[str]) -> None:
        url = (self._base_uri / "api/whitelist").resolve()
        return self._http_client.patch_json_no_response_body(
            url, body={"users": users, "groups": groups}
        )

    def whitelist_remove_user(self, username: str) -> None:
        url = (self._base_uri / f"api/whitelist/users/{username}").resolve()
        self._http_client.delete_json(url)

    def whitelist_remove_group(self, group_name: str) -> None:
        url = (self._base_uri / f"api/whitelist/groups/{group_name}").resolve()
        self._http_client.delete_json(url)
