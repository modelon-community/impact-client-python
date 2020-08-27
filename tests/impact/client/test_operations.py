import pytest
import modelon.impact.client.exceptions as exceptions
from tests.impact.client.fixtures import *
from modelon.impact.client.operations import Status, Case


class TestModelExecutable:
    def test_successful_compile(self, fmu):
        assert fmu.id == 'Test'
        assert fmu.is_complete()
        assert fmu.is_successful()
        assert fmu.settable_parameters() == ['h0', 'v']
        assert fmu.log() == "Successful Log"
        assert fmu.metadata == {
            "steady_state": {
                "residual_variable_count": 1,
                "iteration_variable_count": 2,
            }
        }

    def test_running_compilation(self, fmu_compile_running):
        assert fmu_compile_running.id == 'Test'
        assert not fmu_compile_running.is_complete()
        assert fmu_compile_running.status() == Status.RUNNING

    def test_running_compilation_log(self, fmu_compile_running):
        pytest.raises(
            exceptions.OperationNotCompleteError, fmu_compile_running.log,
        )

    def test_failed_compilation(self, fmu_compile_failed):
        assert fmu_compile_failed.id == 'Test'
        assert fmu_compile_failed.is_complete()
        assert fmu_compile_failed.info["run_info"]["status"] == "failed"
        assert not fmu_compile_failed.is_successful()
        assert fmu_compile_failed.log() == "Failed Log"

    def test_cancel_compile_wait_timeout(self, fmu_compile_failed):
        pytest.raises(
            exceptions.OperationTimeOutError,
            fmu_compile_failed.wait,
            timeout=1e-6,
            status=Status.CANCELLED,
        )

    def test_failed_compile_wait_done(self, fmu_compile_failed):
        fmu_compile_failed.wait(status=Status.DONE)
        assert fmu_compile_failed.is_complete()
        assert fmu_compile_failed.info["run_info"]["status"] == "failed"
        assert not fmu_compile_failed.is_successful()

    def test_failed_compile_empty_log(self, fmu_compile_failed_empty_log):
        pytest.raises(exceptions.EmptyLogError, fmu_compile_failed_empty_log.log)

    def test_cancelled_compilation(self, fmu_compile_cancelled):
        assert fmu_compile_cancelled.info["run_info"]["status"] == "cancelled"
        pytest.raises(
            exceptions.OperationFailureError, fmu_compile_cancelled.is_successful,
        )
        pytest.raises(
            exceptions.OperationFailureError, fmu_compile_cancelled.is_complete,
        )


class TestExperiment:
    def test_successful_execute(self, experiment):
        assert experiment.id == "Test"
        assert experiment.is_complete()
        assert experiment.is_successful()
        assert experiment.info["run_info"]["status"] == "done"
        assert experiment.variables() == ["inertia.I", "time"]
        assert experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert experiment.case("case_1") == Case("case_1", "Workspace", "Test")

    def test_successful_batch_execute(self, batch_experiment):
        assert batch_experiment.is_successful()
        assert batch_experiment.variables() == ["inertia.I", "time"]
        assert batch_experiment.cases() == [
            Case("case_1", "Workspace", "Test"),
            Case("case_2", "Workspace", "Test"),
        ]

    def test_running_execution(self, running_experiment):
        assert not running_experiment.is_complete()
        assert running_experiment.status() == Status.RUNNING

    def test_failed_execution(self, failed_experiment):
        assert failed_experiment.id == 'Test'
        assert failed_experiment.is_complete()
        assert failed_experiment.info["run_info"]["status"] == "done"
        assert not failed_experiment.is_successful()

    def test_cancel_execution_wait_timeout(self, failed_experiment):
        pytest.raises(
            exceptions.OperationTimeOutError,
            failed_experiment.wait,
            timeout=1e-6,
            status=Status.CANCELLED,
        )

    def test_failed_execution_wait_done(self, failed_experiment):
        failed_experiment.wait(status=Status.DONE)
        assert failed_experiment.is_complete()
        assert failed_experiment.status() == Status.DONE
        assert failed_experiment.info["run_info"]["failed"] == 1
        assert not failed_experiment.is_successful()

    def test_failed_execution_cases(self, failed_experiment):
        assert failed_experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert failed_experiment.case("case_1") == Case("case_1", "Workspace", "Test")

    def test_cancelled_execution(self, cancelled_experiment):
        assert cancelled_experiment.info["run_info"]["status"] == "done"
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.is_successful,
        )
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.is_complete,
        )

    def test_cancelled_execution_cases(self, cancelled_experiment):
        assert cancelled_experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert cancelled_experiment.case("case_1") == Case(
            "case_1", "Workspace", "Test"
        )

    def test_exp_trajectories_single_run(self, experiment):
        exp = experiment.trajectories(['inertia.I', 'time'])
        assert exp['case_1']['inertia.I'] == [1, 2, 3, 4]
        assert exp['case_1']['time'] == [5, 2, 9, 4]

    def test_exp_trajectories_batch_execute(self, batch_experiment):
        exp = batch_experiment.trajectories(['inertia.I'])
        assert exp['case_1']['inertia.I'] == [1, 2, 3, 4]
        assert exp['case_2']['inertia.I'] == [14, 4, 4, 74]

    def test_exp_trajectories_no_keys(self, experiment):
        pytest.raises(ValueError, experiment.trajectories, [])

    def test_exp_trajectories_invalid_keys(self, experiment):
        pytest.raises(ValueError, experiment.trajectories, ['s'])


class TestCase:
    def test_case(self, experiment):
        case = experiment.case("case_1")
        assert case.id == "case_1"
        assert case.info["run_info"]["status"] == "successful"
        assert case.log() == "Successful Log"
        assert case.result() == b'\x00\x00\x00\x00'
        assert case.is_successful()
        assert case.trajectories()['inertia.I'] == [1, 2, 3, 4]

    def test_multiple_cases(self, batch_experiment):
        case = batch_experiment.case("case_2")
        assert case.id == "case_2"
        assert case.info["run_info"]["status"] == "successful"
        assert case.log() == "Successful Log"
        assert case.result() == b'\x00\x00\x00\x00'
        assert case.is_successful()
        assert case.trajectories()['inertia.I'] == [14, 4, 4, 74]

    def test_failed_case(self, failed_experiment):
        failed_case = failed_experiment.case("case_2")
        assert failed_case.id == "case_1"
        assert failed_case.info["run_info"]["status"] == "failed"
        assert not failed_case.is_successful()
        pytest.raises(
            exceptions.OperationFailureError, failed_case.result,
        )

    def test_failed_execution_result(self, failed_experiment):
        pytest.raises(
            exceptions.OperationFailureError, failed_experiment.case("case_2").result,
        )
