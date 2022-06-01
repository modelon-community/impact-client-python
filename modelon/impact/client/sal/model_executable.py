"""Model executable service module"""
from typing import Any, Dict, Tuple
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class ModelExecutableService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def fmu_setup(
        self, workspace_id: str, options: Dict[str, Any], get_cached: bool
    ) -> Tuple[str, Dict[str, Any]]:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables"
            f"?getCached={'true' if get_cached else 'false'}"
        ).resolve()
        resp = self._http_client.post_json(url, body=options)
        return resp["id"], resp["parameters"]

    def compile_model(self, workspace_id, fmu_id: str) -> str:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation"
        ).resolve()
        self._http_client.post_json_no_response_body(url)
        return fmu_id

    def compile_log(self, workspace_id: str, fmu_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation/"
            "log"
        ).resolve()
        return self._http_client.get_text(url)

    def fmu_delete(self, workspace_id: str, fmu_id: str):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
        ).resolve()
        self._http_client.delete_json(url)

    def compile_status(self, workspace_id: str, fmu_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation"
        ).resolve()
        return self._http_client.get_json(url)

    def compile_cancel(self, workspace_id: str, fmu_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/compilation"
        ).resolve()
        return self._http_client.delete_json(url)

    def settable_parameters_get(self, workspace_id: str, fmu_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/"
            "settable-parameters"
        ).resolve()
        return self._http_client.get_json(url)

    def ss_fmu_metadata_get(
        self, workspace_id: str, fmu_id: str, parameter_state: Dict[str, Any]
    ):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
            "/steady-state-metadata"
        ).resolve()
        return self._http_client.post_json(url, body=parameter_state)
