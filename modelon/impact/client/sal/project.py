"""Project service module"""
import json
from typing import Dict, Any
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class ProjectService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def projects_get(self, vcs_info=False):
        url = (self._base_uri / f"api/projects?vcsInfo={vcs_info}").resolve()
        return self._http_client.get_json(url)

    def project_get(self, project_id: str):
        url = (self._base_uri / f"api/projects/{project_id}?vcsInfo=true").resolve()
        return self._http_client.get_json(url)

    def project_delete(self, project_id: str):
        url = (self._base_uri / f"api/projects/{project_id}").resolve()
        self._http_client.delete_json(url)

    def project_put(self, project_id: str, project_data: Dict[str, Any]):
        url = (self._base_uri / f"api/projects/{project_id}").resolve()
        self._http_client.put_json(url, body=project_data)

    def project_content_delete(self, project_id: str, content_id: str):
        url = (
            self._base_uri / f"api/projects/{project_id}/content/{content_id}"
        ).resolve()
        self._http_client.delete_json(url)

    def project_content_upload(
        self, path_to_result: str, project_id: str, content_type: str,
    ):
        url = (self._base_uri / f"/api/projects/{project_id}/content").resolve()
        options = {"contentType": content_type}
        with open(path_to_result, "rb") as f:
            multipart_form_data = {
                'file': f,
                'options': json.dumps(options),
            }
            return self._http_client.post_json(url, files=multipart_form_data)
