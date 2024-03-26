from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from modelon.impact.client.configuration import get_client_experiments_v3_experimental
from modelon.impact.client.options import BaseExecutionOptions

if TYPE_CHECKING:
    from modelon.impact.client.entities.case import Case


def get_options(default_options: Any, options: Optional[Any]) -> Dict[str, Any]:
    return (
        dict(default_options())
        if options is None
        else dict(options)
        if isinstance(options, BaseExecutionOptions)
        else options
    )


def case_to_identifier_dict(case: Case) -> Dict[str, Any]:
    return {
        "caseId": case.id,
        "experimentId": case.experiment_id,
    }


def custom_function_parameters_to_dict(parameter_values: dict[str, Any]) -> Any:
    if get_client_experiments_v3_experimental():
        return [
            {"name": name, "value": value} for name, value in parameter_values.items()
        ]
    else:
        return parameter_values
