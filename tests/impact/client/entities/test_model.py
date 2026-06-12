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
        sim_opts = config["experiment"]["base"]["analysis"]["simulationOptions"]
        assert all(
            item in sim_opts.items()
            for item in {
                "dynamic_diagnostics": False,
                "ncp": 500,
            }.items()
        )
        solver_opts = config["experiment"]["base"]["analysis"]["solverOptions"]
        assert not solver_opts
        compiler_opts = config["experiment"]["base"]["model"]["modelica"][
            "compilerOptions"
        ]
        assert all(
            item in compiler_opts.items()
            for item in {
                "generate_html_diagnostics": False,
                "include_protected_variables": False,
            }.items()
        )
        runtime_opts = config["experiment"]["base"]["model"]["modelica"][
            "runtimeOptions"
        ]
        assert not runtime_opts

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


def _experiment_definition_item(modifiers, definition_id="exp_def_1"):
    return {
        "id": definition_id,
        "experiment": {
            "base": {
                "model": {"modelica": {"className": "Test.PID"}},
                "modifiers": modifiers,
                "analysis": {
                    "type": "dynamic",
                    "parameters": [],
                    "simulationOptions": {"ncp": 500},
                    "solverOptions": {},
                    "simulationLogLevel": "WARNING",
                },
            },
        },
        "metadata": {
            "name": "My definition",
            "modelName": "Test.PID",
            "projectId": IDs.PROJECT_ID_PRIMARY,
            "created": "2026-06-08T12:00:00Z",
            "lastModified": "2026-06-08T12:00:00Z",
            "isDefault": True,
            "isReadOnly": False,
        },
    }


@pytest.mark.experimental
class TestGetExperimentDefinitions:
    def _get_entries(self, model, modifiers):
        model.service.workspace.experiment_definitions_get.return_value = {
            "data": {"items": [_experiment_definition_item(modifiers)]}
        }
        model.service.custom_function.custom_function_get.return_value = {
            "name": "dynamic",
            "parameters": [],
        }
        model.service.workspace.experiment_get.return_value = {
            "id": IDs.EXPERIMENT_ID_PRIMARY
        }
        return model.entity.get_experiment_definitions()

    def test_definition_keeps_expression_variable_modifiers(self, model):
        entries = self._get_entries(
            model,
            {
                "initializeFrom": "",
                "variables": [
                    {"name": "driveAngle", "expression": "1.65806278939461138713"},
                    {"name": "PI.k", "expression": "range(10, 100, 3)"},
                ],
            },
        )
        definition_dict = entries[0].definition.to_dict()
        modifiers = definition_dict["experiment"]["base"]["modifiers"]
        assert modifiers["variables"] == [
            {
                "kind": "value",
                "name": "driveAngle",
                "value": pytest.approx(1.65806278939461138713),
                "dataType": "REAL",
            },
            {
                "kind": "range",
                "name": "PI.k",
                "start": 10.0,
                "end": 100.0,
                "steps": 3,
            },
        ]
        assert "initializeFrom" not in modifiers
        model.service.workspace.experiment_get.assert_not_called()

    def test_definition_keeps_operator_dict_variable_modifiers(self, model):
        entries = self._get_entries(
            model,
            {
                "variables": [
                    {
                        "kind": "value",
                        "name": "driveAngle",
                        "value": 1.65806278939461138713,
                        "dataType": "REAL",
                    },
                    {
                        "kind": "range",
                        "name": "PI.k",
                        "start": 10.0,
                        "end": 100.0,
                        "steps": 3,
                    },
                ],
            },
        )
        definition = entries[0].definition
        assert set(definition.modifiers) == {"driveAngle", "PI.k"}
        variables = definition.to_dict()["experiment"]["base"]["modifiers"]["variables"]
        assert variables == [
            {
                "kind": "value",
                "name": "driveAngle",
                "value": pytest.approx(1.65806278939461138713),
                "dataType": "REAL",
            },
            {
                "kind": "range",
                "name": "PI.k",
                "start": 10.0,
                "end": 100.0,
                "steps": 3,
            },
        ]

    def test_definition_keeps_initialize_from(self, model):
        entries = self._get_entries(
            model,
            {"initializeFrom": IDs.EXPERIMENT_ID_PRIMARY, "variables": []},
        )
        definition = entries[0].definition
        model.service.workspace.experiment_get.assert_called_once_with(
            IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY
        )
        definition_dict = definition.to_dict()
        modifiers = definition_dict["experiment"]["base"]["modifiers"]
        assert modifiers["initializeFrom"] == IDs.EXPERIMENT_ID_PRIMARY

    def test_definition_skips_latest_initialize_from(self, model):
        entries = self._get_entries(
            model,
            {"initializeFrom": "latest", "variables": []},
        )
        definition_dict = entries[0].definition.to_dict()
        assert (
            "initializeFrom" not in definition_dict["experiment"]["base"]["modifiers"]
        )
        model.service.workspace.experiment_get.assert_not_called()

    def test_definition_without_modifiers(self, model):
        entries = self._get_entries(model, {})
        definition_dict = entries[0].definition.to_dict()
        assert definition_dict["experiment"]["base"]["modifiers"] == {"variables": []}
