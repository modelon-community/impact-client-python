import collections
import unittest.mock
import pytest
import requests
import requests_mock
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from modelon.impact.client.entities import CustomFunction

MockedServer = collections.namedtuple('MockedServer', ['url', 'context', 'adapter'])


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
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST', f'{mock_server_base.url}/api/login', headers=json_header, json={}
    )

    return mock_server_base


@pytest.fixture
def api_get_metadata(mock_server_base):
    json = {"version": "1.1.0"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def sem_ver_check(mock_server_base):
    json = {"version": "1.2.1"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def login_fails(mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/',
        json=json,
        headers=json_header,
        status_code=401,
    )

    return mock_server_base


@pytest.fixture
def create_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'newWorkspace'}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def delete_workspace(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace',
        status_code=200,
    )

    return mock_server_base


@pytest.fixture
def single_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'AwesomeWorkspace'}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def multiple_workspace(sem_ver_check, mock_server_base):
    json = {'data': {'items': [{'id': 'AwesomeWorkspace'}, {'id': 'BoringWorkspace'}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/workspaces', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def workspaces_error(sem_ver_check, mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
        status_code=401,
    )

    return mock_server_base


@pytest.fixture
def create_workspace_error(sem_ver_check, mock_server_base):
    json = {'error': {'message': 'name not ok', 'code': 123}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
        status_code=400,
    )

    return mock_server_base


@pytest.fixture
def semantic_version_error(sem_ver_check, mock_server_base):
    json = {"version": "3.1.0"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_ok_empty_json(sem_ver_check, mock_server_base):
    json = {}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', mock_server_base.url, json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_with_error(sem_ver_check, mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', mock_server_base.url, json=json, headers=json_header, status_code=401,
    )

    return mock_server_base

    return mock_server_base


@pytest.fixture
def import_lib(sem_ver_check, mock_server_base):
    json = {
        "name": "Single",
        "uses": {"Modelica": {"version": "3.2.2"}, "ThermalPower": {"version": "1.14"}},
    }
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace/libraries',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def upload_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'newWorkspace'}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_export_id(sem_ver_check, mock_server_base):
    json = {"export_id": "0d96b08c8d", "file_size": 2156}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/Workspace/exports',
        json=json,
        headers=json_header,
    )


@pytest.fixture
def download_workspace(sem_ver_check, mock_server_base, get_export_id):
    content = bytes(4)
    content_header = {'content-type': 'application/zip'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/Workspace/exports/0d96b08c8d',
        content=content,
        headers=content_header,
    )

    return mock_server_base


@pytest.fixture
def lock_workspace(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST', f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace/lock',
    )

    return mock_server_base


@pytest.fixture
def unlock_workspace(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE', f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace/lock',
    )

    return mock_server_base


@pytest.fixture
def clone_workspace(sem_ver_check, mock_server_base):
    json = {"workspace_id": "clone_44e8ad8c036"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/Workspace/clone',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_fmu(sem_ver_check, mock_server_base):
    json = {"id": "pid_20090615_134"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/pid_20090615_134',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def get_all_fmu(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": "as9f-3df5"}, {"id": "as9f-3df5"}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def get_all_experiments(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": "as9f-3df5"}, {"id": "as9f-3df5"}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def get_experiment(sem_ver_check, mock_server_base):
    json = {"id": "pid_20090615_134"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_20090615_134',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def experiment_create(sem_ver_check, mock_server_base):
    json = {"experiment_id": "pid_2009"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/experiments',
        json=json,
        headers=json_header,
    )
    return mock_server_base


# Model_executeable
@pytest.fixture
def get_fmu_id(mock_server_base):
    json = {
        "id": "workspace_pid_controller_20090615_134530_as86g32",
        "parameters": {"inertia1.J": 2},
    }
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables',
        json=json,
        headers=json_header,
    )


@pytest.fixture
def model_compile(get_fmu_id, mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/'
        'workspace_pid_controller_20090615_134530_as86g32/compilation',
    )

    return mock_server_base


@pytest.fixture
def get_compile_log(sem_ver_check, mock_server_base):
    text = "Compiler arguments:..."
    header = {'content-type': 'text/plain'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/fmu_id/'
        'compilation/log',
        text=text,
        headers=header,
    )
    return mock_server_base


@pytest.fixture
def get_compile_status(sem_ver_check, mock_server_base):
    json = {
        "finished_executions": 0,
        "total_executions": 1,
        "status": "running",
        "progress": [{"message": "Compiling", "percentage": 0}],
    }
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/fmu_id/'
        'compilation',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def cancel_compile(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/fmu_id/compilation',
    )

    return mock_server_base


@pytest.fixture
def get_settable_parameters(sem_ver_check, mock_server_base):
    json = ["param1", "param3"]
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/fmu_id/'
        'settable-parameters',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def get_ss_fmu_metadata(sem_ver_check, mock_server_base):
    json = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/fmu_id/'
        'steady-state-metadata',
        json=json,
        headers=json_header,
    )
    return mock_server_base


# ExperimentService
@pytest.fixture
def experiment_execute(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/execution',
    )

    return mock_server_base


@pytest.fixture
def experiment_status(sem_ver_check, mock_server_base):
    json = {
        "finished_executions": 1,
        "total_executions": 2,
        "status": "running",
        "progress": [{"message": "Simulating at 1.0", "percentage": 1},],
    }
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/execution',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def cancel_execute(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/execution',
    )

    return mock_server_base


@pytest.fixture
def get_result_variables(sem_ver_check, mock_server_base):
    json = ["PI.J", "inertia.I"]
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/variables',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_trajectories(sem_ver_check, mock_server_base):
    json = {"variable_names": ["variable1", "variable2"]}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/trajectories',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_cases(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": "case_1"}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/cases',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_case(sem_ver_check, mock_server_base):
    json = {"id": "case_1"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/cases/case_1',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_case_log(sem_ver_check, mock_server_base):
    text = "Simulation log.."
    header = {'content-type': 'text/plain'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/cases/case_1/'
        'log',
        text=text,
        headers=header,
    )

    return mock_server_base


@pytest.fixture
def get_case_results(sem_ver_check, mock_server_base):
    binary = bytes(4)
    header = {'content-type': 'application/octet-stream'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/cases/case_1/'
        'result',
        content=binary,
        headers=header,
    )

    return mock_server_base


# CustomFunctionService
@pytest.fixture
def get_custom_function(sem_ver_check, mock_server_base):
    json = {"version": "0.0.1", "name": "cust_func"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/custom-functions/cust_func',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_custom_functions(sem_ver_check, mock_server_base):
    json = {"data": {"items": []}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/custom-functions',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_custom_function_default_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"c_compiler": "gcc"}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/custom-functions/cust_func'
        '/default-options',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_custom_function_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"generate_html_diagnostics": True}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/custom-functions/cust_func'
        '/options',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def set_custom_function_options(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/custom-functions/cust_func'
        '/options',
    )

    return mock_server_base


@pytest.fixture
def del_custom_function_options(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE',
        f'{mock_server_base.url}/api/workspaces/WS/custom-functions/cust_func'
        '/options',
    )

    return mock_server_base


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
