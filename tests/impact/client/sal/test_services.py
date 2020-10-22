import pytest
import modelon.impact.client.sal.service
import modelon.impact.client.sal.exceptions
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH, TEST_WORKSPACE_PATH
from tests.impact.client.fixtures import *


class TestService:
    def test_api_get_meta_data(self, api_get_metadata):
        uri = modelon.impact.client.sal.service.URI(api_get_metadata.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=api_get_metadata.context
        )
        data = service.api_get_metadata()
        assert data == {'version': '1.1.0'}


class TestWorkspaceService:
    def test_create_workspace(self, create_workspace):
        uri = modelon.impact.client.sal.service.URI(create_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace.context
        )
        data = service.workspace.workspace_create('AwesomeWorkspace')
        assert data == {'id': 'newWorkspace'}

    def test_delete_workspace(self, delete_workspace):
        uri = modelon.impact.client.sal.service.URI(delete_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_workspace.context
        )
        service.workspace.workspace_delete('AwesomeWorkspace')
        assert delete_workspace.adapter.called

    def test_get_workspace(self, single_workspace):
        uri = modelon.impact.client.sal.service.URI(single_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_workspace.context
        )
        data = service.workspace.workspace_get('AwesomeWorkspace')
        assert data == {'id': 'AwesomeWorkspace'}

    def test_get_workspaces(self, multiple_workspace):
        uri = modelon.impact.client.sal.service.URI(multiple_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_workspace.context
        )
        data = service.workspace.workspaces_get()
        assert data == {
            'data': {'items': [{'id': 'AwesomeWorkspace'}, {'id': 'BoringWorkspace'}]}
        }

    def test_library_import(self, import_lib):
        uri = modelon.impact.client.sal.service.URI(import_lib.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_lib.context
        )
        service.workspace.library_import('AwesomeWorkspace', SINGLE_FILE_LIBRARY_PATH)
        assert import_lib.adapter.called

    def test_workspace_upload(self, upload_workspace):
        uri = modelon.impact.client.sal.service.URI(upload_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_workspace.context
        )
        data = service.workspace.workspace_upload(TEST_WORKSPACE_PATH)
        assert data == {'id': 'newWorkspace'}

    def test_workspace_download(self, download_workspace):
        uri = modelon.impact.client.sal.service.URI(download_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=download_workspace.context
        )
        data = service.workspace.workspace_download("Workspace", '0d96b08c8d')
        assert data == b'\x00\x00\x00\x00'

    def test_lock_workspace(self, lock_workspace):
        uri = modelon.impact.client.sal.service.URI(lock_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=lock_workspace.context
        )
        service.workspace.workspace_lock("AwesomeWorkspace")
        assert lock_workspace.adapter.called

    def test_unlock_workspace(self, unlock_workspace):
        uri = modelon.impact.client.sal.service.URI(unlock_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=unlock_workspace.context
        )
        service.workspace.workspace_unlock("AwesomeWorkspace")
        assert unlock_workspace.adapter.called

    def test_clone_workspace(self, clone_workspace):
        uri = modelon.impact.client.sal.service.URI(clone_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=clone_workspace.context
        )
        data = service.workspace.workspace_clone("Workspace")
        assert data == {'workspace_id': 'clone_44e8ad8c036'}

    def test_get_fmu(self, get_fmu):
        uri = modelon.impact.client.sal.service.URI(get_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_fmu.context
        )
        data = service.workspace.fmu_get("WS", "pid_20090615_134")
        assert data == {'id': 'pid_20090615_134'}

    def test_get_fmus(self, get_all_fmu):
        uri = modelon.impact.client.sal.service.URI(get_all_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_fmu.context
        )
        data = service.workspace.fmus_get("WS")
        assert data == {'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9f-3df5'}]}}

    def test_fmu_download(self, download_fmu):
        uri = modelon.impact.client.sal.service.URI(download_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=download_fmu.context
        )
        data = service.workspace.fmu_download("WS", 'pid_20090615_134')
        assert data == b'\x00\x00\x00\x00'

    def test_get_experiment(self, get_experiment):
        uri = modelon.impact.client.sal.service.URI(get_experiment.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_experiment.context
        )
        data = service.workspace.experiment_get("WS", 'pid_20090615_134')
        assert data == {'id': 'pid_20090615_134'}

    def test_get_experiments(self, get_all_experiments):
        uri = modelon.impact.client.sal.service.URI(get_all_experiments.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_experiments.context
        )
        data = service.workspace.experiments_get("WS")
        assert data == {'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9f-3df5'}]}}

    def test_create_experiment(self, experiment_create):
        uri = modelon.impact.client.sal.service.URI(experiment_create.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_create.context
        )
        data = service.workspace.experiment_create("WS", {})
        assert experiment_create.adapter.called
        assert data == {"experiment_id": "pid_2009"}


