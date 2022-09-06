import collections
import copy
from unittest.mock import MagicMock
import pytest
import requests
import requests_mock
from modelon.impact.client import Client
from modelon.impact.client.options import (
    CompilerOptions,
    SimulationOptions,
    SolverOptions,
    RuntimeOptions,
)
from tests.impact.client.helpers import (
    create_project_entity,
    create_workspace_entity,
    create_model_exe_entity,
    create_experiment_entity,
    create_custom_function_entity,
    create_model_entity,
    get_test_workspace_definition,
    IDs,
    VERSIONED_PROJECT_BRANCH,
    VERSIONED_PROJECT_TRUNK,
)

MockedServer = collections.namedtuple('MockedServer', ['url', 'context', 'adapter'])
ExperimentMock = collections.namedtuple('ExperimentMock', ['entity', 'service'])
WorkspaceMock = collections.namedtuple('WorkspaceMock', ['entity', 'service'])
ProjectMock = collections.namedtuple('ProjectMock', ['entity', 'service'])


def json_request_list_item(json_response, status_code=200, extra_headers=None):
    extra_headers = extra_headers or {}
    json_header = {'content-type': 'application/json', **extra_headers}
    return {'json': json_response, 'status_code': status_code, 'headers': json_header}


def with_json_route(
    mock_server_base, method, url, json_response, status_code=200, extra_headers=None
):
    request_list = [json_request_list_item(json_response, status_code, extra_headers)]
    return with_json_request_list_route(mock_server_base, method, url, request_list)


def with_json_request_list_route(mock_server_base, method, url, request_list):
    mock_server_base.adapter.register_uri(
        method, f'{mock_server_base.url}/{url}', request_list
    )
    return mock_server_base


def with_exception(mock_server_base, method, url, exce):
    mock_server_base.adapter.register_uri(
        method, f'{mock_server_base.url}/{url}', exc=exce
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


def with_csv_route(
    mock_server_base, method, url, text_response, status_code=200, content_header=None
):
    text = text_response
    content_header = (
        {
            'content-type': 'text/csv',
            'content-disposition': 'attachment; '
            'filename="BouncingBall_2020-09-01_14-33_case_1.csv"',
            'connection': 'close',
            'date': 'Tue, 01 Sep 2020 14:33:56 GMT',
            'server': '127.0.0.1',
            'Transfer-Encoding': 'chunked',
        }
        if content_header is None
        else content_header
    )
    mock_server_base.adapter.register_uri(
        method,
        f'{mock_server_base.url}/{url}',
        text=text,
        headers=content_header,
        status_code=status_code,
    )
    return mock_server_base


def with_mat_stream_route(
    mock_server_base, method, url, mat_response, status_code=200, content_header=None
):
    content = mat_response
    content_header = (
        {
            'content-type': 'application/vnd.impact.mat.v1+octet-stream',
            'content-disposition': 'attachment; '
            'filename="BouncingBall_2020-09-01_14-33_case_1.mat"',
            'connection': 'close',
            'date': 'Tue, 01 Sep 2020 14:33:56 GMT',
            'server': '127.0.0.1',
            'Transfer-Encoding': 'chunked',
        }
        if content_header is None
        else content_header
    )
    mock_server_base.adapter.register_uri(
        method,
        f'{mock_server_base.url}/{url}',
        content=content,
        headers=content_header,
        status_code=status_code,
    )
    return mock_server_base


def with_octet_stream_route(
    mock_server_base, method, url, octet_response, status_code=200, content_header=None
):
    content = octet_response
    content_header = (
        {
            'content-type': 'application/octet-stream',
            'content-disposition': 'attachment; '
            'filename="BouncingBall_2020-09-01_14-33_case_1.mat"',
            'connection': 'close',
            'date': 'Tue, 01 Sep 2020 14:33:56 GMT',
            'server': '127.0.0.1',
            'Transfer-Encoding': 'chunked',
        }
        if content_header is None
        else content_header
    )
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
    json = {"version": "1.21.3"}
    return with_json_route(mock_server_base, 'GET', 'api/', json)


@pytest.fixture
def user_with_license(sem_ver_check):
    json = {'data': {'license': 'impact-pro'}}
    return with_json_route(sem_ver_check, 'GET', 'api/users/me', json)


@pytest.fixture
def user_with_no_license(sem_ver_check):
    json = {'data': {}}
    return with_json_route(sem_ver_check, 'GET', 'api/users/me', json)


@pytest.fixture
def login_fails(mock_server_base):
    json = {'error': {'message': 'no authorization', 'code': 123}}

    return with_json_route(mock_server_base, 'POST', 'api/login', json, 401)


@pytest.fixture
def jupyterhub_api(mock_server_base):
    jupyter_api_json = {"version": "1.3.0"}
    jupyter_user_json = {'name': 'user-name', 'server': 'ok'}
    impact_api_json = {"version": "1.99.99"}

    mock_server = with_json_route(
        mock_server_base,
        'GET',
        'api/',
        jupyter_api_json,
        extra_headers={'x-jupyterhub-version': '1.3.0'},
    )
    mock_server = with_json_route(
        mock_server,
        'GET',
        'hub/api/authorizations/token/secret-token',
        jupyter_user_json,
    )
    mock_server = with_json_route(
        mock_server, 'GET', 'user/user-name/impact/api/', impact_api_json
    )
    mock_server = with_json_route(
        mock_server, 'POST', 'user/user-name/impact/api/login', {}
    )
    mock_server = with_json_route(
        mock_server,
        'GET',
        'user/user-name/impact/api/users/me',
        {'data': {'license': 'impact-pro'}},
    )
    return mock_server


@pytest.fixture
def create_workspace(user_with_license):
    json = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_PRIMARY,
    }
    return with_json_route(user_with_license, 'POST', 'api/workspaces', json)


