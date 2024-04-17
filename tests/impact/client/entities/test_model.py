import pytest

from modelon.impact.client.entities.model import Model
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.operations.model_executable import (
    CachedModelExecutableOperation,
    ModelExecutableOperation,
)
from tests.files.paths import get_archived_modelica_lib_path
from tests.impact.client.helpers import ClientHelper, IDs


class TestModel:
    def _compile_fmu(
        self,
        client_helper: ClientHelper,
        force_compilation=False,
        compiler_options_override=None,
        runtime_options_override=None,
        fmi_target="me",
    ):
        workspace = client_helper.workspace
        dynamic = workspace.get_custom_function("dynamic")
        compiler_options = dynamic.get_compiler_options().with_values(c_compiler="gcc")
        runtime_options = None
        model = workspace.get_model(IDs.PID_MODELICA_CLASS_PATH)
        if compiler_options_override is not None:
            compiler_options = compiler_options_override
        if runtime_options_override is not None:
            runtime_options = runtime_options_override
        fmu_ops = model.compile(
            compiler_options,
            runtime_options=runtime_options,
            force_compilation=force_compilation,
            fmi_target=fmi_target,
        )
        return fmu_ops

    @pytest.mark.vcr()
    def test_find_cached(self, client_helper: ClientHelper):
        fmu_ops_1 = self._compile_fmu(client_helper)
        assert isinstance(fmu_ops_1, ModelExecutableOperation)

        # Wait for completetion
        fmu_1 = fmu_ops_1.wait()
        assert isinstance(fmu_1, ModelExecutable)

        fmu_ops_2 = self._compile_fmu(client_helper)
        assert isinstance(fmu_ops_2, CachedModelExecutableOperation)

        # Wait for completetion
        fmu_2 = fmu_ops_2.wait()
        assert isinstance(fmu_2, ModelExecutable)
        assert fmu_1.id == fmu_2.id

    @pytest.mark.vcr()
    def test_force_compile(self, client_helper: ClientHelper):
        fmu_ops_1 = self._compile_fmu(client_helper)
        assert isinstance(fmu_ops_1, ModelExecutableOperation)

        # Wait for completetion
        fmu_1 = fmu_ops_1.wait()
        assert isinstance(fmu_1, ModelExecutable)

        fmu_ops_2 = self._compile_fmu(client_helper, force_compilation=True)

        # Wait for completetion
        fmu_2 = fmu_ops_2.wait()
        assert fmu_2.id != fmu_1.id

    @pytest.mark.vcr()
    def test_force_compile_dict_options(self, client_helper: ClientHelper):
        fmu = self._compile_fmu(
            client_helper, compiler_options_override={"c_compiler": "gcc"}
        ).wait()
        assert isinstance(fmu, ModelExecutable)

    @pytest.mark.vcr()
    def test_compile_invalid_compiler_options_type(self, client_helper: ClientHelper):
        with pytest.raises(TypeError):
            self._compile_fmu(client_helper, compiler_options_override=[]).wait()

    @pytest.mark.vcr()
    def test_compile_invalid_runtime_options_type(self, client_helper: ClientHelper):
        with pytest.raises(TypeError):
            self._compile_fmu(client_helper, runtime_options_override=[]).wait()

    @pytest.mark.vcr()
    def test_experiment_definition_default_execution_options(
        self, client_helper: ClientHelper
    ):
        workspace = client_helper.workspace
        model = workspace.get_model(IDs.PID_MODELICA_CLASS_PATH)
        dynamic = workspace.get_custom_function("dynamic")
        experiment_definition = model.new_experiment_definition(
            custom_function=dynamic,
        )
        config = experiment_definition.to_dict()
        assert config["experiment"]["base"]["analysis"]["simulationOptions"] == {
            "dynamic_diagnostics": False,
            "ncp": 500,
        }
        assert config["experiment"]["base"]["analysis"]["solverOptions"] == {}
        assert config["experiment"]["base"]["model"]["modelica"]["compilerOptions"] == {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        }
        assert config["experiment"]["base"]["model"]["modelica"]["runtimeOptions"] == {}

    @pytest.mark.vcr()
    def test_import_fmu(self, tmpdir, client_helper: ClientHelper):
        fmu = self._compile_fmu(
            client_helper,
            compiler_options_override={"c_compiler": "gcc"},
            fmi_target="cs",
        ).wait()
        fmu_path = fmu.download(tmpdir)

        prj = client_helper.workspace.get_default_project()
        library_path = get_archived_modelica_lib_path(tmpdir)
        prj.import_modelica_library(library_path).wait()

        package = client_helper.workspace.get_model("Dynamic")
        expected_fmu_class_path = "Dynamic." + IDs.PID_MODELICA_CLASS_PATH.replace(
            ".", "_"
        )
        model = package.import_fmu(fmu_path, expected_fmu_class_path).wait()
        assert isinstance(model, Model)
        assert model.name == expected_fmu_class_path