class TestModelExecutbleService:
    def test_compile_model(self, model_compile):
        uri = modelon.impact.client.sal.service.URI(model_compile.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=model_compile.context
        )
        options = {
            "input": {
                "class_name": "Workspace.PID_Controller",
                "compiler_options": {},
                "runtime_options": {"log_level": 4},
                "compiler_log_level": "warning",
                "fmi_target": "me",
                "fmi_version": "2.0",
                "platform": "win64",
            }
        }
        service.model_executable.compile_model("WS", options)
        assert model_compile.adapter.called

    def test_get_compile_log(self, get_compile_log):
        uri = modelon.impact.client.sal.service.URI(get_compile_log.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_compile_log.context
        )
        data = service.model_executable.compile_log("WS", "fmu_id")
        assert data == "Compiler arguments:..."

    def test_get_compile_status(self, get_compile_status):
        uri = modelon.impact.client.sal.service.URI(get_compile_status.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_compile_status.context
        )
        data = service.model_executable.compile_status("WS", "fmu_id")
        assert data == {
            "finished_executions": 0,
            "total_executions": 1,
            "status": "running",
            "progress": [{"message": "Compiling", "percentage": 0}],
        }

    def test_cancel_compile(self, cancel_compile):
        uri = modelon.impact.client.sal.service.URI(cancel_compile.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=cancel_compile.context
        )
        service.model_executable.compile_cancel("WS", "fmu_id")
        assert cancel_compile.adapter.called

    def test_get_settable_parameters(self, get_settable_parameters):
        uri = modelon.impact.client.sal.service.URI(get_settable_parameters.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_settable_parameters.context
        )
        data = service.model_executable.settable_parameters_get("WS", "fmu_id")
        assert data == ["param1", "param3"]

    def test_get_ss_fmu_metadata(self, get_ss_fmu_metadata):
        uri = modelon.impact.client.sal.service.URI(get_ss_fmu_metadata.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_ss_fmu_metadata.context
        )
        data = service.model_executable.ss_fmu_metadata_get("WS", "fmu_id")
        assert data == {
            "steady_state": {
                "residual_variable_count": 1,
                "iteration_variable_count": 2,
            }
        }


