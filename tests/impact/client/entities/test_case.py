import pytest
import unittest.mock as mock
from datetime import datetime
from modelon.impact.client import exceptions
from modelon.impact.client.entities.case import CaseStatus
from tests.impact.client.helpers import (
    create_case_entity,
    create_external_result_entity,
    IDs,
)
from tests.impact.client.fixtures import *


def get_case_put_json_input(mock_method_call):
    (args, _) = tuple(mock_method_call)
    (_, _, _, put_json_input) = args
    return put_json_input


def get_case_put_call_consistent_value(mock_method_call):
    json = get_case_put_json_input(mock_method_call)
    return json['run_info']['consistent']


class TestCase:
    def test_case(self, experiment):
        case = experiment.entity.get_case("case_1")
        assert case.id == "case_1"
        assert case.run_info.status == CaseStatus.SUCCESSFUL
        assert case.run_info.consistent
        assert case.run_info.started == datetime(2022, 9, 12, 6, 42, 36, 945000)
        assert case.run_info.finished == datetime(2022, 9, 12, 6, 42, 37, 990000)
        assert case.get_log() == "Successful Log"
        result, name = case.get_result()
        assert (result, name) == (b'\x00\x00\x00\x00', 'result.mat')
        artifact, name = case.get_artifact('ABCD')
        assert (artifact, name) == (b'\x00\x00\x00\x00', 'result.mat')
        assert case.is_successful()
        assert case.get_trajectories()['inertia.I'] == [1, 2, 3, 4]
        fmu = case.get_fmu()
        assert fmu.id == IDs.FMU_PRIMARY

    def test_multiple_cases(self, batch_experiment):
        case = batch_experiment.get_case("case_2")
        assert case.id == "case_2"
        assert case.run_info.status == CaseStatus.SUCCESSFUL
        assert case.get_log() == "Successful Log"
        result, name = case.get_result()
        assert (result, name) == (b'\x00\x00\x00\x00', 'result.mat')
        artifact, name = case.get_artifact('ABCD')
        assert (artifact, name) == (b'\x00\x00\x00\x00', 'result.mat')
        assert case.is_successful()
        assert case.get_trajectories()['inertia.I'] == [14, 4, 4, 74]

    def test_failed_case(self, experiment_with_failed_case):
        failed_case = experiment_with_failed_case.get_case("case_2")
        assert failed_case.id == "case_1"
        assert failed_case.run_info.status == CaseStatus.FAILED
        assert not failed_case.is_successful()
        pytest.raises(exceptions.OperationFailureError, failed_case.get_result)
        assert failed_case.get_trajectories()["inertia.I"] == [1, 2, 3, 4]

    def test_failed_execution_result(self, experiment_with_failed_case):
        pytest.raises(
            exceptions.OperationFailureError,
            experiment_with_failed_case.get_case("case_2").get_result,
        )

    def test_case_sync(self, experiment, batch_experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        case.input.parametrization = {'PI.k': 120}
        case.input.analysis.simulation_options = {'ncp': 600}
        case.input.analysis.solver_options = {'atol': 1e-8}
        case.input.analysis.simulation_log_level = "DEBUG"
        case.input.analysis.parameters = {"start_time": 1, "final_time": 2e5}
        case.meta.label = "Cruise operating condition"
        case_2 = batch_experiment.get_case('case_2')
        case.initialize_from_case = case_2
        case.sync()
        exp_sal.case_put.assert_has_calls(
            [
                mock.call(
                    IDs.WORKSPACE_PRIMARY,
                    IDs.EXPERIMENT_PRIMARY,
                    'case_1',
                    {
                        'id': 'case_1',
                        'run_info': {
                            'status': 'successful',
                            'consistent': True,
                            "datetime_started": 1662964956945,
                            "datetime_finished": 1662964957990,
                        },
                        'input': {
                            'fmu_id': IDs.FMU_PRIMARY,
                            'analysis': {
                                'analysis_function': 'dynamic',
                                'parameters': {'start_time': 1, 'final_time': 200000.0},
                                'simulation_options': {'ncp': 600},
                                'solver_options': {'atol': 1e-08},
                                'simulation_log_level': 'DEBUG',
                            },
                            'parametrization': {'PI.k': 120},
                            'structural_parametrization': {},
                            'fmu_base_parametrization': {},
                            'initialize_from_case': {
                                'experimentId': IDs.EXPERIMENT_PRIMARY,
                                'caseId': 'case_2',
                            },
                            "initialize_from_external_result": None,
                        },
                        "meta": {'label': 'Cruise operating condition'},
                    },
                )
            ]
        )
        result = case.execute().wait()
        assert result == create_case_entity(
            'case_1', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )

    def test_case_execute_with_no_sync(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        result = case.execute(sync_case_changes=True).wait()
        exp_sal.case_put.assert_called_once()
        assert result == create_case_entity(
            'case_1', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )

    def test_case_execute_with_auto_sync(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        result = case.execute(sync_case_changes=False).wait()
        exp_sal.case_put.assert_not_called()
        assert result == create_case_entity(
            'case_1', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )

    def test_case_sync_second_time_should_call_with_consistent_false(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        case.input.parametrization = {'PI.k': 120}
        case.sync()
        case.sync()
        case_put_calls = exp_sal.case_put.call_args_list
        assert len(case_put_calls) == 2
        assert get_case_put_call_consistent_value(case_put_calls[0])
        assert not get_case_put_call_consistent_value(case_put_calls[1])

    def test_case_initialize_from_external_result(self, experiment):
        result = create_external_result_entity('upload_id')
        case = experiment.entity.get_case("case_1")
        case.initialize_from_external_result = result
        assert case.initialize_from_external_result == result
        case.sync()
        exp_sal = experiment.service
        exp_sal.case_put.assert_has_calls(
            [
                mock.call(
                    IDs.WORKSPACE_PRIMARY,
                    IDs.EXPERIMENT_PRIMARY,
                    'case_1',
                    {
                        'id': 'case_1',
                        'run_info': {
                            'status': 'successful',
                            'consistent': True,
                            "datetime_started": 1662964956945,
                            "datetime_finished": 1662964957990,
                        },
                        'input': {
                            'fmu_id': IDs.FMU_PRIMARY,
                            'analysis': {
                                'analysis_function': 'dynamic',
                                'parameters': {'start_time': 0, 'final_time': 1},
                                'simulation_options': {},
                                'solver_options': {},
                                'simulation_log_level': 'NOTHING',
                            },
                            'parametrization': {},
                            'structural_parametrization': {},
                            'fmu_base_parametrization': {},
                            'initialize_from_case': None,
                            'initialize_from_external_result': {
                                'uploadId': 'upload_id'
                            },
                        },
                        "meta": {"label": "Cruise operating point"},
                    },
                )
            ]
        )

    def test_reinitiazlizing_result_initialized_case_from_case(self, experiment):
        result = create_external_result_entity('upload_id')
        case_to_init = create_case_entity(
            'Case_2', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        case = experiment.entity.get_case("case_1")
        case.initialize_from_external_result = result
        with pytest.raises(Exception) as err:
            case.initialize_from_case = case_to_init
        assert (
            str(err.value) == "A case cannot use both 'initialize_from_case' and "
            "'initialize_from_external_result' to specify what to initialize from! "
            "To resolve this, set the 'initialize_from_external_result' attribute "
            "to None and re-try."
        )

    def test_reinitiazlizing_case_initialized_case_from_result(self, experiment):
        result = create_external_result_entity('upload_id')
        case_to_init = create_case_entity(
            'Case_2', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        case = experiment.entity.get_case("case_1")
        case.initialize_from_case = case_to_init
        with pytest.raises(Exception) as err:
            case.initialize_from_external_result = result
        assert (
            str(err.value) == "A case cannot use both 'initialize_from_case' and "
            "'initialize_from_external_result' to specify what to initialize from! "
            "To resolve this, set the 'initialize_from_case' attribute "
            "to None and re-try."
        )

    def test_set_case_label(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service
        exp.set_label('Label')
        exp_sal.experiment_set_label.assert_has_calls(
            [mock.call(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, 'Label')]
        )

    def test_case_input(self, experiment):
        exp = experiment.entity

        case = exp.get_case("case_1")
        case.input.analysis.parameters = {"start_time": 0, "final_time": 90}
        case.input.analysis.simulation_options = {'ncp': 600}
        case.input.analysis.solver_options = {'atol': 1e-8}
        case.input.analysis.simulation_log_level = "DEBUG"
        case.input.parametrization = {'PI.k': 120}

        assert case.input.analysis.parameters == {"start_time": 0, "final_time": 90}
        assert case.input.analysis.simulation_options == {'ncp': 600}
        assert case.input.analysis.solver_options == {'atol': 1e-8}
        assert case.input.parametrization == {'PI.k': 120}

    def test_get_result_invalid_format(self, experiment):
        case = experiment.entity.get_case("case_1")
        pytest.raises(ValueError, case.get_result, 'ma')
