"""Workspace service module"""
import os
import json
from typing import Optional, Union, List, Dict, Any
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class WorkspaceService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def workspace_create(self, name: str):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.post_json(url, body={"new": {"name": name}})

    def workspace_delete(self, workspace_id: str):
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        self._http_client.delete_json(url)

    def workspaces_get(self):
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.get_json(url)

    def workspace_get(self, workspace_id: str):
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        return self._http_client.get_json(url)

    def library_import(self, workspace_id: str, path_to_lib: str):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/libraries").resolve()
        with open(path_to_lib, "rb") as f:
            self._http_client.post_json(url, files={"file": f})

    def fmu_import(
        self,
        workspace_id: str,
        fmu_path: str,
        library: str,
        class_name: Optional[str] = None,
        overwrite: bool = False,
        include_patterns: Optional[Union[str, List[str]]] = None,
        exclude_patterns: Optional[Union[str, List[str]]] = None,
        top_level_inputs: Optional[Union[str, List[str]]] = None,
        step_size: float = 0.0,
    ):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/libraries/{library}/models"
        ).resolve()
        default_class_name = ".".join(
            [library, os.path.split(fmu_path)[-1].strip('.fmu')]
        )
        options = {
            "className": class_name if class_name else default_class_name,
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

    def workspace_upload(self, path_to_workspace: str):
        url = (self._base_uri / "api/workspaces").resolve()
        with open(path_to_workspace, "rb") as f:
            return self._http_client.post_json(url, files={"file": f})

    def result_upload(
        self,
        workspace_id: str,
        path_to_result: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
    ):
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

    def get_result_upload_status(self, upload_id: str):
        url = (self._base_uri / f"api/uploads/results/{upload_id}").resolve()
        return self._http_client.get_json(url)

    def get_uploaded_result_meta(self, upload_id: str):
        url = (self._base_uri / f"api/external-result/{upload_id}").resolve()
        return self._http_client.get_json(url)

    def delete_uploaded_result(self, upload_id: str):
        url = (self._base_uri / f"api/external-result/{upload_id}").resolve()
        return self._http_client.delete_json(url)

    def _workspace_get_export_id(self, workspace_id: str, options: Dict[str, Any]):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/exports").resolve()
        return self._http_client.post_json(url, body=options)["export_id"]

    def workspace_download(self, workspace_id: str, options: Dict[str, Any]):
        export_id = self._workspace_get_export_id(workspace_id, options)
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/exports/{export_id}"
        ).resolve()
        return self._http_client.get_zip(url)

    def workspace_clone(self, workspace_id: str):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/clone").resolve()
        return self._http_client.post_json(url)

    def fmus_get(self, workspace_id: str):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables"
        ).resolve()
        return self._http_client.get_json(url)

    def fmu_get(self, workspace_id: str, fmu_id: str):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
        ).resolve()
        return self._http_client.get_json(url)

    def fmu_download(self, workspace_id: str, fmu_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/binary"
        ).resolve()
        return self._http_client.get_zip(url)

    def experiments_get(self, workspace_id: str):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        return self._http_client.get_json(
            url, headers={"Accept": "application/vnd.impact.experiment.v2+json"}
        )

    def experiment_get(self, workspace_id: str, experiment_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}"
        ).resolve()
        return self._http_client.get_json(
            url, headers={"Accept": "application/vnd.impact.experiment.v2+json"}
        )

    def experiment_create(
        self,
        workspace_id: str,
        definition: Dict[str, Any],
        user_data: Optional[Dict[str, Any]] = None,
    ):
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        body = {
            **definition,
            **({"userData": user_data} if user_data is not None else {}),
        }
        return self._http_client.post_json(url, body=body)
