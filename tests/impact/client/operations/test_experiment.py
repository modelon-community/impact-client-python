import pytest
from modelon.impact.client import exceptions
from tests.impact.client.helpers import create_experiment_entity
from modelon.impact.client.operations.base import Status
from tests.impact.client.fixtures import *


class TestExperimentOperation:
    def test_execute_wait_done(self, workspace):
        exp = workspace.entity.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.DONE
        assert exp.is_complete()
        assert exp.wait() == create_experiment_entity('AwesomeWorkspace', 'pid_2009')

    def test_execute_wait_cancel_timeout(self, workspace):
        exp = workspace.entity.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.DONE
        assert exp.is_complete()
        pytest.raises(
            exceptions.OperationTimeOutError, exp.wait, 1e-10, Status.CANCELLED
        )

    def test_execute_wait_running(self, workspace_execute_running):
        exp = workspace_execute_running.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.RUNNING
        assert not exp.is_complete()
        assert exp.wait(status=Status.RUNNING) == create_experiment_entity(
            'AwesomeWorkspace', 'pid_2009'
        )

    def test_execute_wait_cancelled(self, workspace_execute_cancelled):
        exp = workspace_execute_cancelled.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.CANCELLED
        assert exp.wait(status=Status.CANCELLED) == create_experiment_entity(
            'AwesomeWorkspace', 'pid_2009'
        )

    def test_execute_wait_timeout(self, workspace_execute_cancelled):
        exp = workspace_execute_cancelled.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, exp.wait, 1e-10, Status.DONE)
