"""Project service module"""
import json
from typing import Dict, Any, Optional, Union, List
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

    def project_options_get(self, project_id: str, custom_function: str):
        url = (
            self._base_uri
            / f"api/projects/{project_id}/custom-functions/{custom_function}/options"
        ).resolve()
        return self._http_client.get_json(url)

    def project_default_options_get(self, project_id: str, custom_function: str):
        url = (
            self._base_uri
            / f"api/projects/{project_id}/custom-functions/{custom_function}/"
            "default-options"
        ).resolve()
        return self._http_client.get_json(url)

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

    def fmu_upload(
        self,
        workspace_id: str,
        project_id: str,
        content_id: str,
        fmu_path: str,
        class_name: str,
        overwrite: bool = False,
        include_patterns: Optional[Union[str, List[str]]] = None,
        exclude_patterns: Optional[Union[str, List[str]]] = None,
        top_level_inputs: Optional[Union[str, List[str]]] = None,
        step_size: float = 0.0,
    ):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/projects/{project_id}/content/"
            f"{content_id}/models"
        ).resolve()
        options = {
            "className": class_name,
            "overwrite": overwrite,
            "stepSize": step_size,
        }

        if include_patterns:
            options["includePatterns"] = include_patterns
        if exclude_patterns:
            options["excludePatterns"] = exclude_patterns
        if top_level_inputs:
            options["topLevelInputs"] = top_level_inputs

        with open(fmu_path, "rb") as f:
            multipart_form_data = {
                'file': f,
                'options': json.dumps(options),
            }
            return self._http_client.post_json(url, files=multipart_form_data)
