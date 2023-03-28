"""External result service module."""
import json
from typing import Any, Optional, Dict
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class ExternalResultService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def result_upload(
        self,
        workspace_id: str,
        path_to_result: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = (self._base_uri / "api/uploads/results").resolve()
        options: Dict[str, Any] = {
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

    def get_uploaded_result(self, result_id: str) -> Dict[str, Any]:
        url = (self._base_uri / f"api/external-result/{result_id}").resolve()
        return self._http_client.get_json(url)

    def delete_uploaded_result(self, result_id: str) -> None:
        url = (self._base_uri / f"api/external-result/{result_id}").resolve()
        return self._http_client.delete_json(url)
