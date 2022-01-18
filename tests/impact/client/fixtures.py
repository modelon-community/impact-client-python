import collections
import copy
import unittest.mock
import pytest
import requests
import requests_mock
import modelon.impact.client
from modelon.impact.client.entities import (
    CustomFunction,
    Workspace,
    Model,
    Experiment,
    ModelExecutable,
)

MockedServer = collections.namedtuple('MockedServer', ['url', 'context', 'adapter'])
ExperimentMock = collections.namedtuple('ExperimentMock', ['entity', 'service'])
WorkspaceMock = collections.namedtuple('WorkspaceMock', ['entity', 'service'])


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
    json = {'id': 'newWorkspace'}

    return with_json_route(user_with_license, 'POST', 'api/workspaces', json)


@pytest.fixture
def create_workspace_fail_auth_once(sem_ver_check, mock_server_base):
    json_error = {'error': {'code': 123456, 'message': 'JWT expired'}}
    json_ok = {'id': 'newWorkspace'}
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
        user_with_license, 'DELETE', 'api/workspaces/AwesomeWorkspace'
    )


@pytest.fixture
def single_workspace(user_with_license):
    json = {'id': 'AwesomeWorkspace'}

    return with_json_route(
        user_with_license, 'GET', 'api/workspaces/AwesomeWorkspace', json
    )


@pytest.fixture
def multiple_workspace(user_with_license):
    json = {'data': {'items': [{'id': 'AwesomeWorkspace'}, {'id': 'BoringWorkspace'}]}}

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
        sem_ver_check, 'POST', 'api/workspaces/AwesomeWorkspace/libraries', json
    )


@pytest.fixture
def import_fmu(sem_ver_check):
    json = {
        "fmuClassPath": "Workspace.PID_Controller.Model",
        "importWarnings": [
            "Specified argument for 'top_level_inputs=['a']' does not match any variable"
        ],
        "library": {"id": "Workspace", "uses": {}, "name": "Workspace"},
    }

    return with_json_route(
        sem_ver_check,
        'POST',
        'api/workspaces/AwesomeWorkspace/libraries/Workspace/models',
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
            "workspaceId": "workspace",
        }
    }


