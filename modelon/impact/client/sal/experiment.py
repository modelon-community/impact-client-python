"""Experiment service module."""
from __future__ import annotations

import enum
import json
from typing import Any, Dict, List, Optional, Text, Tuple, Union

from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


@enum.unique
class ResultFormat(enum.Enum):
    """Class representing an enumeration for the possible formats available for
    downloading results."""

    MAT = "mat"
    CSV = "csv"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        if cls not in ["mat", "csv"]:
            raise ValueError(
                "Invalid result format! Allowed formats are 'mat' and 'csv."
            )
        return cls(value)


class ExperimentService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client
        self._case_schema = "application/vnd.impact.cases.v2+json"

    def experiment_execute(
        self, workspace_id: str, exp_id: str, case_ids: Optional[List[str]] = None
    ) -> str:
        body = {"includeCases": {"ids": case_ids}} if case_ids is not None else None
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{exp_id}/execution"
        ).resolve()
        self._http_client.post_json_no_response_body(url, body=body)
        return exp_id

    def experiment_delete(self, workspace_id: str, exp_id: str) -> None:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/experiments/{exp_id}"
        ).resolve()
        self._http_client.delete_json(url)

    def experiment_set_label(self, workspace_id: str, exp_id: str, label: str) -> None:
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/experiments/{exp_id}"
        ).resolve()
        return self._http_client.put_json_no_response_body(url, body={"label": label})

    def execute_status(self, workspace_id: str, experiment_id: str) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/execution"
        ).resolve()
        return self._http_client.get_json(url)

    def execute_cancel(self, workspace_id: str, experiment_id: str) -> None:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/execution"
        ).resolve()
        return self._http_client.delete_json(url)

    def experiment_result_variables_get(
        self, workspace_id: str, experiment_id: str
    ) -> List[str]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/variables"
        ).resolve()
        return self._http_client.get_json(url)

    def case_result_variables_get(
        self, workspace_id: str, experiment_id: str, case_id: str
    ) -> List[str]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/variables"
        ).resolve()
        return self._http_client.get_json(url)

    def trajectories_get(
        self,
        workspace_id: str,
        experiment_id: str,
        variables: List[str],
        last_point_only: bool,
        format: Optional[str] = None,
    ) -> Any:
        body = {
            "variable_names": variables,
            "filter": {"lastPointOnly": last_point_only},
        }
        headers = {"Accept": format or "application/vnd.impact.trajectories.v1+json"}
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/trajectories"
        ).resolve()
        return self._http_client.post_json(url, body=body, headers=headers)

    def cases_get(self, workspace_id: str, experiment_id: str) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases"
        ).resolve()
        return self._http_client.get_json(url, headers={"Accept": self._case_schema})

    def case_get(
        self, workspace_id: str, experiment_id: str, case_id: str
    ) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}"
        ).resolve()
        return self._http_client.get_json(url, headers={"Accept": self._case_schema})

    def case_put(
        self,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        case_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}"
        ).resolve()
        return self._http_client.put_json(
            url,
            body=case_data,
            headers={"Content-type": self._case_schema, "Accept": self._case_schema},
        )

    def case_get_log(self, workspace_id: str, experiment_id: str, case_id: str) -> str:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/log"
        ).resolve()
        return self._http_client.get_text(url)

    def case_result_get(
        self,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        result_format: ResultFormat = ResultFormat.MAT,
    ) -> Tuple[Union[Text, bytes], str]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/result"
        ).resolve()
        if result_format == ResultFormat.CSV:
            headers = {"Accept": "text/csv"}
            csv_resp = self._http_client.get_csv(url, headers=headers)
            return csv_resp.stream, csv_resp.file_name
        headers = {"Accept": "application/vnd.impact.mat.v1+octet-stream"}
        mat_resp = self._http_client.get_mat(url, headers=headers)
        return mat_resp.stream, mat_resp.file_name

    def case_trajectories_get(
        self,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        variables: List[str],
        last_point_only: bool,
    ) -> List[str]:
        body = {
            "variable_names": variables,
            "filter": {"lastPointOnly": last_point_only},
        }
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/trajectories"
        ).resolve()
        return self._http_client.post_json(url, body=body)

    def case_artifact_get(
        self, workspace_id: str, experiment_id: str, case_id: str, artifact_id: str
    ) -> Tuple[bytes, str]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/custom-artifacts/{artifact_id}"
        ).resolve()
        resp = self._http_client.get_file_response(url)
        return resp.stream, resp.file_name

    def case_artifacts_meta_get(
        self, workspace_id: str, experiment_id: str, case_id: str
    ) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/custom-artifacts"
        ).resolve()
        return self._http_client.get_json(url)

    def custom_artifact_upload(
        self,
        path_to_artifact: str,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        artifact_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/custom-artifacts-imports"
        ).resolve()
        options: Dict[str, Any] = {"overwrite": overwrite}
        if artifact_id:
            options["artifactId"] = artifact_id
        with open(path_to_artifact, "rb") as f:
            multipart_form_data = {
                "file": f,
                "options": json.dumps(options),
            }
            return self._http_client.post_json(url, files=multipart_form_data)

    def case_result_upload(
        self,
        path_to_result: str,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/result-imports"
        ).resolve()
        options: Dict[str, Any] = {"overwrite": overwrite}
        with open(path_to_result, "rb") as f:
            multipart_form_data = {
                "file": f,
                "options": json.dumps(options),
            }
            return self._http_client.post_json(url, files=multipart_form_data)
