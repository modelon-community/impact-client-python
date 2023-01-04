"""Workspace service module."""
from typing import Optional, Dict, Any, List
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


class WorkspaceService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

    def workspace_create(self, name: str) -> Dict[str, Any]:
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.post_json(url, body={"new": {"name": name}})

    def workspace_delete(self, workspace_id: str) -> None:
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        self._http_client.delete_json(url)

    def workspaces_get(self) -> Dict[str, Any]:
        url = (self._base_uri / "api/workspaces").resolve()
        return self._http_client.get_json(url)

    def projects_get(
        self, workspace_id: str, vcs_info: bool, include_disabled: bool
    ) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/projects?vcsInfo={vcs_info}"
            f"&includeDisabled={include_disabled}"
        ).resolve()
        return self._http_client.get_json(url)

    def project_create(self, workspace_id: str, name: str) -> Dict[str, Any]:
        url = (self._base_uri / f"api/workspaces/{workspace_id}/projects").resolve()
        return self._http_client.post_json(url, body={"new": {"name": name}})

    def dependencies_get(
        self, workspace_id: str, vcs_info: bool, include_disabled: bool
    ) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/dependencies?vcsInfo={vcs_info}"
            f"&includeDisabled={include_disabled}"
        ).resolve()
        return self._http_client.get_json(url)

    def workspace_get(self, workspace_id: str) -> Dict[str, Any]:
        url = (self._base_uri / f"api/workspaces/{workspace_id}").resolve()
        return self._http_client.get_json(url)

    def workspace_export_setup(self, workspace_id: str) -> Dict[str, Any]:
        url = (self._base_uri / "api/workspace-exports").resolve()
        body = {"workspaceId": workspace_id}
        return self._http_client.post_json(url, body=body)

    def workspace_conversion_setup(
        self, workspace_id: str, backup_name: Optional[str]
    ) -> Dict[str, Any]:
        url = (self._base_uri / "api/workspace-conversions").resolve()
        backup_data = {'backup': {'name': backup_name}} if backup_name else {}
        body: Dict[str, Any] = {'data': {'workspaceId': workspace_id, **backup_data}}
        return self._http_client.post_json(url, body=body)

    def get_workspace_conversion_status(self, location: str) -> Dict[str, Any]:
        url = (self._base_uri / location).resolve()
        return self._http_client.get_json(url)

    def workspace_clone(self, workspace_id: str) -> Dict[str, Any]:
        url = (self._base_uri / f"api/workspaces/{workspace_id}/clone").resolve()
        return self._http_client.post_json(url)

    def fmus_get(self, workspace_id: str) -> Dict[str, Any]:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables"
        ).resolve()
        return self._http_client.get_json(url)

    def fmu_get(self, workspace_id: str, fmu_id: str) -> Dict[str, Any]:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}"
        ).resolve()
        return self._http_client.get_json(url)

    def fmu_download(self, workspace_id: str, fmu_id: str) -> bytes:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/model-executables/{fmu_id}/binary"
        ).resolve()
        return self._http_client.get_zip(url)

    def experiments_get(self, workspace_id: str) -> Dict[str, Any]:
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        return self._http_client.get_json(
            url, headers={"Accept": "application/vnd.impact.experiment.v2+json"}
        )

    def experiment_get(self, workspace_id: str, experiment_id: str) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
        url = (self._base_uri / f"api/workspaces/{workspace_id}/experiments").resolve()
        body = {
            **definition,
            **({"userData": user_data} if user_data is not None else {}),
        }
        return self._http_client.post_json(url, body=body)

    def shared_definition_get(
        self, workspace_id: str, strict: bool = False
    ) -> Dict[str, Any]:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/"
            f"sharing-definition?strict={'true' if strict else 'false'}"
        ).resolve()
        return self._http_client.get_json(url)

    def import_from_zip(self, path_to_workspace: str) -> Dict[str, Any]:
        url = (self._base_uri / "api/workspace-imports").resolve()
        with open(path_to_workspace, "rb") as f:
            return self._http_client.post_json(url, files={"file": f})

    def import_from_shared_definition(
        self,
        shared_definition: Dict[str, Any],
        selected_matchings: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if selected_matchings:
            shared_definition = {
                **shared_definition,
                **{"selectedMatchings": {"entries": selected_matchings}},
            }
        url = (self._base_uri / "api/workspace-imports").resolve()
        return self._http_client.post_json(url, body=shared_definition)

    def get_project_matchings(
        self, shared_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = (self._base_uri / "api/workspace-imports-matchings").resolve()
        return self._http_client.post_json(url, body=shared_definition)

    def import_project_from_zip(
        self, workspace_id: str, path_to_project: str
    ) -> Dict[str, Any]:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/project-imports"
        ).resolve()
        with open(path_to_project, "rb") as f:
            return self._http_client.post_json(url, files={"file": f})

    def import_dependency_from_zip(
        self, workspace_id: str, path_to_project: str
    ) -> Dict[str, Any]:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/dependency-imports"
        ).resolve()
        with open(path_to_project, "rb") as f:
            return self._http_client.post_json(url, files={"file": f})