@pytest.fixture
def create_workspace_fail_auth_once(sem_ver_check, mock_server_base):
    json_error = {'error': {'code': 123456, 'message': 'JWT expired'}}
    json_ok = {'id': IDs.WORKSPACE_PRIMARY}
    request_list = [
        json_request_list_item(json_error, 401),
        json_request_list_item(json_ok, 200),
    ]

    return with_json_request_list_route(
        mock_server_base, 'POST', 'api/workspaces', request_list
    )


@pytest.fixture
def create_workspace_fail_auth_many(sem_ver_check, mock_server_base):
    json_error = {'error': {'code': 123456, 'message': 'JWT expired'}}
    request_list = [
        json_request_list_item(json_error, 401),
        json_request_list_item(json_error, 401),
    ]

    return with_json_request_list_route(
        mock_server_base, 'POST', 'api/workspaces', request_list
    )


@pytest.fixture
def create_workspace_fail_bad_input(sem_ver_check, mock_server_base):
    json_error = {'error': {'code': 123456, 'message': 'Not an allowed workspace name'}}
    return with_json_route(mock_server_base, 'POST', 'api/workspaces', json_error, 400)


@pytest.fixture
def delete_workspace(user_with_license):

    return with_json_route_no_resp(
        user_with_license, 'DELETE', f'api/workspaces/{IDs.WORKSPACE_PRIMARY}'
    )


@pytest.fixture
def single_workspace(user_with_license):
    json = {"definition": get_test_workspace_definition(), "id": IDs.WORKSPACE_PRIMARY}
    return with_json_route(
        user_with_license, 'GET', f'api/workspaces/{IDs.WORKSPACE_PRIMARY}', json
    )


@pytest.fixture
def multiple_workspace(user_with_license):
    workspace_1_def = get_test_workspace_definition(IDs.WORKSPACE_PRIMARY)
    workspace_2_def = get_test_workspace_definition(IDs.WORKSPACE_SECONDARY)
    json = {
        'data': {
            'items': [
                {'id': 'workspace_1', "definition": workspace_1_def},
                {'id': 'workspace_2', "definition": workspace_2_def},
            ]
        }
    }

    return with_json_route(user_with_license, 'GET', 'api/workspaces', json)


@pytest.fixture
def workspaces_error(user_with_license):
    json = {'error': {'message': 'no authorization', 'code': 123}}

    return with_json_route(user_with_license, 'GET', 'api/workspaces', json, 401)


@pytest.fixture
def create_workspace_error(user_with_license):
    json = {'error': {'message': 'name not ok', 'code': 123}}

    return with_json_route(user_with_license, 'POST', 'api/workspaces', json, 400)


@pytest.fixture
def semantic_version_error(mock_server_base):
    json = {"version": "4.1.0"}

    return with_json_route(mock_server_base, 'GET', 'api/', json)


@pytest.fixture
def get_ok_empty_json(mock_server_base):

    return with_json_route(mock_server_base, 'GET', '', {})


@pytest.fixture
def get_with_error(mock_server_base):
    json = {'error': {'message': 'no authorization', 'code': 123}}

    return with_json_route(mock_server_base, 'GET', '', json, 401)


@pytest.fixture
def get_with_ssl_exception(mock_server_base):
    return with_exception(mock_server_base, 'GET', '', requests.exceptions.SSLError)


@pytest.fixture
def import_lib(sem_ver_check):
    json = {
        "name": "Single",
        "uses": {"Modelica": {"version": "3.2.2"}, "ThermalPower": {"version": "1.14"}},
    }

    return with_json_route(
        sem_ver_check, 'POST', f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/libraries', json
    )


@pytest.fixture
def import_fmu(sem_ver_check):
    json = {
        "fmuClassPath": "Workspace.PID_Controller.Model",
        "importWarnings": [
            "Specified argument for 'top_level_inputs=['a']' does not match any variable"
        ],
        "library": {
            'project_id': IDs.PROJECT_PRIMARY,
            'content_id': IDs.PROJECT_CONTENT_PRIMARY,
        },
    }

    return with_json_route(
        sem_ver_check,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/projects/{IDs.PROJECT_PRIMARY}/content/{IDs.PROJECT_CONTENT_PRIMARY}/models',
        json,
    )


def get_upload_result_ready_data():
    return {
        "data": {
            "id": "2f036b9fab6f45c788cc466da327cc78workspace",
            "status": "ready",
            "data": {
                "resourceUri": "api/external-result/2f036b9fab6f45c788cc466da327cc78workspace"
            },
        }
    }


def get_upload_result_running_data():
    return {
        "data": {
            "id": "2f036b9fab6f45c788cc466da327cc78workspace",
            "status": "running",
            "data": {
                "resourceUri": "api/external-result/2f036b9fab6f45c788cc466da327cc78workspace"
            },
        }
    }


def get_result_upload_post_data():
    return {
        "data": {
            "id": "2f036b9fab6f45c788cc466da327cc78workspace",
            "status": "running",
        }
    }


def get_external_result_data():
    return {
        "data": {
            "id": "2f036b9fab6f45c788cc466da327cc78workspace",
            "createdAt": "2021-09-02T08:26:49.612000",
            "name": "result_for_PID",
            "description": "This is a result file for PID controller",
            "workspaceId": IDs.WORKSPACE_PRIMARY,
        }
    }


@pytest.fixture
def workspace_sal_upload_base():
    workspace_service = MagicMock()
    workspace_service.result_upload.return_value = get_result_upload_post_data()
    workspace_service.get_uploaded_result_meta.return_value = get_external_result_data()

    return workspace_service


@pytest.fixture
def workspace_sal_upload_result_ready(workspace_sal_upload_base):
    workspace_sal_upload_base.get_result_upload_status.return_value = (
        get_upload_result_ready_data()
    )

    return workspace_sal_upload_base


@pytest.fixture
def workspace_sal_upload_result_running(workspace_sal_upload_base):
    workspace_sal_upload_base.get_result_upload_status.return_value = (
        get_upload_result_running_data()
    )

    return workspace_sal_upload_base


