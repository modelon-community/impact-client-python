"""Modeling service module."""
from typing import Any, Dict, List, Optional

from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.ws import SyncWebSocketClient


class ModelingService:
    def __init__(
        self, uri: URI, http_client: HTTPClient, ws_client: SyncWebSocketClient
    ):
        self._base_uri = uri
        self._http_client = http_client
        self._ws_client = ws_client

    @property
    def id(self) -> str:
        return self._ws_client.session_id

    def get_available_runtime_options(self) -> Dict[str, Any]:
        return self._ws_client.get_json_response("impact/getRuntimeOptions", None)

    def get_available_compiler_options(self) -> Dict[str, Any]:
        return self._ws_client.get_json_response("impact/getCompilerOptions", None)

    def get_projects(self) -> Any:
        return self._ws_client.get_json_response("impact/getProjects", None)

    def get_top_classes(self) -> Dict[str, List[Any]]:
        projects = self.get_projects()
        return {
            project.get("id"): [
                top_class for top_class in project.get("topClasses", [])
            ]
            for project in projects
        }

    def get_top_class_info(self, class_path: str) -> Any:
        return self._ws_client.get_json_response("impact/getTopClassInfo", class_path)

    def get_experiment_definitions(
        self, project_ids: List[str], class_name: str
    ) -> Any:
        params = {"projectIds": project_ids, "fullClassName": class_name}
        return self._ws_client.get_json_response(
            "impact/getExperimentDefinitions", params
        )

    def find_usage(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response("impact/findUsage", modelica_path)

    def get_model_parmeters(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response(
            "impact/getModelParameters", modelica_path
        )

    def create_top_level_package(
        self, project_id: str, package_name: str, libraryToExtend: Optional[str] = None
    ) -> Any:
        params = {
            "projectId": project_id,
            "libraryName": package_name,
            "libraryToExtend": libraryToExtend,
        }
        return self._ws_client.get_json_response("impact/addLibrary", params)

    def duplicate_modelica_model(
        self,
        source_project_id: str,
        old_name: str,
        target_project_id: str,
        new_name: str,
        target_package_name: str,
    ) -> Any:
        params = {
            "sourceProjectId": source_project_id,
            "oldName": old_name,
            "targetProjectId": target_project_id,
            "newName": new_name,
            "targetPackage": target_package_name,
        }
        return self._ws_client.get_json_response("impact/duplicateModel", params)

    def get_all_sub_models(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response("impact/getSubClasses", modelica_path)

    def get_sub_models(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response("impact/listModels", modelica_path)

    def get_sub_packages(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response("impact/listPackages", modelica_path)

    def close_session(self) -> None:
        return self._ws_client.close()