class TestExperimentService:
    def test_model_execute(self, experiment_execute):
        uri = modelon.impact.client.sal.service.URI(experiment_execute.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_execute.context
        )
        service.experiment.experiment_execute("WS", "pid_2009")
        assert experiment_execute.adapter.called

    def test_get_experiment_status(self, experiment_status):
        uri = modelon.impact.client.sal.service.URI(experiment_status.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_status.context
        )
        data = service.experiment.execute_status("WS", "pid_2009")
        assert data == {
            "finished_executions": 1,
            "total_executions": 2,
            "status": "running",
            "progress": [{"message": "Simulating at 1.0", "percentage": 1},],
        }

    def test_cancel_execute(self, cancel_execute):
        uri = modelon.impact.client.sal.service.URI(cancel_execute.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=cancel_execute.context
        )
        service.experiment.execute_cancel("WS", "pid_2009")
        assert cancel_execute.adapter.called

    def test_get_result_variables(self, get_result_variables):
        uri = modelon.impact.client.sal.service.URI(get_result_variables.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_result_variables.context
        )
        data = service.experiment.result_variables_get("WS", "pid_2009")
        assert data == ["PI.J", "inertia.I"]

    def test_get_trajectories(self, get_trajectories):
        uri = modelon.impact.client.sal.service.URI(get_trajectories.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_trajectories.context
        )
        data = service.experiment.trajectories_get(
            "WS", "pid_2009", ["variable1", "variable2"]
        )
        assert data == [[[1.0, 1.0], [3.0, 3.0], [5.0, 5.0]]]

    def test_get_cases(self, get_cases):
        uri = modelon.impact.client.sal.service.URI(get_cases.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_cases.context
        )
        data = service.experiment.cases_get("WS", "pid_2009")
        assert data == {"data": {"items": [{"id": "case_1"}]}}

    def test_get_case(self, get_case):
        uri = modelon.impact.client.sal.service.URI(get_case.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case.context
        )
        data = service.experiment.case_get("WS", "pid_2009", "case_1")
        assert data == {"id": "case_1"}

    def test_get_case_log(self, get_case_log):
        uri = modelon.impact.client.sal.service.URI(get_case_log.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case_log.context
        )
        data = service.experiment.case_get_log("WS", "pid_2009", "case_1")
        assert data == 'Simulation log..'

    def test_get_case_result(self, get_case_results):
        uri = modelon.impact.client.sal.service.URI(get_case_results.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case_results.context
        )
        data, name = service.experiment.case_result_get("WS", "pid_2009", "case_1")
        assert data == b'\x00\x00\x00\x00'
        assert name == 'Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.csv'

    def test_case_get_trajectories(self, get_case_trajectories):
        uri = modelon.impact.client.sal.service.URI(get_case_trajectories.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case_trajectories.context
        )
        data = service.experiment.case_trajectories_get(
            "WS", "pid_2009", "case_1", ["variable1", "variable2"]
        )
        assert data == [[1.0, 2.0, 7.0], [2.0, 3.0, 5.0]]


class TestCustomFunctionService:
    def test_get_custom_function(self, get_custom_function):
        uri = modelon.impact.client.sal.service.URI(get_custom_function.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_function.context
        )
        data = service.custom_function.custom_function_get('WS', 'cust_func')
        assert data == {'name': 'cust_func', 'version': '0.0.1'}

    def test_get_custom_functions(self, get_custom_functions):
        uri = modelon.impact.client.sal.service.URI(get_custom_functions.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_functions.context
        )
        data = service.custom_function.custom_functions_get('WS')
        assert data == {"data": {"items": []}}

    def test_get_custom_function_default_options(
        self, get_custom_function_default_options
    ):
        uri = modelon.impact.client.sal.service.URI(
            get_custom_function_default_options.url
        )
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_function_default_options.context
        )
        data = service.custom_function.custom_function_default_options_get(
            'WS', 'cust_func'
        )
        assert data == {'compiler': {'c_compiler': 'gcc'}}

    def test_get_custom_function_options(self, get_custom_function_options):
        uri = modelon.impact.client.sal.service.URI(get_custom_function_options.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_custom_function_options.context
        )
        data = service.custom_function.custom_function_options_get('WS', 'cust_func')
        assert data == {"compiler": {"generate_html_diagnostics": True}}

    def test_set_custom_function_set_options(self, set_custom_function_options):
        uri = modelon.impact.client.sal.service.URI(set_custom_function_options.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=set_custom_function_options.context
        )
        service.custom_function.custom_function_options_set('WS', 'cust_func', {})
        assert set_custom_function_options.adapter.called

    def test_del_custom_function_options(self, del_custom_function_options):
        uri = modelon.impact.client.sal.service.URI(del_custom_function_options.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=del_custom_function_options.context
        )
        service.custom_function.custom_function_options_delete('WS', 'cust_func', {})
        assert del_custom_function_options.adapter.called


class TestHTTPClient:
    def test_get_json_error(self, get_with_error):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_with_error.context
        )
        pytest.raises(
            modelon.impact.client.sal.exceptions.HTTPError,
            client.get_json,
            get_with_error.url,
        )

    def test_get_json_ok(self, get_ok_empty_json):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_ok_empty_json.context
        )
        data = client.get_json(get_ok_empty_json.url)
        assert data == {}

    def test_ssl_error_mapping(self, get_with_ssl_exception):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_with_ssl_exception.context
        )
        pytest.raises(
            modelon.impact.client.sal.exceptions.SSLError,
            client.get_json,
            get_with_ssl_exception.url,
        )