@pytest.fixture
def upload_result_status_ready(sem_ver_check, mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        'api/uploads/results/2f036b9fab6f45c788cc466da327cc78workspace',
        get_upload_result_ready_data(),
    )


@pytest.fixture
def upload_result_status_running(sem_ver_check, mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        'api/uploads/results/2f036b9fab6f45c788cc466da327cc78workspace',
        get_upload_result_running_data(),
    )


@pytest.fixture
def upload_result(sem_ver_check, mock_server_base):
    return with_json_route(
        mock_server_base, 'POST', 'api/uploads/results', get_result_upload_post_data()
    )


@pytest.fixture
def upload_result_meta(sem_ver_check, mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        'api/external-result/2f036b9fab6f45c788cc466da327cc78workspace',
        get_external_result_data(),
    )


@pytest.fixture
def upload_result_delete(sem_ver_check, mock_server_base):
    return with_json_route_no_resp(
        mock_server_base,
        'DELETE',
        'api/external-result/2f036b9fab6f45c788cc466da327cc78workspace',
    )


@pytest.fixture
def upload_workspace(sem_ver_check, mock_server_base):
    json = {'id': IDs.WORKSPACE_PRIMARY}

    return with_json_route(mock_server_base, 'POST', 'api/workspaces', json)


@pytest.fixture
def get_export_id(sem_ver_check, mock_server_base):
    json = {"export_id": "0d96b08c8d", "file_size": 2156}

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/exports',
        json,
    )


@pytest.fixture
def download_workspace(sem_ver_check, mock_server_base, get_export_id):
    content = bytes(4)

    return with_zip_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/exports/0d96b08c8d',
        content,
    )


# TODO: Cloning workspace is not implemented on feature branch
# @pytest.fixture
# def clone_workspace(sem_ver_check, mock_server_base):
#     json = {"workspace_id": "clone_44e8ad8c036"}

#     return with_json_route(
#         mock_server_base, 'POST', 'api/workspaces/Workspace/clone', json
#     )


@pytest.fixture
def get_fmu(sem_ver_check, mock_server_base):
    json = {"id": IDs.FMU_PRIMARY}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}',
        json,
    )


@pytest.fixture
def get_all_fmu(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": IDs.FMU_PRIMARY}, {"id": IDs.FMU_SECONDARY}]}}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables',
        json,
    )


@pytest.fixture
def download_fmu(sem_ver_check, mock_server_base):
    content = bytes(4)

    return with_zip_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}/binary',
        content,
    )


@pytest.fixture
def get_projects(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "items": [
                {"id": IDs.PROJECT_PRIMARY, "definition": {}, "projectType": "LOCAL",}
            ]
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/projects',
        json,
    )


@pytest.fixture
def create_project(sem_ver_check, mock_server_base):
    json = {
        "id": IDs.PROJECT_PRIMARY,
        "definition": {
            "name": "my_project",
            "format": "1.0",
            "dependencies": [],
            "content": [],
            "executionOptions": [],
        },
        "projectType": "LOCAL",
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/projects',
        json,
    )


@pytest.fixture
def get_dependencies(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "items": [
                {
                    "id": IDs.MSL_300_PROJECT_ID,
                    "definition": {},
                    "projectType": "SYSTEM",
                },
            ]
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/dependencies',
        json,
    )


@pytest.fixture
def get_all_experiments(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "items": [{"id": IDs.EXPERIMENT_PRIMARY}, {"id": IDs.EXPERIMENT_SECONDARY}]
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments',
        json,
    )


@pytest.fixture
def get_experiment(sem_ver_check, mock_server_base):
    json = {"id": IDs.EXPERIMENT_PRIMARY}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}',
        json,
    )


@pytest.fixture
def experiment_create(sem_ver_check, mock_server_base):
    json = {"experiment_id": IDs.EXPERIMENT_PRIMARY}

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments',
        json,
    )


@pytest.fixture
def no_cached_fmu_id(mock_server_base):
    json = {
        "id": None,
        "parameters": {},
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables?getCached=true',
        json,
    )


@pytest.fixture
def get_fmu_id(mock_server_base):
    json = {
        "id": IDs.FMU_PRIMARY,
        "parameters": {"inertia1.J": 2},
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables',
        json,
    )


@pytest.fixture
def model_compile(get_fmu_id, no_cached_fmu_id, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}/compilation',
    )


@pytest.fixture
def get_cached_fmu_id(mock_server_base):
    json = {
        "id": IDs.FMU_PRIMARY,
        "parameters": {},
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables?getCached=true',
        json,
    )


@pytest.fixture
def get_compile_log(sem_ver_check, mock_server_base):
    text = "Compiler arguments:..."

    return with_text_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}/compilation/log',
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
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}/compilation',
        json,
    )


@pytest.fixture
def cancel_compile(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'DELETE',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}/compilation',
    )


@pytest.fixture
def get_settable_parameters(sem_ver_check, mock_server_base):
    json = ["param1", "param3"]

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}/settable-parameters',
        json,
    )


@pytest.fixture
def get_ss_fmu_metadata(sem_ver_check, mock_server_base):
    json = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}/steady-state-metadata',
        json,
    )


@pytest.fixture
def delete_fmu(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'DELETE',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/{IDs.FMU_PRIMARY}',
    )


@pytest.fixture
def experiment_execute(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/execution',
    )


@pytest.fixture
def set_experiment_label(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'PUT',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}',
    )


@pytest.fixture
def delete_experiment(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'DELETE',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}',
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
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/execution',
        json,
    )


@pytest.fixture
def cancel_execute(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'DELETE',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/execution',
    )


@pytest.fixture
def get_result_variables(sem_ver_check, mock_server_base):
    json = ["PI.J", "inertia.I"]

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/variables',
        json,
    )


