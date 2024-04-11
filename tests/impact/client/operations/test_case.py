import pytest

from modelon.impact.client import exceptions
from modelon.impact.client.operations.base import Status
from tests.impact.client.helpers import IDs, create_case_entity


class TestCaseOperation:
    def test_execute_wait_done(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
        case_ops = case.execute()
        assert case_ops.id == IDs.CASE_ID_PRIMARY
        assert case_ops.status == Status.DONE
        assert case_ops.is_complete()
        assert case_ops.wait() == create_case_entity(
            IDs.CASE_ID_PRIMARY, IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY
        )

    def test_execute_wait_cancel_timeout(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
        case_ops = case.execute()
        assert case_ops.id == IDs.CASE_ID_PRIMARY
        assert case_ops.status == Status.DONE
        assert case_ops.is_complete()
        pytest.raises(
            exceptions.OperationTimeOutError, case_ops.wait, 1e-10, Status.CANCELLED
        )

    def test_execute_wait_running(self, experiment_running):
        case = experiment_running.get_case(IDs.CASE_ID_PRIMARY)
        case_ops = case.execute()
        assert case_ops.id == IDs.CASE_ID_PRIMARY
        assert case_ops.status == Status.RUNNING
        assert not case_ops.is_complete()
        assert case_ops.wait(status=Status.RUNNING) == create_case_entity(
            IDs.CASE_ID_PRIMARY,
            IDs.WORKSPACE_ID_PRIMARY,
            IDs.EXPERIMENT_ID_PRIMARY,
        )

    def test_execute_wait_cancelled(self, experiment_cancelled):
        case = experiment_cancelled.get_case(IDs.CASE_ID_PRIMARY)
        case = case.execute()
        assert case.id == IDs.CASE_ID_PRIMARY
        assert case.status == Status.CANCELLED
        assert case.wait(status=Status.CANCELLED) == create_case_entity(
            IDs.CASE_ID_PRIMARY,
            IDs.WORKSPACE_ID_PRIMARY,
            IDs.EXPERIMENT_ID_PRIMARY,
        )

    def test_execute_wait_timeout(self, experiment_cancelled):
        case = experiment_cancelled.get_case(IDs.CASE_ID_PRIMARY)
        case = case.execute()
        assert case.id == IDs.CASE_ID_PRIMARY
        assert case.status == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, case.wait, 1e-10, Status.DONE)
