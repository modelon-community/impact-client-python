import pytest
from modelon.impact.client import exceptions

from modelon.impact.client.entities import (
    Case,
    ModelExecutable,
    Experiment,
    ExternalResult,
)
from modelon.impact.client.operations import (
    ExternalResultUploadOperation,
    Status,
    AsyncOperationStatus,
    CachedModelExecutableOperation,
    ModelExecutableOperation,
)
from unittest import mock
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
        self,
        workspace,
    ):
        exp = workspace.entity.execute({})
        assert exp.id == "pid_2009"
        assert exp.status() == Status.DONE
        assert exp.is_complete()
        assert exp.wait() == Experiment('AwesomeWorkspace', 'pid_2009')

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


class TestCaseOperation:
    def test_execute_wait_done(
        self,
        experiment,
    ):
        case = experiment.entity.get_case('case_1')
        case_ops = case.execute()
        assert case_ops.id == "case_1"
        assert case_ops.status() == Status.DONE
        assert case_ops.is_complete()
        assert case_ops.wait() == Case('case_1', 'Workspace', 'Test', 'pid_2009')

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
        assert case_ops.wait(status=Status.RUNNING) == Case(
            'case_1', 'Workspace', 'Test', 'pid_2009'
        )

    def test_execute_wait_cancelled(self, experiment_cancelled):
        case = experiment_cancelled.get_case('case_1')
        case = case.execute()
        assert case.id == "case_1"
        assert case.status() == Status.CANCELLED
        assert case.wait(status=Status.CANCELLED) == Case(
            'case_1', 'Workspace', 'Test', 'pid_2009'
        )

    def test_execute_wait_timeout(self, experiment_cancelled):
        case = experiment_cancelled.get_case('case_1')
        case = case.execute()
        assert case.id == "case_1"
        assert case.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, case.wait, 1e-10, Status.DONE)


class TestExternalResultUploadOperation:
    def test_result_upload_ops(
        self, workspace_ops, upload_result, upload_result_status_ready
    ):
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            result_ops = workspace_ops.upload_result("test.mat", "Workspace")
            mock_file.assert_called_with("test.mat", "rb")
        assert isinstance(result_ops, ExternalResultUploadOperation)
        assert result_ops.id == '2f036b9fab6f45c788cc466da327cc78workspace'
        assert result_ops.status() == AsyncOperationStatus.READY
        assert result_ops.status().done()
        assert result_ops.wait() == ExternalResult(
            '2f036b9fab6f45c788cc466da327cc78workspace'
        )
        pytest.raises(NotImplementedError, result_ops.cancel)

    def test_execute_wait_timeout(
        self, workspace_ops, upload_result, upload_result_status_running
    ):
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            result_ops = workspace_ops.upload_result("test.mat", "Workspace")
            mock_file.assert_called_with("test.mat", "rb")
        pytest.raises(exceptions.OperationTimeOutError, result_ops.wait, 1)
