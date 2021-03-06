import pytest
from modelon.impact.client import exceptions

from modelon.impact.client.entities import ModelExecutable, Experiment
from modelon.impact.client.operations import (
    Status,
    CachedModelExecutableOperation,
    ModelExecutableOperation,
)
from tests.impact.client.fixtures import *


class TestModelExecutableOperation:
    def test_compile_wait_done(self, model_compiled, compiler_options):
        fmu = model_compiled.compile(compiler_options, force_compilation=True)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.DONE
        assert fmu.is_complete()
        assert fmu.wait() == ModelExecutable('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_compile_wait_cancel_timeout(self, model_compiled, compiler_options):
        fmu = model_compiled.compile(compiler_options, force_compilation=True)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.DONE
        assert fmu.is_complete()
        pytest.raises(
            exceptions.OperationTimeOutError, fmu.wait, 1e-10, Status.CANCELLED
        )

    def test_compile_wait_running(self, model_compiling, compiler_options):
        fmu = model_compiling.compile(compiler_options, force_compilation=True)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.RUNNING
        assert not fmu.is_complete()
        assert fmu.wait(status=Status.RUNNING) == ModelExecutable(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_compile_wait_cancelled(self, model_compile_cancelled, compiler_options):
        fmu = model_compile_cancelled.compile(compiler_options, force_compilation=True)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.CANCELLED
        assert fmu.wait(status=Status.CANCELLED) == ModelExecutable(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_compile_wait_timeout(self, model_compile_cancelled, compiler_options):
        fmu = model_compile_cancelled.compile(compiler_options, force_compilation=True)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, fmu.wait, 1e-10, Status.DONE)


class TestCachedModelExecutableOperation:
    def test_cached_fmu_wait_done(self, model_cached, compiler_options):
        fmu = model_cached.compile(compiler_options, force_compilation=False)
        assert fmu == CachedModelExecutableOperation(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.name == "Looking for cached FMU"
        assert fmu.status() == Status.DONE
        assert fmu.is_complete()
        assert fmu.wait() == ModelExecutable('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_cached_fmu_wait_cancelled(self, model_cached, compiler_options):
        fmu = model_cached.compile(compiler_options, force_compilation=False)
        assert fmu == CachedModelExecutableOperation(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.DONE
        pytest.raises(
            exceptions.OperationTimeOutError, fmu.wait, status=Status.CANCELLED
        )


class TestExperimentOperation:
    def test_execute_wait_done(
        self, workspace,
    ):
        exp = workspace.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.DONE
        assert exp.is_complete()
        assert exp.wait() == Experiment('AwesomeWorkspace', 'pid_2009')

    def test_execute_wait_cancel_timeout(self, workspace):
        exp = workspace.execute({})
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
        assert exp.wait(status=Status.RUNNING) == Experiment(
            'AwesomeWorkspace', 'pid_2009'
        )

    def test_execute_wait_cancelled(self, workspace_execute_cancelled):
        exp = workspace_execute_cancelled.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.CANCELLED
        assert exp.wait(status=Status.CANCELLED) == Experiment(
            'AwesomeWorkspace', 'pid_2009'
        )

    def test_execute_wait_timeout(self, workspace_execute_cancelled):
        exp = workspace_execute_cancelled.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, exp.wait, 1e-10, Status.DONE)
