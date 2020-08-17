import collections
import unittest.mock
import pytest
import requests
import requests_mock
import modelon.impact.client
from modelon.impact.client.entities import CustomFunction

MockedServer = collections.namedtuple('MockedServer', ['url', 'context', 'adapter'])


def with_json_route(mock_server_base, method, url, json_response, status_code=200):
    json = json_response
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        method,
        f'{mock_server_base.url}/{url}',
        json=json,
        headers=json_header,
        status_code=status_code,
    )
    return mock_server_base


def with_json_route_no_resp(mock_server_base, method, url, status_code=200):
    mock_server_base.adapter.register_uri(
        method, f'{mock_server_base.url}/{url}', status_code=status_code,
    )
    return mock_server_base


def with_zip_route(mock_server_base, method, url, zip_response, status_code=200):
    content = zip_response
    content_header = {'content-type': 'application/zip'}
    mock_server_base.adapter.register_uri(
        method,
        f'{mock_server_base.url}/{url}',
        content=content,
        headers=content_header,
        status_code=status_code,
    )
    return mock_server_base


def with_text_route(mock_server_base, method, url, text_response, status_code=200):
    text = text_response
    text_header = {'content-type': 'text/plain'}
    mock_server_base.adapter.register_uri(
        method,
        f'{mock_server_base.url}/{url}',
        text=text,
        headers=text_header,
        status_code=status_code,
    )
    return mock_server_base


def with_octet_stream_route(
    mock_server_base, method, url, octet_response, status_code=200
):
    content = octet_response
    content_header = {'content-type': 'application/octet-stream'}
    mock_server_base.adapter.register_uri(
        method,
        f'{mock_server_base.url}/{url}',
        content=content,
        headers=content_header,
        status_code=status_code,
    )
    return mock_server_base


class MockContex:
    def __init__(self, session):
        self.session = session


@pytest.fixture
def mock_server_base():
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount('http://', adapter)
    mock_url = 'http://mock-impact.com'

    mock_server_base = MockedServer(mock_url, MockContex(session), adapter)

    return with_json_route(mock_server_base, 'POST', 'api/login', {})


@pytest.fixture
def api_get_metadata(mock_server_base):
    json = {"version": "1.1.0"}

    return with_json_route(mock_server_base, 'GET', 'api/', json)


@pytest.fixture
def sem_ver_check(mock_server_base):
    json = {"version": "1.4.1"}

    return with_json_route(mock_server_base, 'GET', 'api/', json)


@pytest.fixture
def login_fails(mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}

    return with_json_route(mock_server_base, 'GET', 'api/', json, 401)


@pytest.fixture
def create_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'newWorkspace'}

    return with_json_route(mock_server_base, 'POST', 'api/workspaces', json)


@pytest.fixture
def delete_workspace(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'DELETE', 'api/workspaces/AwesomeWorkspace'
    )


@pytest.fixture
def single_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'AwesomeWorkspace'}

    return with_json_route(
        mock_server_base, 'GET', 'api/workspaces/AwesomeWorkspace', json
    )


@pytest.fixture
def multiple_workspace(sem_ver_check, mock_server_base):
    json = {'data': {'items': [{'id': 'AwesomeWorkspace'}, {'id': 'BoringWorkspace'}]}}

    return with_json_route(mock_server_base, 'GET', 'api/workspaces', json)


@pytest.fixture
def workspaces_error(sem_ver_check, mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}

    return with_json_route(mock_server_base, 'GET', 'api/workspaces', json, 401)


@pytest.fixture
def create_workspace_error(sem_ver_check, mock_server_base):
    json = {'error': {'message': 'name not ok', 'code': 123}}

    return with_json_route(mock_server_base, 'POST', 'api/workspaces', json, 400)


@pytest.fixture
def semantic_version_error(sem_ver_check, mock_server_base):
    json = {"version": "3.1.0"}

    return with_json_route(mock_server_base, 'GET', 'api/', json)


@pytest.fixture
def get_ok_empty_json(sem_ver_check, mock_server_base):

    return with_json_route(mock_server_base, 'GET', '', {})


@pytest.fixture
def get_with_error(sem_ver_check, mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}

    return with_json_route(mock_server_base, 'GET', '', json, 401)


