import pytest

from tests.impact.client.helpers import (
    create_cached_model_exe_operation,
    create_model_exe_operation,
    IDs,
)


class TestModel:
    def test_find_cached(self, model_cached, compiler_options, runtime_options):
        fmu = model_cached.compile(compiler_options, runtime_options)
        assert fmu == create_cached_model_exe_operation(
            IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY
        )

    def test_force_compile(self, model_compiled, compiler_options, runtime_options):
        fmu = model_compiled.compile(
            compiler_options, runtime_options, force_compilation=True
        )
        assert fmu == create_model_exe_operation(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)

    def test_force_compile_dict_options(self, model_compiled):
        fmu = model_compiled.compile({'c_compiler': 'gcc'}, force_compilation=True)
        assert fmu == create_model_exe_operation(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)

    def test_compile_invalid_type_options(self, model_compiled):
        pytest.raises(TypeError, model_compiled.compile, [])

    def test_experiment_definition_default_execution_options(
        self, model, custom_function
    ):
        experiment_definition = model.new_experiment_definition(
            custom_function=custom_function,
        )
        config = experiment_definition.to_dict()
        assert config['experiment']['base']['analysis']['simulationOptions'] == {
            'dynamic_diagnostics': False,
            'ncp': 500,
        }
        assert config['experiment']['base']['analysis']['solverOptions'] == {
            'rtol': 1e-05
        }
        assert config['experiment']['base']['model']['modelica']['compilerOptions'] == {
            'c_compiler': 'gcc',
            'generate_html_diagnostics': False,
            'include_protected_variables': False,
        }
        assert config['experiment']['base']['model']['modelica']['runtimeOptions'] == {
            'log_level': 2
        }