@pytest.fixture
def get_trajectories(sem_ver_check, mock_server_base):
    json = [[[1.0, 1.0], [3.0, 3.0], [5.0, 5.0]]]

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/trajectories',
        json,
    )


@pytest.fixture
def get_cases(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": "case_1"}]}}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases',
        json,
    )


@pytest.fixture
def get_case(sem_ver_check, mock_server_base):
    json = {"id": "case_1"}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases/case_1',
        json,
    )


@pytest.fixture
def put_case(sem_ver_check, mock_server_base):
    json = {"id": "case_1"}

    return with_json_route(
        mock_server_base,
        'PUT',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases/case_1',
        json,
    )


@pytest.fixture
def get_case_log(sem_ver_check, mock_server_base):
    text = "Simulation log.."

    return with_text_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases/case_1/log',
        text,
    )


@pytest.fixture
def get_mat_case_results(sem_ver_check, mock_server_base):
    binary = bytes(4)

    return with_octet_stream_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases/case_1/result',
        binary,
        content_header={
            'X-Powered-By': 'Express',
            'content-type': 'application/vnd.impact.mat.v1+octet-stream',
            'content-disposition': 'attachment; filename="Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.mat"',
            'connection': 'close',
            'date': 'Thu, 22 Oct 2020 06:03:46 GMT',
            'server': '127.0.0.1',
            'Content-Length': '540',
            'ETag': 'W/"21c-YYNaLhSng67+inxuWx+DHndUdno"',
            'Vary': 'Accept-Encoding',
        },
    )


@pytest.fixture
def get_csv_case_results(sem_ver_check, mock_server_base):
    text = "1;2;3"

    return with_csv_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases/case_1/result',
        text,
        content_header={
            'X-Powered-By': 'Express',
            'content-type': 'text/csv',
            'content-disposition': 'attachment; filename="Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.csv"',
            'connection': 'close',
            'date': 'Thu, 22 Oct 2020 06:03:46 GMT',
            'server': '127.0.0.1',
            'Content-Length': '540',
            'ETag': 'W/"21c-YYNaLhSng67+inxuWx+DHndUdno"',
            'Vary': 'Accept-Encoding',
        },
    )


@pytest.fixture
def get_case_artifact(sem_ver_check, mock_server_base):
    binary = bytes(4)

    return with_octet_stream_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases/case_1/custom-artifacts/ABCD',
        binary,
        content_header={
            'X-Powered-By': 'Express',
            'content-type': 'application/octet-stream',
            'content-disposition': 'attachment; filename="Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.mat"',
            'connection': 'close',
            'date': 'Thu, 22 Oct 2020 06:03:46 GMT',
            'server': '127.0.0.1',
            'Content-Length': '540',
            'ETag': 'W/"21c-YYNaLhSng67+inxuWx+DHndUdno"',
            'Vary': 'Accept-Encoding',
        },
    )


@pytest.fixture
def get_case_trajectories(sem_ver_check, mock_server_base):
    json = [[1.0, 2.0, 7.0], [2.0, 3.0, 5.0]]

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments/{IDs.EXPERIMENT_PRIMARY}/cases/case_1/trajectories',
        json,
    )


@pytest.fixture
def get_custom_function(sem_ver_check, mock_server_base):
    json = {"version": "0.0.1", "name": "cust_func"}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/custom-functions/cust_func',
        json,
    )


@pytest.fixture
def get_custom_functions(sem_ver_check, mock_server_base):
    json = {"data": {"items": []}}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/custom-functions',
        json,
    )


@pytest.fixture
def get_custom_function_default_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"c_compiler": "gcc"}}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/custom-functions/cust_func/default-options',
        json,
    )


@pytest.fixture
def get_custom_function_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"generate_html_diagnostics": True}}

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/custom-functions/cust_func/options',
        json,
    )


def _custom_function_parameter_list():
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
        {'name': 'p5', 'defaultValue': 0.0, 'type': 'Number'},
    ]


