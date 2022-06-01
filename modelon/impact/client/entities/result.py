from collections.abc import Mapping
from typing import List
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.sal.experiment import ExperimentService
from modelon.impact.client.entities.asserts import assert_variable_in_result


def _create_result_dict(variables, workspace_id, exp_id, case_id, exp_sal):
    response = exp_sal.trajectories_get(workspace_id, exp_id, variables)
    case_index = int(case_id.split("_")[1])
    data = {
        variable: response[i][case_index - 1] for i, variable in enumerate(variables)
    }
    return data


class Result(Mapping):
    """
    Result class containing base functionality.
    """

    def __init__(
        self,
        variables: List[str],
        case_id: str,
        workspace_id: str,
        exp_id: str,
        workspace_service: WorkspaceService,
        exp_service: ExperimentService,
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service
        self._variables = variables

    def __getitem__(self, key):
        assert_variable_in_result([key], self._variables)
        response = self._exp_sal.case_trajectories_get(
            self._workspace_id, self._exp_id, self._case_id, [key]
        )
        return response[0]

    def __iter__(self):
        data = _create_result_dict(
            self._variables,
            self._workspace_id,
            self._exp_id,
            self._case_id,
            self._exp_sal,
        )
        return data.__iter__()

    def __len__(self):
        return self._variables.__len__()

    def keys(self):
        return self._variables