@pytest.fixture
def workspace_sal_upload_base():
    workspace_service = unittest.mock.MagicMock()
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
def download_fmu(sem_ver_check, mock_server_base):
    content = bytes(4)

    return with_zip_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/model-executables/pid_20090615_134/binary',
        content,
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
def no_cached_fmu_id(mock_server_base):
    json = {
        "id": None,
        "parameters": {},
    }

    return with_json_route(
        mock_server_base,
        'POST',
        'api/workspaces/WS/model-executables?getCached=true',
        json,
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
def model_compile(get_fmu_id, no_cached_fmu_id, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base,
        'POST',
        'api/workspaces/WS/model-executables/'
        'workspace_pid_controller_20090615_134530_as86g32/compilation',
    )


@pytest.fixture
def get_cached_fmu_id(mock_server_base):
    json = {
        "id": "workspace_pid_controller_20090615_134530_as86g32",
        "parameters": {},
    }

    return with_json_route(
        mock_server_base,
        'POST',
        'api/workspaces/WS/model-executables?getCached=true',
        json,
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
        'POST',
        'api/workspaces/WS/model-executables/fmu_id/steady-state-metadata',
        json,
    )


@pytest.fixture
def delete_fmu(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'DELETE', 'api/workspaces/WS/model-executables/fmu_id'
    )


@pytest.fixture
def experiment_execute(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'POST', 'api/workspaces/WS/experiments/pid_2009/execution'
    )


@pytest.fixture
def set_experiment_label(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'PUT', 'api/workspaces/WS/experiments/pid_2009'
    )


@pytest.fixture
def delete_experiment(sem_ver_check, mock_server_base):

    return with_json_route_no_resp(
        mock_server_base, 'DELETE', 'api/workspaces/WS/experiments/pid_2009'
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
    json = [[[1.0, 1.0], [3.0, 3.0], [5.0, 5.0]]]

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
def put_case(sem_ver_check, mock_server_base):
    json = {"id": "case_1"}

    return with_json_route(
        mock_server_base,
        'PUT',
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
def get_mat_case_results(sem_ver_check, mock_server_base):
    binary = bytes(4)

    return with_octet_stream_route(
        mock_server_base,
        'GET',
        'api/workspaces/WS/experiments/pid_2009/cases/case_1/result',
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
        'api/workspaces/WS/experiments/pid_2009/cases/case_1/result',
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
        'api/workspaces/WS/experiments/pid_2009/cases/case_1/custom-artifacts/ABCD',
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
        'api/workspaces/WS/experiments/pid_2009/cases/case_1/trajectories',
        json,
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
    ws_service = unittest.mock.MagicMock()
    custom_function_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_create.return_value = {"experiment_id": "pid_2009"}
    ws_service.library_import.return_value = {
        "name": "Single",
        "uses": {"Modelica": {"version": "3.2.2"}},
    }
    ws_service.workspace_clone.return_value = {"workspace_id": "MyClonedWorkspace"}
    ws_service.fmus_get.return_value = {
        'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9D-4df5'}]}
    }
    ws_service.fmu_get.return_value = {'id': 'pid_20090615_134'}
    ws_service.experiment_get.return_value = {'id': 'pid_20090615_134'}
    exp_service.execute_status.return_value = {"status": "done"}
    ws_service.experiments_get.return_value = {
        'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'dd9f-3df5'}]}
    }
    ws_service.workspace_download.return_value = b'\x00\x00\x00\x00'
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
    exp_service.experiment_execute.return_value = "pid_2009"
    return WorkspaceMock(
        Workspace(
            'AwesomeWorkspace',
            ws_service,
            experiment_service=exp_service,
            custom_function_service=custom_function_service,
        ),
        ws_service,
    )


@pytest.fixture
def workspace_execute_running():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_create.return_value = {"experiment_id": "pid_2009"}
    exp_service.experiment_execute.return_value = "pid_2009"
    exp_service.execute_status.return_value = {"status": "running"}
    return Workspace('AwesomeWorkspace', ws_service, experiment_service=exp_service)


@pytest.fixture
def workspace_execute_cancelled():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_create.return_value = {"experiment_id": "pid_2009"}
    exp_service.experiment_execute.return_value = "pid_2009"
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return Workspace('AwesomeWorkspace', ws_service, experiment_service=exp_service)


@pytest.fixture
def workspace_ops(single_workspace):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    return client.get_workspace('AwesomeWorkspace')


@pytest.fixture
def custom_function():
    custom_function_service = unittest.mock.MagicMock()
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
    return CustomFunction(
        'test_ws', 'dynamic', _custom_function_parameter_list(), custom_function_service
    )


@pytest.fixture
def custom_function_no_param():
    custom_function_service = unittest.mock.MagicMock()
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {},
        "simulation": {"ncp": 500},
        "solver": {},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    return CustomFunction("test_ws", 'dynamic', [], custom_function_service)


@pytest.fixture
def model_compiled():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = 'test_pid_fmu_id'
    model_exe_service.compile_status.return_value = {"status": "done"}
    return Model('Test.PID', "test_ws", ws_service, model_exe_service)


@pytest.fixture
def model_cached():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    model_exe_service.fmu_setup.return_value = ('test_pid_fmu_id', {})
    model_exe_service.compile_status.return_value = {"status": "done"}
    return Model('Test.PID', "test_ws", ws_service, model_exe_service)


@pytest.fixture
def model_compiling():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = 'test_pid_fmu_id'
    model_exe_service.compile_status.return_value = {"status": "running"}
    return Model('Test.PID', "test_ws", ws_service, model_exe_service)


@pytest.fixture
def model_compile_cancelled():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = 'test_pid_fmu_id'
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return Model('Test.PID', "test_ws", ws_service, model_exe_service)


@pytest.fixture
def compiler_options():
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
    return modelon.impact.client.options.ExecutionOptions(
        opts["compiler"], "dynamic", custom_function_service
    )


@pytest.fixture
def runtime_options():
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
    return modelon.impact.client.options.ExecutionOptions(
        opts["runtime"], "dynamic", custom_function_service
    )


@pytest.fixture
def simulation_options():
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
    return modelon.impact.client.options.ExecutionOptions(
        opts["simulation"], "dynamic", custom_function_service
    )


@pytest.fixture
def solver_options():
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
    return modelon.impact.client.options.ExecutionOptions(
        opts["solver"], "dynamic", custom_function_service
    )


@pytest.fixture
def fmu():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {
        'id': 'workspace_pid_controller_20210113_131626_77c5174',
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
    model_exe_service.fmu_setup.return_value = ('test_pid_fmu_id', {})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return ModelExecutable("Workspace", "Test", ws_service, model_exe_service)


@pytest.fixture
def fmu_with_modifiers():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {
        'id': 'workspace_pid_controller_20210113_131626_77c5174',
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
    model_exe_service.fmu_setup.return_value = ('test_pid_fmu_id', {'PI.K': 20})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return ModelExecutable(
        "Workspace", "Test", ws_service, model_exe_service, modifiers={'PI.K': 20}
    )


@pytest.fixture
def model():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    return Model('Test.PID', "test_ws", ws_service, model_exe_service)


@pytest.fixture
def fmu_compile_running():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "not_started"}}
    model_exe_service.compile_status.return_value = {"status": "running"}
    return ModelExecutable("Workspace", "Test", ws_service, model_exe_service)


@pytest.fixture
def fmu_compile_failed():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "failed"}}
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.compile_log.return_value = "Failed Log"
    return ModelExecutable("Workspace", "Test", ws_service, model_exe_service)


