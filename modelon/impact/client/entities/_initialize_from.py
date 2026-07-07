from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from modelon.impact.client.entities.external_result import ExternalResult

if TYPE_CHECKING:
    from modelon.impact.client.entities.case import Case
    from modelon.impact.client.entities.experiment import Experiment
    from modelon.impact.client.sal.service import Service

logger = logging.getLogger(__name__)

LATEST_EXPERIMENT = "latest"
"""Symbolic 'initializeFrom' value denoting the most recently created experiment of the
model."""


def _get_latest_experiment(
    workspace_id: str, sal: Service, class_path: Optional[str] = None
) -> Optional[Experiment]:
    from modelon.impact.client.entities.experiment import Experiment

    experiments = sal.workspace.experiments_get(workspace_id, class_path=class_path)[
        "data"
    ]["items"]
    if not experiments:
        logger.warning(
            "Could not resolve 'initializeFrom' value '%s': no experiments "
            "exist for '%s' in workspace '%s'.",
            LATEST_EXPERIMENT,
            class_path,
            workspace_id,
        )
        return None
    latest = max(
        experiments,
        key=lambda item: item.get("meta_data", {}).get("created_epoch", 0),
    )
    return Experiment(workspace_id, latest["id"], sal, latest)


def _resolve_extension_initialize_from(
    workspace_id: str,
    sal: Service,
    modifiers: Dict[str, Any],
    class_path: Optional[str] = None,
) -> Optional[Union[Case, Experiment]]:
    if "initializeFrom" in modifiers:
        from modelon.impact.client.entities.experiment import Experiment

        if modifiers["initializeFrom"] == LATEST_EXPERIMENT:
            return _get_latest_experiment(workspace_id, sal, class_path)

        resp = sal.workspace.experiment_get(workspace_id, modifiers["initializeFrom"])
        return Experiment(workspace_id, resp["id"], sal, resp)
    elif "initializeFromCase" in modifiers:
        from modelon.impact.client.entities.case import Case

        exp_id = modifiers["initializeFromCase"]["experimentId"]
        case_id = modifiers["initializeFromCase"]["caseId"]
        case_data = sal.experiment.case_get(workspace_id, exp_id, case_id)
        return Case(case_data["id"], workspace_id, exp_id, sal, case_data)
    return None


def _resolve_initialize_from(
    workspace_id: str,
    sal: Service,
    modifiers: Dict[str, Any],
    class_path: Optional[str] = None,
) -> Optional[Union[Case, Experiment, ExternalResult]]:
    if "initializeFromExternalResult" in modifiers:
        return ExternalResult(
            result_id=modifiers["initializeFromExternalResult"], service=sal
        )
    return _resolve_extension_initialize_from(
        workspace_id, sal, modifiers, class_path=class_path
    )
