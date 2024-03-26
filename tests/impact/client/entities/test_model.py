import pytest

from modelon.impact.client.entities.model import Model
from tests.impact.client.helpers import (
    IDs,
    create_cached_model_exe_operation,
    create_model_exe_operation,
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
        fmu = model_compiled.compile({"c_compiler": "gcc"}, force_compilation=True)
        assert fmu == create_model_exe_operation(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)

    def test_compile_invalid_type_options(self, model_compiled):
        pytest.raises(TypeError, model_compiled.compile, [])

    def test_experiment_definition_default_execution_options(
        self, model, custom_function
    ):
        model = model.entity
        experiment_definition = model.new_experiment_definition(
            custom_function=custom_function,
        )
        config = experiment_definition.to_dict()
        assert config["experiment"]["base"]["analysis"]["simulationOptions"] == {
            "dynamic_diagnostics": False,
            "ncp": 500,
        }
        assert config["experiment"]["base"]["analysis"]["solverOptions"] == {
            "rtol": 1e-05
        }
        assert config["experiment"]["base"]["model"]["modelica"]["compilerOptions"] == {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        }
        assert config["experiment"]["base"]["model"]["modelica"]["runtimeOptions"] == {
            "log_level": 2
        }

    def test_import_fmu(self, model):
        entity = model.entity
        project_service = model.service.project
        model = entity.import_fmu("test.fmu").wait()
        expected_fmu_class_path = IDs.LOCAL_MODELICA_CLASS_PATH + ".test"
        project_service.fmu_import.assert_called_with(
            IDs.PROJECT_PRIMARY,
            IDs.PROJECT_CONTENT_PRIMARY,
            "test.fmu",
            expected_fmu_class_path,
            False,
            None,
            None,
            None,
            step_size=0.0,
        )
        assert isinstance(model, Model)
        assert model.name == expected_fmu_class_path