@pytest.fixture
def workspace():
    ws_service = MagicMock()
    custom_function_service = MagicMock()
    exp_service = MagicMock()
    project_service = MagicMock()
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_PRIMARY
    }
    # TODO: Cloning workspace is not implemented on feature branch
    # ws_service.workspace_clone.return_value = {"workspace_id": "MyClonedWorkspace"}
    ws_service.fmus_get.return_value = {
        'data': {'items': [{'id': IDs.FMU_PRIMARY}, {'id': IDs.FMU_SECONDARY}]}
    }
    ws_service.fmu_get.return_value = {'id': IDs.FMU_PRIMARY}
    ws_service.project_create.return_value = {
        "id": IDs.PROJECT_PRIMARY,
        "definition": {
            "name": "my_project",
            "format": "1.0",
            "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
            "content": [
                {
                    "id": IDs.PROJECT_CONTENT_PRIMARY,
                    "relpath": "MyPackage",
                    "contentType": "MODELICA",
                    "name": "MyPackage",
                    "defaultDisabled": False,
                }
            ],
            "executionOptions": [],
        },
        "projectType": "LOCAL",
    }
    ws_service.experiment_get.return_value = {'id': IDs.EXPERIMENT_PRIMARY}
    exp_service.execute_status.return_value = {"status": "done"}
    ws_service.experiments_get.return_value = {
        'data': {
            'items': [{'id': IDs.EXPERIMENT_PRIMARY}, {'id': IDs.EXPERIMENT_SECONDARY}]
        }
    }
    ws_service.workspace_download.return_value = b'\x00\x00\x00\x00'
    ws_service.workspace_get.return_value = get_test_workspace_definition()
    ws_service.projects_get.return_value = {
        "data": {
            "items": [
                {
                    "id": IDs.PROJECT_PRIMARY,
                    "definition": {
                        "name": "NewProject",
                        "format": "1.0",
                        "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
                        "content": [
                            {
                                "id": IDs.PROJECT_CONTENT_PRIMARY,
                                "relpath": "MyPackage",
                                "contentType": "MODELICA",
                                "name": "MyPackage",
                                "defaultDisabled": False,
                            },
                        ],
                        "executionOptions": [],
                    },
                    "projectType": "LOCAL",
                }
            ]
        }
    }
    ws_service.dependencies_get.return_value = {
        "data": {
            "items": [
                {
                    "id": IDs.MSL_300_PROJECT_ID,
                    "definition": {
                        "name": "MSL",
                        "version": "3.2.3",
                        "format": "1.0",
                        "dependencies": [],
                        "content": [
                            {
                                "id": IDs.MSL_CONTENT_ID,
                                "relpath": "Modelica",
                                "contentType": "MODELICA",
                                "name": "Modelica",
                                "defaultDisabled": False,
                            }
                        ],
                        "executionOptions": [],
                    },
                    "projectType": "SYSTEM",
                },
                {
                    "id": IDs.MSL_400_PROJECT_ID,
                    "definition": {
                        "name": "MSL",
                        "version": "4.0.0",
                        "format": "1.0",
                        "dependencies": [],
                        "content": [
                            {
                                "id": IDs.MSL_CONTENT_ID,
                                "relpath": "Modelica",
                                "contentType": "MODELICA",
                                "name": "Modelica",
                                "defaultDisabled": False,
                            }
                        ],
                        "executionOptions": [],
                    },
                    "projectType": "SYSTEM",
                },
            ]
        }
    }
    custom_function_service.custom_function_get.return_value = {
        'name': 'dynamic',
        'parameters': _custom_function_parameter_list(),
    }
    custom_function_service.custom_functions_get.return_value = {
        'data': {
            'items': [
                {'name': 'dynamic', 'parameters': _custom_function_parameter_list()}
            ]
        }
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    project_service.project_get.return_value = {
        "id": IDs.PROJECT_PRIMARY,
        "definition": {
            "name": "NewProject",
            "format": "1.0",
            "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
            "content": [
                {
                    "id": IDs.PROJECT_CONTENT_PRIMARY,
                    "relpath": "MyPackage",
                    "contentType": "MODELICA",
                    "name": "MyPackage",
                    "defaultDisabled": False,
                }
            ],
            "executionOptions": [],
        },
        "projectType": "LOCAL",
    }
    return WorkspaceMock(
        create_workspace_entity(
            IDs.WORKSPACE_PRIMARY,
            workspace_service=ws_service,
            experiment_service=exp_service,
            custom_function_service=custom_function_service,
            project_service=project_service,
        ),
        ws_service,
    )


@pytest.fixture
def workspace_execute_running():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_PRIMARY
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "running"}
    return create_workspace_entity(
        IDs.WORKSPACE_PRIMARY,
        workspace_service=ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def workspace_execute_cancelled():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_PRIMARY
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return create_workspace_entity(
        IDs.WORKSPACE_PRIMARY,
        workspace_service=ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def workspace_ops(single_workspace):
    client = Client(url=single_workspace.url, context=single_workspace.context)
    return client.get_workspace(IDs.WORKSPACE_PRIMARY)


@pytest.fixture
def custom_function():
    custom_function_service = MagicMock()
    custom_function_service.custom_function_get.return_value = {
        'name': 'dynamic',
        'parameters': _custom_function_parameter_list(),
    }
    custom_function_service.custom_function_options_get.return_value = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {"cs_solver": 0},
        "simulation": {"ncp": 500},
        "solver": {'atol': 1e-7, 'rtol': 1e-9},
    }
    custom_function_service.custom_function_default_options_get.return_value = {
        "compiler": {"c_compiler": "msvs"},
        "runtime": {"log_level": 2},
        "simulation": {"ncp": 500},
        "solver": {"rtol": 1e-5},
    }
    return create_custom_function_entity(
        IDs.WORKSPACE_PRIMARY,
        'dynamic',
        _custom_function_parameter_list(),
        custom_function_service,
    )


@pytest.fixture
def custom_function_no_param():
    custom_function_service = MagicMock()
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {},
        "simulation": {"ncp": 500},
        "solver": {},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    return create_custom_function_entity(
        IDs.WORKSPACE_PRIMARY, 'dynamic', [], custom_function_service
    )


@pytest.fixture
def model_compiled():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "done"}
    return create_model_entity(
        'Test.PID', IDs.WORKSPACE_PRIMARY, ws_service, model_exe_service
    )


@pytest.fixture
def model_cached():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    model_exe_service.fmu_setup.return_value = (IDs.FMU_PRIMARY, {})
    model_exe_service.compile_status.return_value = {"status": "done"}
    return create_model_entity(
        'Test.PID', IDs.WORKSPACE_PRIMARY, ws_service, model_exe_service
    )


@pytest.fixture
def model_compiling():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "running"}
    return create_model_entity(
        'Test.PID', IDs.WORKSPACE_PRIMARY, ws_service, model_exe_service
    )


@pytest.fixture
def model_compile_cancelled():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return create_model_entity(
        'Test.PID', IDs.WORKSPACE_PRIMARY, ws_service, model_exe_service
    )


@pytest.fixture
def compiler_options():
    custom_function_service = MagicMock()
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {"log_level": 3},
        "simulation": {"ncp": 2000},
        "solver": {"rtol": 0.0001},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    return CompilerOptions(opts["compiler"], "dynamic")


@pytest.fixture
def runtime_options():
    custom_function_service = MagicMock()
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {"log_level": 3},
        "simulation": {"ncp": 2000},
        "solver": {"rtol": 0.0001},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    return RuntimeOptions(opts["runtime"], "dynamic")


@pytest.fixture
def simulation_options():
    custom_function_service = MagicMock()
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {"log_level": 3},
        "simulation": {"ncp": 2000},
        "solver": {"rtol": 0.0001},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    return SimulationOptions(opts["simulation"], "dynamic")


