from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from modelon.impact.client.entities.external_result import ExternalResult

if TYPE_CHECKING:
    from modelon.impact.client.entities.case import Case
    from modelon.impact.client.entities.experiment import Experiment
    from modelon.impact.client.sal.service import Service


def _resolve_initialize_from(
    workspace_id: str,
    sal: Service,
    modifiers: Dict[str, Any],
) -> Optional[Union[Case, Experiment, ExternalResult]]:
    if "initializeFrom" in modifiers:
        from modelon.impact.client.entities.experiment import Experiment

        resp = sal.workspace.experiment_get(workspace_id, modifiers["initializeFrom"])
        return Experiment(workspace_id, resp["id"], sal, resp)
    elif "initializeFromCase" in modifiers:
        from modelon.impact.client.entities.case import Case

        exp_id = modifiers["initializeFromCase"]["experimentId"]
        case_id = modifiers["initializeFromCase"]["caseId"]
        case_data = sal.experiment.case_get(workspace_id, exp_id, case_id)
        return Case(case_data["id"], workspace_id, exp_id, sal, case_data)
    elif "initializeFromExternalResult" in modifiers:
        return ExternalResult(
            result_id=modifiers["initializeFromExternalResult"], service=sal
        )
    return None
