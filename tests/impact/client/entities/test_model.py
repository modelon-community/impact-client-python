import pytest

from tests.impact.client.helpers import (
    create_cached_model_exe_operation,
    create_model_exe_operation,
)
from tests.impact.client.fixtures import *


class TestModel:
    def test_find_cached(self, model_cached, compiler_options, runtime_options):
        fmu = model_cached.compile(compiler_options, runtime_options)
        assert fmu == create_cached_model_exe_operation(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_force_compile(self, model_compiled, compiler_options, runtime_options):
        fmu = model_compiled.compile(
            compiler_options, runtime_options, force_compilation=True
        )
        assert fmu == create_model_exe_operation('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_force_compile_dict_options(self, model_compiled):
        fmu = model_compiled.compile({'c_compiler': 'gcc'}, force_compilation=True)
        assert fmu == create_model_exe_operation('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_compile_invalid_type_options(self, model_compiled):
        pytest.raises(TypeError, model_compiled.compile, [])
