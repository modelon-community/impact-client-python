import pytest
from modelon.impact.client import exceptions
from tests.impact.client.helpers import (
    create_case_entity,
    create_model_exe_entity,
    create_experiment_entity,
    create_external_result_entity,
)
from modelon.impact.client.operations import (
    ExternalResultUploadOperation,
    Status,
    AsyncOperationStatus,
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
        assert fmu.wait() == create_model_exe_entity(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

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
        assert fmu.wait(status=Status.RUNNING) == create_model_exe_entity(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_compile_wait_cancelled(self, model_compile_cancelled, compiler_options):
        fmu = model_compile_cancelled.compile(compiler_options, force_compilation=True)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.CANCELLED
        assert fmu.wait(status=Status.CANCELLED) == create_model_exe_entity(
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
        assert fmu.wait() == create_model_exe_entity(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

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


class TestCaseOperation:
    def test_execute_wait_done(self, experiment):
        case = experiment.entity.get_case('case_1')
        case_ops = case.execute()
        assert case_ops.id == "case_1"
        assert case_ops.status() == Status.DONE
        assert case_ops.is_complete()
        assert case_ops.wait() == create_case_entity(
            'case_1', 'Workspace', 'Test', 'pid_2009'
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
            'case_1', 'Workspace', 'Test', 'pid_2009',
        )

    def test_execute_wait_cancelled(self, experiment_cancelled):
        case = experiment_cancelled.get_case('case_1')
        case = case.execute()
        assert case.id == "case_1"
        assert case.status() == Status.CANCELLED
        assert case.wait(status=Status.CANCELLED) == create_case_entity(
            'case_1', 'Workspace', 'Test', 'pid_2009',
        )

    def test_execute_wait_timeout(self, experiment_cancelled):
        case = experiment_cancelled.get_case('case_1')
        case = case.execute()
        assert case.id == "case_1"
        assert case.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, case.wait, 1e-10, Status.DONE)


class TestExternalResultUploadOperation:
    def test_given_running_when_wait_then_timeout(
        self, workspace_sal_upload_result_running
    ):
        # Given
        workspace_service = workspace_sal_upload_result_running
        upload_op = ExternalResultUploadOperation(
            '2f036b9fab6f45c788cc466da327cc78workspace', workspace_service
        )

        # When, then
        pytest.raises(exceptions.OperationTimeOutError, upload_op.wait, 1)

    def test_given_ready_when_wait_then_ok(self, workspace_sal_upload_result_ready):
        # Given
        workspace_service = workspace_sal_upload_result_ready
        upload_op = ExternalResultUploadOperation(
            '2f036b9fab6f45c788cc466da327cc78workspace', workspace_service
        )

        # When
        result = upload_op.wait()

        # Then
        assert isinstance(upload_op, ExternalResultUploadOperation)
        assert upload_op.id == '2f036b9fab6f45c788cc466da327cc78workspace'
        assert upload_op.status() == AsyncOperationStatus.READY
        assert upload_op.status().done()
        assert result == create_external_result_entity(
            '2f036b9fab6f45c788cc466da327cc78workspace'
        )
        meta = result.metadata
        assert meta.id == "2f036b9fab6f45c788cc466da327cc78workspace"
        assert meta.name == "result_for_PID"
        assert meta.description == "This is a result file for PID controller"
        assert meta.workspace_id == "workspace"
        assert result.id == "2f036b9fab6f45c788cc466da327cc78workspace"

    def test_give_status_ready_when_cancel_then_raises_not_implemented(
        self, workspace_sal_upload_result_ready
    ):
        # Given
        workspace_service = workspace_sal_upload_result_ready
        upload_op = ExternalResultUploadOperation(
            '2f036b9fab6f45c788cc466da327cc78workspace', workspace_service
        )

        # When, then
        pytest.raises(NotImplementedError, upload_op.cancel)
