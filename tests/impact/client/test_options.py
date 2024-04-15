import pytest

from tests.impact.client.helpers import ClientHelper, IDs


class TestClient:
    @pytest.mark.vcr()
    def test_modify_options(self, client_helper: ClientHelper):
        dynamic = self._get_dynamic_custom_function(client_helper)
        simulation_opts = dynamic.get_simulation_options().with_values(ncp=10)
        runtime_opts = dynamic.get_runtime_options().with_values(log_level=1)
        solver_opts = dynamic.get_solver_options().with_values(rtol=50)
        compiler_opts = dynamic.get_compiler_options().with_values(c_compiler=4)

        assert dict(compiler_opts) == {
            "c_compiler": 4,
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        }
        assert dict(runtime_opts) == {"log_level": 1}
        assert dict(simulation_opts) == {"ncp": 10, "dynamic_diagnostics": False}
        assert dict(solver_opts) == {"rtol": 50}

    def _get_dynamic_custom_function(self, client_helper):
        workspace = client_helper.client.create_workspace(IDs.WORKSPACE_ID_PRIMARY)
        dynamic = workspace.get_custom_function("dynamic")
        return dynamic

    @pytest.mark.vcr()
    def test_append_options(self, client_helper: ClientHelper):
        dynamic = self._get_dynamic_custom_function(client_helper)
        simulation_opts = dynamic.get_simulation_options().with_values(a=10)
        runtime_opts = dynamic.get_runtime_options().with_values(b="hello")
        solver_opts = dynamic.get_solver_options().with_values(c=5.0)
        compiler_opts = dynamic.get_compiler_options().with_values(d=True)

        assert dict(compiler_opts) == {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
            "d": True,
        }
        assert dict(runtime_opts) == {"b": "hello"}
        assert dict(simulation_opts) == {
            "ncp": 500,
            "dynamic_diagnostics": False,
            "a": 10,
        }
        assert dict(solver_opts) == {"c": 5.0}

    @pytest.mark.vcr()
    def test_simulation_options_with_result_filter(self, client_helper: ClientHelper):
        dynamic = self._get_dynamic_custom_function(client_helper)
        simulation_opts = dynamic.get_simulation_options().with_result_filter(
            filter=["*.phi"]
        )
        assert dict(simulation_opts) == {
            "ncp": 500,
            "dynamic_diagnostics": False,
            "filter": "['*.phi']",
        }

    @pytest.mark.vcr()
    def test_simulation_options_with_result_filter_invalid_string_imput(
        self, client_helper: ClientHelper
    ):
        dynamic = self._get_dynamic_custom_function(client_helper)
        with pytest.raises(ValueError):
            dynamic.get_simulation_options().with_result_filter(filter="*.phi")

    @pytest.mark.vcr()
    def test_simulation_options_with_result_filter_invalid_list_imput(
        self, client_helper: ClientHelper
    ):
        dynamic = self._get_dynamic_custom_function(client_helper)
        with pytest.raises(ValueError):
            dynamic.get_simulation_options().with_result_filter(filter=["*.phi", 2])
