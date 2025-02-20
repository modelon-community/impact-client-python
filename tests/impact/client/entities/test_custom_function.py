import pytest

from modelon.impact.client.options import (
    CompilerOptions,
    RuntimeOptions,
    SimulationOptions,
    SolverOptions,
)
from tests.impact.client.helpers import (
    ClientHelper,
    IDs,
    create_case_entity,
    create_custom_artifact_uri_entity,
    create_experiment_entity,
    create_workspace_entity,
)


class TestCustomFunction:
    def _get_dynamic_cf(self, client_helper):
        workspace = client_helper.client.create_workspace(IDs.WORKSPACE_ID_SECONDARY)
        dynamic = workspace.get_custom_function("dynamic")
        return dynamic

    @pytest.mark.experimental
    def test_custom_function_with_parameters_ok(self, custom_function):
        workspace = create_workspace_entity(IDs.WORKSPACE_ID_PRIMARY)
        experiment = create_experiment_entity(
            IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY
        )
        case = create_case_entity(
            IDs.CASE_ID_PRIMARY, IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY
        )
        custom_artifact_uri = create_custom_artifact_uri_entity(
            IDs.CASE_ID_PRIMARY,
            IDs.EXPERIMENT_ID_PRIMARY,
            IDs.CUSTOM_ARTIFACT_ID,
        )
        library = "Modelica"
        resource_path = IDs.MODELICA_RESOURCE_PATH
        modelica_resource_uri = workspace.get_modelica_resource_uri(
            library, resource_path
        )
        variable_names = ["var1", "var2"]
        new = custom_function.with_parameters(
            p1=3.4,
            p2=False,
            p3="då",
            p4="new string",
            p5=4,
            p6=experiment,
            p7=case,
            p8=custom_artifact_uri,
            p9=modelica_resource_uri,
            p10=variable_names,
        )
        assert new.parameter_values == {
            "p1": 3.4,
            "p2": False,
            "p3": "då",
            "p4": "new string",
            "p5": 4.0,
            "p6": experiment,
            "p7": case,
            "p8": custom_artifact_uri,
            "p9": modelica_resource_uri,
            "p10": variable_names,
        }
        assert new.parameter_values.as_raw_dict() == {
            "p1": 3.4,
            "p2": False,
            "p3": "då",
            "p4": "new string",
            "p5": 4.0,
            "p6": experiment.id,
            "p7": f"{case.experiment_id}/{case.id}",
            "p8": str(custom_artifact_uri),
            "p9": str(modelica_resource_uri),
            "p10": variable_names,
        }

    def test_custom_function_with_parameters_no_such_parameter(self, custom_function):
        pytest.raises(ValueError, custom_function.with_parameters, does_not_exist=3.4)

    def test_custom_function_with_parameters_cannot_set_number_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p1="not a number")

    def test_custom_function_with_parameters_cannot_set_boolean_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p2="not a boolean")

    def test_custom_function_with_parameters_cannot_set_enumeration_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3=4.6)

    def test_custom_function_with_parameters_cannot_set_string_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p4=4.6)

    def test_custom_function_with_parameters_cannot_set_experiment_result_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p6=True)

    def test_custom_function_with_parameters_cannot_set_case_result_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p7="not a case")

    def test_custom_function_with_parameters_cannot_set_file_uri_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p8="not a file uri")

    def test_custom_function_with_parameters_cannot_set_enumeration_value(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3="not in values")

    def test_custom_function_with_parameters_cannot_set_variable_names_value(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p10="not in values")

    @pytest.mark.vcr()
    def test_compiler_options(self, client_helper: ClientHelper):
        dynamic_cf = self._get_dynamic_cf(client_helper)
        new = dynamic_cf.get_compiler_options().with_values(c_compiler="msvs")
        assert dict(new) == {
            "c_compiler": "msvs",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        }
        assert isinstance(new, CompilerOptions)
        defaults_options = dict(dynamic_cf.get_compiler_options(use_defaults=True))
        assert all(
            item in defaults_options.items()
            for item in {
                "generate_html_diagnostics": False,
                "include_protected_variables": False,
            }.items()
        )

    @pytest.mark.vcr()
    def test_runtime_options(self, client_helper: ClientHelper):
        dynamic_cf = self._get_dynamic_cf(client_helper)
        new = dynamic_cf.get_runtime_options().with_values(cs_solver=0)
        assert dict(new) == {"cs_solver": 0}
        assert isinstance(new, RuntimeOptions)
        defaults = dynamic_cf.get_runtime_options(use_defaults=True)
        assert dict(defaults) == {}

    @pytest.mark.vcr()
    def test_simulation_options(self, client_helper: ClientHelper):
        dynamic_cf = self._get_dynamic_cf(client_helper)
        new = dynamic_cf.get_simulation_options().with_values(ncp=5000)
        assert dict(new) == {"ncp": 5000, "dynamic_diagnostics": False}
        assert isinstance(new, SimulationOptions)
        defaults = dynamic_cf.get_simulation_options(use_defaults=True)
        assert dict(defaults) == {"ncp": 500, "dynamic_diagnostics": False}

    @pytest.mark.vcr()
    def test_solver_options(self, client_helper: ClientHelper):
        dynamic_cf = self._get_dynamic_cf(client_helper)
        new = dynamic_cf.get_solver_options().with_values(atol=1e-7, rtol=1e-9)
        assert dict(new) == {"atol": 1e-7, "rtol": 1e-9}
        assert isinstance(new, SolverOptions)
        defaults = dynamic_cf.get_solver_options(use_defaults=True)
        assert dict(defaults) == {}