@pytest.fixture
def solver_options():
    custom_function_service = MagicMock()
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {"log_level": 3},
        "simulation": {"ncp": 2000},
        "solver": {"rtol": 0.0001},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    return SolverOptions(opts["solver"], "dynamic")


@pytest.fixture
def fmu():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    ws_service.fmu_get.return_value = {
        'id': IDs.FMU_PRIMARY,
        'input': {
            'class_name': 'Workspace.PID_Controller',
            'compiler_options': {'c_compiler': 'gcc'},
            'runtime_options': {},
            'compiler_log_level': 'w',
            'fmi_target': 'me',
            'fmi_version': '2.0',
            'platform': 'auto',
            'model_snapshot': '1610523986117',
            'toolchain_version': '0.0.1',
            'compiled_on_sys': 'win32',
        },
        'run_info': {
            'status': 'successful',
            'datetime_started': 1610523986193,
            'errors': [],
            'datetime_finished': 1610523990763,
        },
        'meta': {
            'created_epoch': 1610523986,
            'input_hash': 'f47e0d051a804eee3cde3e3d98da5f39',
            'fmu_file': 'model.fmu',
        },
    }
    ws_service.fmu_download.return_value = b'\x00\x00\x00\x00'
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.settable_parameters_get.return_value = ['h0', 'v']
    model_exe_service.compile_log.return_value = "Successful Log"
    model_exe_service.fmu_setup.return_value = (IDs.FMU_PRIMARY, {})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return create_model_exe_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.FMU_PRIMARY,
        ws_service,
        model_exe_service=model_exe_service,
    )


@pytest.fixture
def fmu_with_modifiers():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    ws_service.fmu_get.return_value = {
        'id': IDs.FMU_PRIMARY,
        'input': {
            'class_name': 'Workspace.PID_Controller',
            'compiler_options': {'c_compiler': 'gcc'},
            'runtime_options': {},
            'compiler_log_level': 'w',
            'fmi_target': 'me',
            'fmi_version': '2.0',
            'platform': 'auto',
            'model_snapshot': '1610523986117',
            'toolchain_version': '0.0.1',
            'compiled_on_sys': 'win32',
        },
        'run_info': {
            'status': 'successful',
            'datetime_started': 1610523986193,
            'errors': [],
            'datetime_finished': 1610523990763,
        },
        'meta': {
            'created_epoch': 1610523986,
            'input_hash': 'f47e0d051a804eee3cde3e3d98da5f39',
            'fmu_file': 'model.fmu',
        },
    }
    ws_service.fmu_download.return_value = b'\x00\x00\x00\x00'
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.settable_parameters_get.return_value = ['h0', 'v']
    model_exe_service.compile_log.return_value = "Successful Log"
    model_exe_service.fmu_setup.return_value = (IDs.FMU_PRIMARY, {'PI.K': 20})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return create_model_exe_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.FMU_PRIMARY,
        workspace_service=ws_service,
        model_exe_service=model_exe_service,
        modifiers={'PI.K': 20},
    )


@pytest.fixture
def model():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    return create_model_entity(
        'Test.PID', IDs.WORKSPACE_PRIMARY, ws_service, model_exe_service
    )


@pytest.fixture
def fmu_compile_running():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "not_started"}}
    model_exe_service.compile_status.return_value = {"status": "running"}
    return create_model_exe_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.FMU_PRIMARY,
        ws_service,
        model_exe_service=model_exe_service,
    )


@pytest.fixture
def fmu_compile_failed():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "failed"}}
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.compile_log.return_value = "Failed Log"
    return create_model_exe_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.FMU_PRIMARY,
        ws_service,
        model_exe_service=model_exe_service,
    )


@pytest.fixture
def fmu_compile_cancelled():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "cancelled"}}
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return create_model_exe_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.FMU_PRIMARY,
        ws_service,
        model_exe_service=model_exe_service,
    )


@pytest.fixture
def experiment():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 0, "successful": 1, "cancelled": 0}
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.cases_get.return_value = {"data": {"items": [{"id": "case_1"}]}}
    case_get_data = {
        "id": "case_1",
        "run_info": {"status": "successful", "consistent": True},
        "input": {
            "fmu_id": IDs.FMU_PRIMARY,
            "analysis": {
                "analysis_function": "dynamic",
                "parameters": {"start_time": 0, "final_time": 1},
                "simulation_options": {},
                "solver_options": {},
                "simulation_log_level": "NOTHING",
            },
            "parametrization": {},
            "structural_parametrization": {},
            "fmu_base_parametrization": {},
            "initialize_from_case": None,
            "initialize_from_external_result": None,
        },
        "meta": {"label": "Cruise operating point"},
    }
    case_put_return = copy.deepcopy(case_get_data)
    case_put_return['run_info']['consistent'] = False

    exp_service.case_get.return_value = case_get_data
    exp_service.case_put.return_value = case_put_return
    exp_service.case_get_log.return_value = "Successful Log"
    exp_service.case_result_get.return_value = (bytes(4), 'result.mat')
    exp_service.case_artifact_get.return_value = (bytes(4), 'result.mat')
    exp_service.trajectories_get.return_value = [[[1, 2, 3, 4]], [[5, 2, 9, 4]]]
    exp_service.case_trajectories_get.return_value = [[1, 2, 3, 4], [5, 2, 9, 4]]
    return ExperimentMock(
        create_experiment_entity(
            IDs.WORKSPACE_PRIMARY,
            IDs.EXPERIMENT_PRIMARY,
            ws_service,
            model_exe_service,
            exp_service,
        ),
        exp_service,
    )