@pytest.fixture
def import_lib(sem_ver_check, mock_server_base):
    json = {
        "name": "Single",
        "uses": {"Modelica": {"version": "3.2.2"}, "ThermalPower": {"version": "1.14"}},
    }

    return with_json_route(
        mock_server_base, 'POST', 'api/workspaces/AwesomeWorkspace/libraries', json
    )


@pytest.fixture
def upload_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'newWorkspace'}

    return with_json_route(mock_server_base, 'POST', 'api/workspaces', json)


@pytest.fixture
def get_export_id(sem_ver_check, mock_server_base):
    json = {"export_id": "0d96b08c8d", "file_size": 2156}

    return with_json_route(
        mock_server_base, 'POST', 'api/workspaces/Workspace/exports', json
    )


@pytest.fixture
def download_workspace(sem_ver_check, mock_server_base, get_export_id):
    content = bytes(4)

    return with_zip_route(
        mock_server_base, 'GET', 'api/workspaces/Workspace/exports/0d96b08c8d', content
    )


@pytest.fixture
def lock_workspace(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'POST', 'api/workspaces/AwesomeWorkspace/lock'
    )


@pytest.fixture
def unlock_workspace(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'DELETE', 'api/workspaces/AwesomeWorkspace/lock'
    )


@pytest.fixture
def clone_workspace(sem_ver_check, mock_server_base):
    json = {"workspace_id": "clone_44e8ad8c036"}

    return with_json_route(
        mock_server_base, 'POST', 'api/workspaces/Workspace/clone', json
    )


@pytest.fixture
def get_fmu(sem_ver_check, mock_server_base):
    json = {"id": "pid_20090615_134"}

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/model-executables/pid_20090615_134',
        json,
    )


@pytest.fixture
def get_all_fmu(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": "as9f-3df5"}, {"id": "as9f-3df5"}]}}

    return with_json_route(
        mock_server_base, 'GET', 'api/workspaces/WS/model-executables', json
    )


@pytest.fixture
def get_all_experiments(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": "as9f-3df5"}, {"id": "as9f-3df5"}]}}

    return with_json_route(
        mock_server_base, 'GET', 'api/workspaces/WS/experiments', json
    )


@pytest.fixture
def get_experiment(sem_ver_check, mock_server_base):
    json = {"id": "pid_20090615_134"}

    return with_json_route(
        mock_server_base, 'GET', 'api/workspaces/WS/experiments/pid_20090615_134', json
    )


@pytest.fixture
def experiment_create(sem_ver_check, mock_server_base):
    json = {"experiment_id": "pid_2009"}

    return with_json_route(
        mock_server_base, 'POST', 'api/workspaces/WS/experiments', json
    )


@pytest.fixture
def get_fmu_id(mock_server_base):
    json = {
        "id": "workspace_pid_controller_20090615_134530_as86g32",
        "parameters": {"inertia1.J": 2},
    }

    return with_json_route(
        mock_server_base, 'POST', 'api/workspaces/WS/model-executables', json
    )


@pytest.fixture
def model_compile(get_fmu_id, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'POST',
        'api/workspaces/WS/model-executables/'
        'workspace_pid_controller_20090615_134530_as86g32/compilation',
    )


@pytest.fixture
def get_compile_log(sem_ver_check, mock_server_base):
    text = "Compiler arguments:..."

    return with_text_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/model-executables/fmu_id/compilation/log',
        text,
    )


@pytest.fixture
def get_compile_status(sem_ver_check, mock_server_base):
    json = {
        "finished_executions": 0,
        "total_executions": 1,
        "status": "running",
        "progress": [{"message": "Compiling", "percentage": 0}],
    }

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/model-executables/fmu_id/compilation',
        json,
    )


@pytest.fixture
def cancel_compile(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'DELETE',
        'api/workspaces/WS/model-executables/fmu_id/compilation',
    )


@pytest.fixture
def get_settable_parameters(sem_ver_check, mock_server_base):
    json = ["param1", "param3"]

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/model-executables/fmu_id/settable-parameters',
        json,
    )


@pytest.fixture
def get_ss_fmu_metadata(sem_ver_check, mock_server_base):
    json = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/model-executables/fmu_id/steady-state-metadata',
        json,
    )


