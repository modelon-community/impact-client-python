"""Experiment service module"""
import enum
from typing import Any, Optional, List, Dict
from modelon.impact.client.sal.http import HTTPClient
from modelon.impact.client.sal.uri import URI


@enum.unique
class ResultFormat(enum.Enum):
    """
    Class representing an enumeration for the possible
    formats avaiable for downloading results.
    """

    MAT = "mat"
    CSV = "csv"

    @classmethod
    def _missing_(cls, value):
        if cls not in ['mat', 'csv']:
            raise ValueError(
                "Invalid result format! Allowed formats are 'mat' and 'csv."
            )
        return cls(value)


class ExperimentService:
    def __init__(self, uri: URI, http_client: HTTPClient):
        self._base_uri = uri
        self._http_client = http_client

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

    def experiment_delete(self, workspace_id: str, exp_id: str):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/experiments/{exp_id}"
        ).resolve()
        self._http_client.delete_json(url)

    def experiment_set_label(self, workspace_id: str, exp_id: str, label: str):
        url = (
            self._base_uri / f"api/workspaces/{workspace_id}/experiments/{exp_id}"
        ).resolve()
        return self._http_client.put_json_no_response_body(url, body={"label": label})

    def execute_status(self, workspace_id: str, experiment_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/execution"
        ).resolve()
        return self._http_client.get_json(url)

    def execute_cancel(self, workspace_id: str, experiment_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/execution"
        ).resolve()
        return self._http_client.delete_json(url)

    def result_variables_get(self, workspace_id: str, experiment_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/variables"
        ).resolve()
        return self._http_client.get_json(url)

    def trajectories_get(
        self, workspace_id: str, experiment_id: str, variables: List[str]
    ):
        body = {"variable_names": variables}
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/trajectories"
        ).resolve()
        return self._http_client.post_json(url, body=body)

    def cases_get(self, workspace_id: str, experiment_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases"
        ).resolve()
        return self._http_client.get_json(url)

    def case_get(self, workspace_id: str, experiment_id: str, case_id: str):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}"
        ).resolve()
        return self._http_client.get_json(url)

    def case_put(
        self,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        case_data: Dict[str, Any],
    ):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}"
        ).resolve()
        return self._http_client.put_json(url, body=case_data)

    def case_get_log(self, workspace_id: str, experiment_id: str, case_id: str):
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
    ):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/result"
        ).resolve()
        if result_format == ResultFormat.CSV:
            headers = {'Accept': 'text/csv'}
            csv_resp = self._http_client.get_csv(url, headers=headers)
            return csv_resp.stream, csv_resp.file_name
        headers = {'Accept': 'application/vnd.impact.mat.v1+octet-stream'}
        mat_resp = self._http_client.get_mat(url, headers=headers)
        return mat_resp.stream, mat_resp.file_name

    def case_trajectories_get(
        self, workspace_id: str, experiment_id: str, case_id: str, variables: List[str]
    ):
        body = {"variable_names": variables}
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/trajectories"
        ).resolve()
        return self._http_client.post_json(url, body=body)

    def case_artifact_get(
        self, workspace_id: str, experiment_id: str, case_id: str, artifact_id: str
    ):
        url = (
            self._base_uri
            / f"api/workspaces/{workspace_id}/experiments/{experiment_id}/cases/"
            f"{case_id}/custom-artifacts/{artifact_id}"
        ).resolve()
        resp = self._http_client.get_octet_response(url)
        return resp.stream, resp.file_name