@pytest.fixture
def experiment_running():
    ws_service = MagicMock()
    exp_service = MagicMock()
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.case_get.return_value = {"id": "case_1"}
    exp_service.execute_status.return_value = {"status": "running"}
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        workspace_service=ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def experiment_cancelled():
    ws_service = MagicMock()
    exp_service = MagicMock()
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.case_get.return_value = {"id": "case_1"}
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        workspace_service=ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def batch_experiment_with_case_filter():
    ws_service = MagicMock()
    model_exe_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {
            "status": "done",
            "failed": 0,
            "successful": 1,
            "cancelled": 0,
            "not_started": 3,
        }
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.cases_get.return_value = {
        "data": {
            "items": [
                {"id": "case_1", "meta": {"label": None}},
                {"id": "case_2", "meta": {"label": "Cruise operating point"}},
                {"id": "case_3", "meta": {"label": None}},
                {"id": "case_4", "meta": {"label": "Cruise operating point"}},
            ]
        }
    }
    exp_service.case_get.return_value = {
        "id": "case_3",
        "run_info": {"status": "successful", "consistent": True},
        "input": {"fmu_id": IDs.FMU_PRIMARY},
    }
    return ExperimentMock(
        create_experiment_entity(
            IDs.WORKSPACE_PRIMARY,
            IDs.EXPERIMENT_PRIMARY,
            ws_service,
            model_exe_service,
            exp_service,
        ),
        exp_service,
    )


@pytest.fixture
def batch_experiment():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 0, "successful": 2, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.cases_get.return_value = {
        "data": {"items": [{"id": "case_1"}, {"id": "case_2"}]}
    }
    exp_service.case_get.return_value = {
        "id": "case_2",
        "run_info": {"status": "successful", "consistent": True},
    }
    exp_service.case_get_log.return_value = "Successful Log"
    exp_service.case_result_get.return_value = (bytes(4), 'result.mat')
    exp_service.case_artifact_get.return_value = (bytes(4), 'result.mat')
    exp_service.trajectories_get.return_value = [
        [[1, 2, 3, 4], [14, 4, 4, 74]],
        [[5, 2, 9, 4], [11, 22, 32, 44]],
    ]
    exp_service.case_trajectories_get.return_value = [[14, 4, 4, 74], [11, 22, 32, 44]]
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def batch_experiment_some_successful():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {
            "status": "done",
            "failed": 1,
            "successful": 2,
            "cancelled": 0,
            "not_started": 1,
        }
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.cases_get.return_value = {
        "data": {
            "items": [
                {"id": "case_1"},
                {"id": "case_2"},
                {"id": "case_3"},
                {"id": "case_4"},
            ]
        }
    }
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        workspace_service=ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def running_experiment():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {"run_info": {"status": "not_started"}}
    exp_service.execute_status.return_value = {"status": "running"}
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        workspace_service=ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def experiment_with_failed_case():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 1, "successful": 0, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.cases_get.return_value = {"data": {"items": [{"id": "case_1"}]}}
    exp_service.case_get.return_value = {
        "id": "case_1",
        "run_info": {"status": "failed", "consistent": True},
    }
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.trajectories_get.return_value = [[[1, 2, 3, 4]], [[5, 2, 9, 4]]]
    exp_service.case_trajectories_get.return_value = [[1, 2, 3, 4], [5, 2, 9, 4]]
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        workspace_service=ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def failed_experiment():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {
            "status": "failed",
            "failed": 0,
            "successful": 0,
            "cancelled": 0,
            'errors': ['out of licenses', 'too large experiment'],
        }
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.cases_get.return_value = {"data": {"items": []}}
    exp_service.case_get.return_value = {}
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def cancelled_experiment():
    ws_service = MagicMock()
    exp_service = MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {
            "status": "cancelled",
            "failed": 0,
            "successful": 0,
            "cancelled": 1,
        }
    }
    exp_service.cases_get.return_value = {"data": {"items": [{"id": "case_1"}]}}
    exp_service.case_get.return_value = {"id": "case_1"}
    exp_service.execute_status.return_value = {
        "status": "cancelled",
        "consistent": True,
    }
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY,
        IDs.EXPERIMENT_PRIMARY,
        ws_service,
        experiment_service=exp_service,
    )


@pytest.fixture
def single_project(user_with_license):
    json = {
        "id": IDs.PROJECT_PRIMARY,
        "definition": {
            "name": "NewProject",
            "format": "1.0",
            "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
            "content": [
                {
                    "id": IDs.PROJECT_CONTENT_PRIMARY,
                    "relpath": "MyPackage",
                    "contentType": "MODELICA",
                    "name": "MyPackage",
                    "defaultDisabled": False,
                }
            ],
            "executionOptions": [],
        },
        "projectType": "LOCAL",
    }
    return with_json_route(
        user_with_license, 'GET', f'api/projects/{IDs.PROJECT_PRIMARY}', json
    )


@pytest.fixture
def multiple_projects(user_with_license):
    json = {
        "data": {
            "items": [
                {
                    "id": IDs.PROJECT_PRIMARY,
                    "definition": {
                        "name": "NewProject",
                        "format": "1.0",
                        "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
                        "content": [
                            {
                                "id": IDs.PROJECT_CONTENT_PRIMARY,
                                "relpath": "MyPackage",
                                "contentType": "MODELICA",
                                "name": "MyPackage",
                                "defaultDisabled": False,
                            }
                        ],
                        "executionOptions": [],
                    },
                    "projectType": "LOCAL",
                }
            ]
        }
    }
    return with_json_route(user_with_license, 'GET', 'api/projects', json)


@pytest.fixture
def delete_project(user_with_license):
    return with_json_route_no_resp(
        user_with_license, 'DELETE', f'api/projects/{IDs.PROJECT_PRIMARY}'
    )


@pytest.fixture
def delete_project_content(user_with_license):
    return with_json_route_no_resp(
        user_with_license,
        'DELETE',
        f'api/projects/{IDs.PROJECT_PRIMARY}/content/{IDs.PROJECT_CONTENT_PRIMARY}',
    )


