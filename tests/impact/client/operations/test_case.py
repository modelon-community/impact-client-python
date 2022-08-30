import pytest
from modelon.impact.client import exceptions
from tests.impact.client.helpers import create_case_entity, IDs
from modelon.impact.client.operations.base import Status
from tests.impact.client.fixtures import *


class TestCaseOperation:
    def test_execute_wait_done(self, experiment):
        case = experiment.entity.get_case('case_1')
        case_ops = case.execute()
        assert case_ops.id == "case_1"
        assert case_ops.status() == Status.DONE
        assert case_ops.is_complete()
        assert case_ops.wait() == create_case_entity(
            'case_1', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )

    def test_execute_wait_cancel_timeout(self, experiment):
        case = experiment.entity.get_case('case_1')
        case_ops = case.execute()
        assert case_ops.id == "case_1"
        assert case_ops.status() == Status.DONE
        assert case_ops.is_complete()
        pytest.raises(
            exceptions.OperationTimeOutError, case_ops.wait, 1e-10, Status.CANCELLED
        )

    def test_execute_wait_running(self, experiment_running):
        case = experiment_running.get_case('case_1')
        case_ops = case.execute()
        assert case_ops.id == "case_1"
        assert case_ops.status() == Status.RUNNING
        assert not case_ops.is_complete()
        assert case_ops.wait(status=Status.RUNNING) == create_case_entity(
            'case_1', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY,
        )

    def test_execute_wait_cancelled(self, experiment_cancelled):
        case = experiment_cancelled.get_case('case_1')
        case = case.execute()
        assert case.id == "case_1"
        assert case.status() == Status.CANCELLED
        assert case.wait(status=Status.CANCELLED) == create_case_entity(
            'case_1', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY,
        )

    def test_execute_wait_timeout(self, experiment_cancelled):
        case = experiment_cancelled.get_case('case_1')
        case = case.execute()
        assert case.id == "case_1"
        assert case.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, case.wait, 1e-10, Status.DONE)

