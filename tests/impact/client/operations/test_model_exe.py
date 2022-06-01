import pytest
from modelon.impact.client import exceptions
from tests.impact.client.helpers import (
    create_model_exe_entity,
    create_cached_model_exe_operation,
    create_model_exe_operation,
)
from modelon.impact.client.operations.base import Status
from tests.impact.client.fixtures import *


class TestModelExecutableOperation:
    def test_compile_wait_done(self, model_compiled, compiler_options):
        fmu = model_compiled.compile(compiler_options, force_compilation=True)
        assert fmu == create_model_exe_operation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.DONE
        assert fmu.is_complete()
        assert fmu.wait() == create_model_exe_entity(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_compile_wait_cancel_timeout(self, model_compiled, compiler_options):
        fmu = model_compiled.compile(compiler_options, force_compilation=True)
        assert fmu == create_model_exe_operation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.DONE
        assert fmu.is_complete()
        pytest.raises(
            exceptions.OperationTimeOutError, fmu.wait, 1e-10, Status.CANCELLED
        )

    def test_compile_wait_running(self, model_compiling, compiler_options):
        fmu = model_compiling.compile(compiler_options, force_compilation=True)
        assert fmu == create_model_exe_operation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.RUNNING
        assert not fmu.is_complete()
        assert fmu.wait(status=Status.RUNNING) == create_model_exe_entity(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_compile_wait_cancelled(self, model_compile_cancelled, compiler_options):
        fmu = model_compile_cancelled.compile(compiler_options, force_compilation=True)
        assert fmu == create_model_exe_operation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.CANCELLED
        assert fmu.wait(status=Status.CANCELLED) == create_model_exe_entity(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_compile_wait_timeout(self, model_compile_cancelled, compiler_options):
        fmu = model_compile_cancelled.compile(compiler_options, force_compilation=True)
        assert fmu == create_model_exe_operation('AwesomeWorkspace', 'test_pid_fmu_id')
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.CANCELLED
        pytest.raises(exceptions.OperationTimeOutError, fmu.wait, 1e-10, Status.DONE)


class TestCachedModelExecutableOperation:
    def test_cached_fmu_wait_done(self, model_cached, compiler_options):
        fmu = model_cached.compile(compiler_options, force_compilation=False)
        assert fmu == create_cached_model_exe_operation(
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
        assert fmu == create_cached_model_exe_operation(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )
        assert fmu.id == "test_pid_fmu_id"
        assert fmu.status() == Status.DONE
        pytest.raises(
            exceptions.OperationTimeOutError, fmu.wait, status=Status.CANCELLED
        )