@pytest.fixture
def experiment_execute(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'POST', 'api/workspaces/WS/experiments/pid_2009/execution'
    )


@pytest.fixture
def experiment_status(sem_ver_check, mock_server_base):
    json = {
        "finished_executions": 1,
        "total_executions": 2,
        "status": "running",
        "progress": [{"message": "Simulating at 1.0", "percentage": 1}],
    }

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/experiments/pid_2009/execution',
        json,
    )


@pytest.fixture
def cancel_execute(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'DELETE', 'api/workspaces/WS/experiments/pid_2009/execution'
    )


@pytest.fixture
def get_result_variables(sem_ver_check, mock_server_base):
    json = ["PI.J", "inertia.I"]

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/experiments/pid_2009/variables',
        json,
    )


@pytest.fixture
def get_trajectories(sem_ver_check, mock_server_base):
    json = {"variable_names": ["variable1", "variable2"]}

    return with_json_route(
        mock_server_base,
        'POST',
        'api/workspaces/WS/experiments/pid_2009/trajectories',
        json,
    )


@pytest.fixture
def get_cases(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": "case_1"}]}}

    return with_json_route(
        mock_server_base, 'GET', 'api/workspaces/WS/experiments/pid_2009/cases', json
    )


@pytest.fixture
def get_case(sem_ver_check, mock_server_base):
    json = {"id": "case_1"}

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/experiments/pid_2009/cases/case_1',
        json,
    )


@pytest.fixture
def get_case_log(sem_ver_check, mock_server_base):
    text = "Simulation log.."

    return with_text_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/experiments/pid_2009/cases/case_1/log',
        text,
    )


@pytest.fixture
def get_case_results(sem_ver_check, mock_server_base):
    binary = bytes(4)

    return with_octet_stream_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/experiments/pid_2009/cases/case_1/result',
        binary,
    )


@pytest.fixture
def get_custom_function(sem_ver_check, mock_server_base):
    json = {"version": "0.0.1", "name": "cust_func"}

    return with_json_route(
        mock_server_base, 'GET', 'api/workspaces/WS/custom-functions/cust_func', json
    )


@pytest.fixture
def get_custom_functions(sem_ver_check, mock_server_base):
    json = {"data": {"items": []}}

    return with_json_route(
        mock_server_base, 'GET', 'api/workspaces/WS/custom-functions', json
    )


@pytest.fixture
def get_custom_function_default_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"c_compiler": "gcc"}}

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/custom-functions/cust_func/default-options',
        json,
    )


@pytest.fixture
def get_custom_function_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"generate_html_diagnostics": True}}

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/custom-functions/cust_func/options',
        json,
    )


@pytest.fixture
def set_custom_function_options(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'POST', 'api/workspaces/WS/custom-functions/cust_func/options'
    )


@pytest.fixture
def del_custom_function_options(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'DELETE',
        'api/workspaces/WS/custom-functions/cust_func/options',
    )


@pytest.fixture
def custom_function_parameter_list():
    return [
        {'name': 'p1', 'defaultValue': 1.0, 'type': 'Number'},
        {'name': 'p2', 'defaultValue': True, 'type': 'Boolean'},
        {
            'name': 'p3',
            'defaultValue': 'hej',
            'type': 'Enumeration',
            'values': ['hej', 'då'],
        },
        {'name': 'p4', 'defaultValue': 'a string', 'type': 'String'},
    ]


@pytest.fixture
def custom_function(custom_function_parameter_list):
    custom_function_service = unittest.mock.MagicMock()
    return CustomFunction(
        'ws', 'test', custom_function_parameter_list, custom_function_service
    )


@pytest.fixture
def custom_function_no_param():
    custom_function_service = unittest.mock.MagicMock()
    return CustomFunction("test_ws", 'dynamic', [], custom_function_service)


@pytest.fixture
def model():
    return modelon.impact.client.entities.Model('Test.PID', "test_ws")