@pytest.fixture
def fmu_compile_cancelled():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    ws_service.fmu_get.return_value = {"run_info": {"status": "cancelled"}}
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return ModelExecutable("Workspace", "Test", ws_service, model_exe_service)


@pytest.fixture
def experiment():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 0, "successful": 1, "cancelled": 0}
    }
    exp_service.experiment_execute.return_value = "pid_2009"
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.cases_get.return_value = {"data": {"items": [{"id": "case_1"}]}}
    case_get_data = {
        "id": "case_1",
        "run_info": {"status": "successful", "consistent": True},
        "input": {
            "fmu_id": "modelica_fluid_examples_heatingsystem_20210130_114628_bbd91f1",
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
        Experiment("Workspace", "Test", ws_service, model_exe_service, exp_service),
        exp_service,
    )


@pytest.fixture
def experiment_running():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    exp_service.experiment_execute.return_value = "pid_2009"
    exp_service.case_get.return_value = {"id": "case_1"}
    exp_service.execute_status.return_value = {"status": "running"}
    return Experiment("Workspace", "Test", ws_service, exp_service=exp_service)


@pytest.fixture
def experiment_cancelled():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    exp_service.experiment_execute.return_value = "pid_2009"
    exp_service.case_get.return_value = {"id": "case_1"}
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return Experiment("Workspace", "Test", ws_service, exp_service=exp_service)


@pytest.fixture
def batch_experiment_with_case_filter():
    ws_service = unittest.mock.MagicMock()
    model_exe_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {
        "run_info": {
            "status": "done",
            "failed": 0,
            "successful": 1,
            "cancelled": 0,
            "not_started": 3,
        }
    }
    exp_service.experiment_execute.return_value = "Experiment"
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
        "input": {
            "fmu_id": "modelica_fluid_examples_heatingsystem_20210130_114628_bbd91f1"
        },
    }
    return ExperimentMock(
        Experiment(
            "Workspace", "Experiment", ws_service, model_exe_service, exp_service
        ),
        exp_service,
    )


@pytest.fixture
def batch_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
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
    return Experiment("Workspace", "Test", ws_service, exp_service=exp_service)


@pytest.fixture
def batch_experiment_some_successful():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
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
    return Experiment("Workspace", "Test", ws_service, exp_service=exp_service)


@pytest.fixture
def running_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
    ws_service.experiment_get.return_value = {"run_info": {"status": "not_started"}}
    exp_service.execute_status.return_value = {"status": "running"}
    return Experiment("Workspace", "Test", ws_service, exp_service=exp_service)


@pytest.fixture
def experiment_with_failed_case():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
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
    return Experiment("Workspace", "Test", ws_service, exp_service=exp_service)


@pytest.fixture
def failed_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
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
    return Experiment("Workspace", "Test", ws_service, exp_service)


@pytest.fixture
def cancelled_experiment():
    ws_service = unittest.mock.MagicMock()
    exp_service = unittest.mock.MagicMock()
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
    return Experiment("Workspace", "Test", ws_service, exp_service=exp_service)