@pytest.fixture
def project():
    project_service = MagicMock()
    project_service.projects_get.return_value = {
        "data": {
            "items": [
                {
                    "id": IDs.PROJECT_PRIMARY,
                    "definition": {
                        "name": "NewProject",
                        "format": "1.0",
                        "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
                        "content": [
                            {
                                "id": IDs.PROJECT_CONTENT_PRIMARY,
                                "relpath": "MyPackage",
                                "contentType": "MODELICA",
                                "name": "MyPackage",
                                "defaultDisabled": False,
                            }
                        ],
                        "executionOptions": [],
                    },
                    "projectType": "LOCAL",
                }
            ]
        }
    }
    project_service.project_get.return_value = {
        "id": IDs.PROJECT_PRIMARY,
        "definition": {
            "name": "NewProject",
            "format": "1.0",
            "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
            "content": [
                {
                    "id": IDs.PROJECT_CONTENT_PRIMARY,
                    "relpath": "MyPackage",
                    "contentType": "MODELICA",
                    "name": "MyPackage",
                    "defaultDisabled": False,
                }
            ],
            "executionOptions": [],
        },
        "projectType": "LOCAL",
    }
    project_service.project_content_upload.return_value = {
        "id": IDs.PROJECT_CONTENT_SECONDARY,
        "relpath": "test.mo",
        "contentType": "MODELICA",
        "name": "test",
        "defaultDisabled": False,
    }
    project_service.fmu_upload.return_value = {
        "fmuClassPath": "Workspace.PID_Controller.Model",
        "importWarnings": [
            "Specified argument for 'top_level_inputs=['a']' does not match any variable"
        ],
        "library": {
            'project_id': IDs.PROJECT_PRIMARY,
            'content_id': IDs.PROJECT_CONTENT_PRIMARY,
        },
    }
    return ProjectMock(
        create_project_entity(IDs.PROJECT_PRIMARY, project_service=project_service),
        service=project_service,
    )


@pytest.fixture
def upload_project_content(sem_ver_check, mock_server_base):
    json = {
        "id": IDs.PROJECT_CONTENT_SECONDARY,
        "relpath": "test.mo",
        "contentType": "MODELICA",
        "name": "test",
        "defaultDisabled": False,
    }

    return with_json_route(
        mock_server_base,
        'POST',
        F'api/projects/{IDs.PROJECT_CONTENT_SECONDARY}/content',
        json,
    )


@pytest.fixture
def shared_definition_get(user_with_license, mock_server_base):
    json = {
        "definition": {
            "name": "test",
            "projects": [
                {
                    "reference": {
                        "id": IDs.VERSIONED_PROJECT_REFERENCE,
                        "vcsUri": "git+https://github.com/project/test.git@main:da6abb188a089527df1b54b27ace84274b819e4a",
                    },
                    "disabled": True,
                    "disabledContent": [],
                }
            ],
            "dependencies": [],
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/sharing-definition?strict=true',
        json,
    )


@pytest.fixture
def get_workspace_upload_status(user_with_license, mock_server_base):
    json = {
        "data": {
            'id': 'efa5cc60e3d04049ad0566bc53b431f8',
            'status': 'ready',
            'data': {'resourceUri': 'api/workspaces/test', 'workspaceId': 'test'},
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspace-imports/05c7c0c45a084f079682eaf443287901',
        json,
    )


@pytest.fixture
def get_successful_workspace_upload_status(user_with_license, mock_server_base):
    json = {
        "data": {
            "id": "05c7c0c45a084f079682eaf443287901",
            "status": "ready",
            "data": {
                'resourceUri': 'api/workspaces/123456780',
                'workspaceId': "123456780",
            },
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspace-imports/05c7c0c45a084f079682eaf443287901',
        json,
    )


@pytest.fixture
def get_failed_workspace_upload_status(user_with_license, mock_server_base):
    json = {
        "data": {
            "id": "05c7c0c45a084f079682eaf443287901",
            "status": "error",
            "error": {
                "message": "Could not import workspace 'test'. Multiple existing projects matches the URI git+https://github.com/project/test.git@main:da6abb188a089527df1b54b27ace84274b819e4a and no selected matching was given",
                "code": 12102,
            },
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        'api/workspace-imports/05c7c0c45a084f079682eaf443287901',
        json,
    )


@pytest.fixture
def import_from_shared_definition(user_with_license, mock_server_base):
    json = {
        "data": {"location": "api/workspace-imports/05c7c0c45a084f079682eaf443287901"}
    }

    return with_json_route(mock_server_base, 'POST', 'api/workspace-imports', json)


@pytest.fixture
def get_project_matchings(user_with_license, mock_server_base):
    json = {
        "data": {
            "vcs": [
                {
                    "entryId": IDs.VERSIONED_PROJECT_REFERENCE,
                    "uri": {
                        "serviceKind": "git",
                        "serviceUrl": "https://github.com",
                        "repoUrl": {
                            "url": "github.com/project/test.git",
                            "refname": "main",
                            "sha1": "da6abb188a089527df1b54b27ace84274b819e4a",
                        },
                        "protocol": "https",
                        "subdir": ".",
                    },
                    "projects": [VERSIONED_PROJECT_TRUNK, VERSIONED_PROJECT_BRANCH],
                },
            ]
        }
    }

    return with_json_route(
        mock_server_base, 'POST', 'api/workspace-imports-matchings', json
    )


@pytest.fixture
def get_versioned_projects(user_with_license, mock_server_base):
    json = {"data": {"items": [VERSIONED_PROJECT_TRUNK, VERSIONED_PROJECT_BRANCH]}}

    return with_json_route(mock_server_base, 'GET', 'api/projects?vcsInfo=true', json)


@pytest.fixture
def get_versioned_new_project_trunk(user_with_license, mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        f'api/projects/{IDs.VERSIONED_PROJECT_PRIMARY}?vcsInfo=true',
        VERSIONED_PROJECT_TRUNK,
    )


@pytest.fixture
def get_versioned_new_project_branch(user_with_license, mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        f'api/projects/{IDs.VERSIONED_PROJECT_SECONDARY}?vcsInfo=true',
        VERSIONED_PROJECT_BRANCH,
    )
