from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.entities.workspace import Workspace
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.model import Model
from modelon.impact.client.operations.experiment import ExperimentOperation
from modelon.impact.client.operations.model_executable import (
    CachedModelExecutableOperation,
    ModelExecutableOperation,
)
from unittest.mock import MagicMock


def create_workspace_entity(
    name,
    workspace_service=None,
    model_exe_service=None,
    experiment_service=None,
    custom_function_service=None,
):
    return Workspace(
        name,
        workspace_service or MagicMock(),
        model_exe_service or MagicMock(),
        experiment_service or MagicMock(),
        custom_function_service or MagicMock(),
    )


def create_model_entity(
    class_name, workspace_id, workspace_service=None, model_exe_service=None,
):
    return Model(
        class_name,
        workspace_id,
        workspace_service or MagicMock(),
        model_exe_service or MagicMock(),
    )


def create_model_exe_entity(
    workspace_id,
    fmu_id,
    workspace_service=None,
    model_exe_service=None,
    info=None,
    modifiers=None,
):
    return ModelExecutable(
        workspace_id,
        fmu_id,
        workspace_service or MagicMock(),
        model_exe_service or MagicMock(),
        info,
        modifiers,
    )


def create_experiment_entity(
    workspace_id,
    exp_id,
    workspace_service=None,
    model_exe_service=None,
    experiment_service=None,
    info=None,
):
    return Experiment(
        workspace_id,
        exp_id,
        workspace_service or MagicMock(),
        model_exe_service or MagicMock(),
        experiment_service or MagicMock(),
        info,
    )


def create_case_entity(
    case_id,
    workspace_id,
    exp_id,
    workspace_service=None,
    model_exe_service=None,
    experiment_service=None,
    info=None,
):
    return Case(
        case_id,
        workspace_id,
        exp_id,
        experiment_service or MagicMock(),
        model_exe_service or MagicMock(),
        workspace_service or MagicMock(),
        info,
    )


def create_external_result_entity(result_id, workspace_service=None):
    return ExternalResult(result_id, workspace_service or MagicMock())


def create_custom_function_entity(
    workspace_id, name, parameter_data=None, custom_function_service=None
):
    return CustomFunction(
        workspace_id, name, parameter_data, custom_function_service or MagicMock()
    )


def create_experiment_operation(
    workspace_id,
    exp_id,
    workspace_service=None,
    model_exe_service=None,
    exp_service=None,
):
    return ExperimentOperation(
        workspace_id,
        exp_id,
        workspace_service or MagicMock(),
        model_exe_service or MagicMock(),
        exp_service or MagicMock(),
    )


def create_cached_model_exe_operation(
    workspace_id,
    fmu_id,
    workspace_service=None,
    model_exe_service=None,
    info=None,
    modifiers=None,
):
    return CachedModelExecutableOperation(
        workspace_id,
        fmu_id,
        workspace_service or MagicMock(),
        model_exe_service or MagicMock(),
        info=info,
        modifiers=modifiers,
    )


def create_model_exe_operation(
    workspace_id, fmu_id, workspace_service=None, model_exe_service=None,
):
    return ModelExecutableOperation(
        workspace_id,
        fmu_id,
        workspace_service or MagicMock(),
        model_exe_service or MagicMock(),
    )
