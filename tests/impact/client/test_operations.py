import pytest
import modelon.impact.client.exceptions as exceptions
from tests.impact.client.fixtures import *
from modelon.impact.client.operations import Status, Case


class TestModelExecutable:
    def test_successful_compile(self, fmu):
        assert fmu.id == 'Test'
        assert fmu.is_complete()
        assert fmu.is_successful()
        assert fmu.settable_parameters == ['h0', 'v']
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
        assert fmu_compile_running.status() == 'running'

    def test_failed_compilation(self, fmu_compile_failed):
        assert fmu_compile_failed.id == 'Test'
        assert fmu_compile_failed.is_complete()
        assert fmu_compile_failed.info["run_info"]["status"] == "failed"
        assert not fmu_compile_failed.is_successful()
        assert fmu_compile_failed.log() == "Failed Log"

    def test_failed_compile_wait_cancel(self, fmu_compile_failed):
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_failed.wait,
            status=Status.CANCELLED,
        )

    def test_failed_compile_wait_done(self, fmu_compile_failed):
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_failed.wait,
            status=Status.DONE,
        )

    def test_cancelled_compilation(self, fmu_compile_cancelled):
        assert fmu_compile_cancelled.id == 'Test'
        assert fmu_compile_cancelled.is_complete()
        assert fmu_compile_cancelled.info["run_info"]["status"] == "cancelled"
        assert not fmu_compile_cancelled.is_successful()

    def test_cancelled_compile_wait_done(self, fmu_compile_cancelled):
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_cancelled.wait,
            status=Status.DONE,
        )

    def test_cancelled_compilation_log(self, fmu_compile_cancelled_log):
        pytest.raises(exceptions.EmptyLogError, fmu_compile_cancelled_log.log)


class TestExperiment:
    def test_successful_execute(self, experiment):
        assert experiment.id == "Test"
        assert experiment.is_complete()
        assert experiment.is_successful()
        assert experiment.info["run_info"]["status"] == "done"
        assert experiment.variables == ["PI.J", "inertia.I", "time"]
        assert experiment.log() == "Successful Log"
        assert experiment.get_trajectories("PI.J") == {
            'PI.J': [[5, 2, 9, 4]],
            'time': [[1, 2, 3, 4]],
        }
        assert experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert experiment.case("case_1") == Case("case_1", "Workspace", "Test")

    def test_successful_batch_execute(self, batch_experiment):
        assert batch_experiment.is_successful()
        assert batch_experiment.variables == ["PI.J", "inertia.I", "time"]
        assert batch_experiment.cases() == [
            Case("case_1", "Workspace", "Test"),
            Case("case_2", "Workspace", "Test"),
        ]
        assert batch_experiment.get_trajectories("PI.J") == {
            'PI.J': [[5, 2, 9, 4], [1, 2, 3, 4]],
            'time': [[1, 2, 3, 4], [1, 2, 3, 4]],
        }

    def test_running_execution(self, running_experiment):
        assert not running_experiment.is_successful()
        assert running_experiment.status() == "running"

    def test_failed_execution(self, failed_experiment):
        assert failed_experiment.id == 'Test'
        assert failed_experiment.is_complete()
        assert failed_experiment.info["run_info"]["status"] == "done"
        assert not failed_experiment.is_successful()
        assert failed_experiment.log() == "Failed Log"

    def test_failed_execution_wait_cancel(self, failed_experiment):
        pytest.raises(
            exceptions.OperationFailureError,
            failed_experiment.wait,
            status=Status.CANCELLED,
        )

    def test_failed_execution_wait_done(self, failed_experiment):
        pytest.raises(
            exceptions.OperationFailureError,
            failed_experiment.wait,
            status=Status.DONE,
        )

    def test_failed_execution_trajectories(self, failed_experiment):
        pytest.raises(
            exceptions.OperationFailureError, failed_experiment.get_trajectories,
        )

    def test_failed_execution_result(self, failed_experiment):
        pytest.raises(
            exceptions.OperationFailureError, failed_experiment.result,
        )

    def test_failed_execution_cases(self, failed_experiment):
        assert failed_experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert failed_experiment.case("case_1") == Case("case_1", "Workspace", "Test")

    def test_cancelled_execution(self, cancelled_experiment):
        assert cancelled_experiment.id == 'Test'
        assert not cancelled_experiment.is_complete()
        assert cancelled_experiment.info["run_info"]["status"] == "done"
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.is_successful,
        )

    def test_cancelled_execution_wait_done(self, cancelled_experiment):
        pytest.raises(
            exceptions.OperationFailureError,
            cancelled_experiment.wait,
            status=Status.DONE,
        )

    def test_cancelled_compilation_log(self, cancelled_experiment):
        pytest.raises(exceptions.OperationFailureError, cancelled_experiment.log)

    def test_cancelled_execution_trajectories(self, cancelled_experiment):
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.get_trajectories,
        )

    def test_cancelled_execution_result(self, cancelled_experiment):
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.result,
        )

    def test_cancelled_execution_cases(self, cancelled_experiment):
        assert cancelled_experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert cancelled_experiment.case("case_1") == Case(
            "case_1", "Workspace", "Test"
        )


class TestCase:
    def test_case(self, case):
        assert case.id == "case_1"
        assert case.info["run_info"]["status"] == "successful"
        assert case.log() == "Successful Log"
        assert case.result() == b'\x00\x00\x00\x00'