@pytest.fixture
def options():
    custom_function_service = unittest.mock.MagicMock()
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {"log_level": 3},
        "simulation": {"ncp": 2000},
        "solver": {"rtol": 0.0001},
    }
    def_opts = {
        "compiler": {"c_compiler": "msvs"},
        "runtime": {"log_level": 2},
        "simulation": {"ncp": 500},
        "solver": {"rtol": 1e-5},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    custom_function_service.custom_function_default_options_get.return_value = def_opts
    return modelon.impact.client.options.ExecutionOption(
        "test_ws", opts, "dynamic", custom_function_service
    )


@pytest.fixture
def workspace(single_workspace):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspace = client.get_workspace('AwesomeWorkspace')
    return workspace


@pytest.fixture
def fmu():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "successful"}}
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.settable_parameters_get.return_value = ['h0', 'v']
    model_exe_service.compile_log.return_value = "Successful Log"
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return modelon.impact.client.operations.ModelExecutable(
        "Workspace", "Test", ws_service, model_exe_service
    )


@pytest.fixture
def fmu_compile_running():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "running"}}
    model_exe_service.compile_status.return_value = {"status": "running"}
    return modelon.impact.client.operations.ModelExecutable(
        "Workspace", "Test", ws_service, model_exe_service
    )


@pytest.fixture
def fmu_compile_failed():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "failed"}}
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.compile_log.return_value = "Failed Log"
    return modelon.impact.client.operations.ModelExecutable(
        "Workspace", "Test", ws_service, model_exe_service
    )


@pytest.fixture
def fmu_compile_failed_empty_log():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "failed"}}
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.compile_log.return_value = ""
    return modelon.impact.client.operations.ModelExecutable(
        "Workspace", "Test", ws_service, model_exe_service
    )


@pytest.fixture
def fmu_compile_cancelled():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "cancelled"}}
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return modelon.impact.client.operations.ModelExecutable(
        "Workspace", "Test", ws_service, model_exe_service
    )


@pytest.fixture
def experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 0, "successful": 1, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["PI.J", "inertia.I", "time"]
    exp_service.case_get_log.return_value = "Successful Log"
    exp_service.cases_get.return_value = {"data": {"items": [{"id": "case_1"}]}}
    exp_service.case_get.return_value = {"id": "case_1"}
    exp_service.trajectories_get.return_value = [[[1, 2, 3, 4]], [[5, 2, 9, 4]]]
    return modelon.impact.client.operations.Experiment(
        "Workspace", "Test", ws_service, exp_service
    )


@pytest.fixture
def batch_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 0, "successful": 1, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["PI.J", "inertia.I", "time"]
    exp_service.cases_get.return_value = {
        "data": {"items": [{"id": "case_1"}, {"id": "case_2"}]}
    }
    exp_service.trajectories_get.return_value = [
        [[1, 2, 3, 4], [1, 2, 3, 4]],
        [[5, 2, 9, 4], [1, 2, 3, 4]],
    ]
    return modelon.impact.client.operations.Experiment(
        "Workspace", "Test", ws_service, exp_service
    )


@pytest.fixture
def running_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    exp_service.execute_status.return_value = {"status": "running"}
    exp_service.case_get_log.return_value = ""
    return modelon.impact.client.operations.Experiment(
        "Workspace", "Test", ws_service, exp_service
    )


@pytest.fixture
def failed_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 1, "successful": 0, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.case_get_log.return_value = "Failed Log"
    exp_service.cases_get.return_value = {"data": {"items": [{"id": "case_1"}]}}
    exp_service.case_get.return_value = {"id": "case_1"}
    return modelon.impact.client.operations.Experiment(
        "Workspace", "Test", ws_service, exp_service
    )


@pytest.fixture
def cancelled_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 1, "successful": 0, "cancelled": 1}
    }
    exp_service.cases_get.return_value = {"data": {"items": [{"id": "case_1"}]}}
    exp_service.case_get.return_value = {"id": "case_1"}
    exp_service.execute_status.return_value = {"status": "cancelled"}
    exp_service.case_get_log.return_value = ""
    return modelon.impact.client.operations.Experiment(
        "Workspace", "Test", ws_service, exp_service
    )


@pytest.fixture
def case():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 0, "successful": 1, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.case_get.return_value = {
        "id": "case_1",
        "run_info": {"status": "successful"},
    }
    exp_service.case_get_log.return_value = "Successful Log"
    exp_service.case_result_get.return_value = bytes(4)
    return modelon.impact.client.operations.Case(
        "case_1", "Workspace", "Test", exp_service, ws_service
    )
