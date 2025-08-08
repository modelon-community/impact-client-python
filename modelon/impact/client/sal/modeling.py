"""Modeling service module."""
from typing import Any, Dict, List

from modelon.impact.client.sal.ws import SyncWebSocketClient


class ModelingService:
    def __init__(self, ws_client: SyncWebSocketClient):
        self._ws_client = ws_client

    @property
    def id(self) -> str:
        return self._ws_client.session_id

    def get_top_class_info(self, class_path: str) -> Any:
        params = {"className": class_path}
        return self._ws_client.get_json_response("impact/getTopClassInfo", params)

    def get_model_parameters(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response(
            "impact/getModelParameters", modelica_path
        )

    def get_model_source(self, class_path: str) -> str:
        params = {"className": class_path}
        return self._ws_client.get_json_response("impact/getSource", params)

    def get_models(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response("impact/listModels", modelica_path)

    def get_subpackages(self, modelica_path: str) -> List[str]:
        return self._ws_client.get_json_response("impact/listPackages", modelica_path)

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

    def close_session(self) -> None:
        return self._ws_client.close()
