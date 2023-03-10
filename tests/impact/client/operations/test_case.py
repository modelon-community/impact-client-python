import pytest
from modelon.impact.client import exceptions
from tests.impact.client.helpers import create_case_entity, IDs
from modelon.impact.client.operations.base import Status


class TestCaseOperation:
    def test_execute_wait_done(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_PRIMARY)
        case_ops = case.execute()
        assert case_ops.id == IDs.CASE_PRIMARY
        assert case_ops.status() == Status.DONE
        assert case_ops.is_complete()
        assert case_ops.wait() == create_case_entity(
            IDs.CASE_PRIMARY, IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )

    def test_execute_wait_cancel_timeout(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_PRIMARY)
        case_ops = case.execute()
        assert case_ops.id == IDs.CASE_PRIMARY
        assert case_ops.status() == Status.DONE
        assert case_ops.is_complete()
        pytest.raises(
            exceptions.OperationTimeOutError, case_ops.wait, 1e-10, Status.CANCELLED
        )

    def test_execute_wait_running(self, experiment_running):
        case = experiment_running.get_case(IDs.CASE_PRIMARY)
        case_ops = case.execute()
        assert case_ops.id == IDs.CASE_PRIMARY
        assert case_ops.status() == Status.RUNNING
        assert not case_ops.is_complete()
        assert case_ops.wait(status=Status.RUNNING) == create_case_entity(
            IDs.CASE_PRIMARY,
            IDs.WORKSPACE_PRIMARY,
            IDs.EXPERIMENT_PRIMARY,
        )

    def test_execute_wait_cancelled(self, experiment_cancelled):
        case = experiment_cancelled.get_case(IDs.CASE_PRIMARY)
        case = case.execute()
        assert case.id == IDs.CASE_PRIMARY
        assert case.status() == Status.CANCELLED
        assert case.wait(status=Status.CANCELLED) == create_case_entity(
            IDs.CASE_PRIMARY,
            IDs.WORKSPACE_PRIMARY,
            IDs.EXPERIMENT_PRIMARY,
        )

    def test_execute_wait_timeout(self, experiment_cancelled):
        case = experiment_cancelled.get_case(IDs.CASE_PRIMARY)
        case = case.execute()
        assert case.id == IDs.CASE_PRIMARY
        assert case.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, case.wait, 1e-10, Status.DONE)
