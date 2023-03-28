from __future__ import annotations
from collections.abc import Mapping
from typing import Dict, List, Any, Iterator, TYPE_CHECKING
from modelon.impact.client.entities.asserts import assert_variable_in_result

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service
    from modelon.impact.client.sal.experiment import ExperimentService


def _create_result_dict(
    variables: List[str],
    workspace_id: str,
    exp_id: str,
    case_id: str,
    exp_sal: ExperimentService,
) -> Dict[str, Any]:
    response = exp_sal.trajectories_get(workspace_id, exp_id, variables)
    case_index = int(case_id.split("_")[1])
    data = {
        variable: response[i][case_index - 1] for i, variable in enumerate(variables)
    }
    return data


class Result(Mapping):
    """Result class containing base functionality."""

    def __init__(
        self,
        variables: List[str],
        case_id: str,
        workspace_id: str,
        exp_id: str,
        service: Service,
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._sal = service
        self._variables = variables

    def __getitem__(self, key: str) -> Any:
        assert_variable_in_result([key], self._variables)
        response = self._sal.experiment.case_trajectories_get(
            self._workspace_id, self._exp_id, self._case_id, [key]
        )
        return response[0]

    def __iter__(self) -> Iterator[Any]:
        data = _create_result_dict(
            self._variables,
            self._workspace_id,
            self._exp_id,
            self._case_id,
            self._sal.experiment,
        )
        return data.__iter__()

    def __len__(self) -> int:
        return self._variables.__len__()

    def keys(self):  # type: ignore
        return self._variables
