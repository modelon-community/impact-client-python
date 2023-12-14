import collections
import copy
from unittest.mock import MagicMock

import pytest
import requests

from modelon.impact.client import Client
from modelon.impact.client.options import (
    CompilerOptions,
    RuntimeOptions,
    SimulationOptions,
    SolverOptions,
)
from modelon.impact.client.sal import exceptions
from tests.impact.client.helpers import (
    LAST_POINT_TRAJECTORY,
    MODEL_DESCRIPTION_XML,
    UNVERSIONED_PROJECT,
    VERSIONED_PROJECT_BRANCH,
    VERSIONED_PROJECT_TRUNK,
    IDs,
    create_custom_function_entity,
    create_experiment_entity,
    create_model_entity,
    create_model_exe_entity,
    create_project_entity,
    create_published_workspace_entity,
    create_workspace_entity,
    get_test_fmu_experiment_definition,
    get_test_get_fmu,
    get_test_modelica_experiment_definition,
    get_test_published_workspace_definition,
    get_test_workspace_definition,
    json_request_list_item,
    with_csv_route,
    with_exception,
    with_json_request_list_route,
    with_json_route,
    with_json_route_no_resp,
    with_octet_stream_route,
    with_text_route,
    with_xml_route,
    with_zip_route,
)

ExperimentMock = collections.namedtuple('ExperimentMock', ['entity', 'service'])
WorkspaceMock = collections.namedtuple('WorkspaceMock', ['entity', 'service'])
PublishedWorkspaceMock = collections.namedtuple(
    'PublishedWorkspaceMock', ['entity', 'service']
)
ProjectMock = collections.namedtuple('ProjectMock', ['entity', 'service'])
ModelMock = collections.namedtuple('ModelMock', ['entity', 'service'])


def get_model_exes_url(workspace_id):
    return f'api/workspaces/{workspace_id}/model-executables'


def get_model_exe_url(workspace_id, fmu_id):
    return f'{get_model_exes_url(workspace_id)}/{fmu_id}'


def get_experiment_url(workspace_id, experiment_id):
    return f'api/workspaces/{workspace_id}/experiments/{experiment_id}'


def get_case_url(workspace_id, experiment_id, case_id):
    return f'{get_experiment_url(workspace_id, experiment_id)}/cases/{case_id}'


def get_content_header(content_type, filename):
    return {
        'X-Powered-By': 'Express',
        'content-type': content_type,
        'content-disposition': f'attachment; filename="{filename}"',
        'connection': 'close',
        'date': 'Thu, 22 Oct 2020 06:03:46 GMT',
        'server': '127.0.0.1',
        'Content-Length': '540',
        'ETag': 'W/"21c-YYNaLhSng67+inxuWx+DHndUdno"',
        'Vary': 'Accept-Encoding',
    }


@pytest.fixture
def sem_ver_check(mock_server_base):
    json = {"version": "4.0.0"}
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
    impact_api_json = {"version": "4.0.0"}

    mock_server = with_json_route(
        mock_server_base,
        'GET',
        'hub/api/',
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
def is_jh_url_uncaught_exception(mock_server_base):
    mock_server = with_exception(
        mock_server_base,
        'GET',
        'hub/api/',
        Exception,
    )
    return mock_server


@pytest.fixture
def is_jh_url_communication_error(mock_server_base):
    mock_server = with_exception(
        mock_server_base,
        'GET',
        'hub/api/',
        exceptions.CommunicationError,
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
def single_workspace_with_size(user_with_license):
    json = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_PRIMARY,
        "sizeInfo": {"total": 7014},
    }
    return with_json_route(
        user_with_license,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}?sizeInfo=True',
        json,
    )


@pytest.fixture
def multiple_published_workspaces(user_with_license):
    definition = get_test_published_workspace_definition()
    json = {'data': {'items': [{"id": IDs.PUBLISHED_WORKSPACE_ID, **definition}]}}

    return with_json_route(user_with_license, 'GET', 'api/published-workspaces', json)


@pytest.fixture
def published_workspace(user_with_license):
    definition = get_test_published_workspace_definition()
    json = {"id": IDs.PUBLISHED_WORKSPACE_ID, **definition}

    return with_json_route(
        user_with_license,
        'GET',
        f'api/published-workspaces/{IDs.PUBLISHED_WORKSPACE_ID}',
        json,
    )


@pytest.fixture
def delete_published_workspace(user_with_license):
    return with_json_route_no_resp(
        user_with_license,
        'DELETE',
        f'api/published-workspaces/{IDs.PUBLISHED_WORKSPACE_ID}',
    )


@pytest.fixture
def rename_published_workspace(user_with_license):
    return with_json_route_no_resp(
        user_with_license,
        'PATCH',
        f'api/published-workspaces/{IDs.PUBLISHED_WORKSPACE_ID}',
    )


@pytest.fixture
def request_published_workspace_access(user_with_license):
    return with_json_route_no_resp(
        user_with_license,
        'PATCH',
        f'api/published-workspaces/{IDs.PUBLISHED_WORKSPACE_ID}/access/users',
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
    json = {"version": "1.0.0"}

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
            "Specified argument for 'top_level_inputs=['a']' "
            "does not match any variable"
        ],
        "library": {
            'project_id': IDs.PROJECT_PRIMARY,
            'content_id': IDs.PROJECT_CONTENT_PRIMARY,
        },
    }

    project_url = f'api/projects/{IDs.PROJECT_PRIMARY}'
    return with_json_route(
        sem_ver_check,
        'POST',
        f'{project_url}/content/{IDs.PROJECT_CONTENT_PRIMARY}/fmu-imports',
        json,
    )


def get_upload_status_data(status):
    resource_uri = f"api/external-result/{IDs.EXTERNAL_RESULT}"
    status_data = {
        "data": {
            "id": IDs.IMPORT,
            "status": status,
        }
    }
    if status == "ready":
        status_data["data"]["data"] = {"resourceUri": resource_uri}
    if status == "error":
        status_data["data"]["error"] = {"message": "Upload failed"}

    return status_data


def get_upload_result_ready_data():
    return get_upload_status_data("ready")


def get_upload_result_running_data():
    return get_upload_status_data("running")


def get_upload_result_error_data():
    return get_upload_status_data("error")


def get_result_upload_post_data():
    return {"data": {"location": f"api/uploads/results/{IDs.IMPORT}"}}


def get_external_result_data():
    return {
        "data": {
            "id": IDs.EXTERNAL_RESULT,
            "createdAt": "2021-09-02T08:26:49.612000",
            "name": "result_for_PID",
            "description": "This is a result file for PID controller",
            "workspaceId": IDs.WORKSPACE_PRIMARY,
        }
    }


@pytest.fixture
def update_workspace(user_with_license):
    json = {
        "definition": get_test_workspace_definition(IDs.WORKSPACE_SECONDARY),
        "id": IDs.WORKSPACE_PRIMARY,
    }
    return with_json_route(
        user_with_license,
        'PUT',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}',
        json,
    )


@pytest.fixture
def external_result_sal_upload():
    service = MagicMock()
    external_result_service = service.external_result
    external_result_service.result_upload.return_value = get_result_upload_post_data()
    external_result_service.get_uploaded_result.return_value = (
        get_external_result_data()
    )

    return service


@pytest.fixture
def external_result_sal_upload_ready(external_result_sal_upload):
    imports = external_result_sal_upload.imports
    imports.get_import_status.return_value = get_upload_result_ready_data()
    return external_result_sal_upload


@pytest.fixture
def external_result_sal_upload_running(external_result_sal_upload):
    imports = external_result_sal_upload.imports
    imports.get_import_status.return_value = get_upload_result_running_data()

    return external_result_sal_upload


@pytest.fixture
def external_result_sal_upload_error(external_result_sal_upload):
    imports = external_result_sal_upload.imports
    imports.get_import_status.return_value = get_upload_result_error_data()

    return external_result_sal_upload


@pytest.fixture
def upload_result_status_ready(sem_ver_check, mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        f'api/uploads/results/{IDs.IMPORT}',
        get_upload_result_ready_data(),
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
        f'api/external-result/{IDs.EXTERNAL_RESULT}',
        get_external_result_data(),
    )


@pytest.fixture
def upload_result_delete(sem_ver_check, mock_server_base):
    return with_json_route_no_resp(
        mock_server_base, 'DELETE', f'api/external-result/{IDs.EXTERNAL_RESULT}'
    )


@pytest.fixture
def setup_export_workspace(sem_ver_check, mock_server_base):
    json = {"data": {"location": f"api/workspace-exports/{IDs.EXPORT}"}}
    return with_json_route(mock_server_base, 'POST', 'api/workspace-exports', json)


@pytest.fixture
def setup_workspace_conversion(sem_ver_check, user_with_license, mock_server_base):
    json = {"data": {"location": f"api/workspace-conversions/{IDs.CONVERSION}"}}
    return with_json_route(mock_server_base, 'POST', 'api/workspace-conversions', json)


@pytest.fixture
def get_export_workspace_status(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "id": IDs.EXPORT,
            "status": "ready",
            "data": {"downloadUri": f"api/exports/{IDs.EXPORT}", "size": 10481015},
            "error": {
                "message": "Could not export workspace 'my_workspace'. "
                "Maximum allowed zip file size of 95MB exceeded",
                "code": 12072,
            },
        }
    }
    return with_json_route(
        mock_server_base, 'GET', f'api/workspace-exports/{IDs.EXPORT}', json
    )


@pytest.fixture
def get_workspace_conversion_status(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "id": IDs.CONVERSION,
            "status": "ready",
            "data": {
                "downloadUri": f"api/workspaces/{IDs.WORKSPACE_PRIMARY}",
                "workspaceId": IDs.WORKSPACE_PRIMARY,
            },
            "error": {
                "message": "Could not convert workspace 'my_workspace'.",
                "code": 12101,
            },
        }
    }
    return with_json_route(
        mock_server_base, 'GET', f'api/workspace-conversions/{IDs.CONVERSION}', json
    )


@pytest.fixture
def get_export_archive(sem_ver_check, mock_server_base):
    content = bytes(4)

    return with_zip_route(mock_server_base, 'GET', f'api/exports/{IDs.EXPORT}', content)


@pytest.fixture
def get_fmu(sem_ver_check, mock_server_base):
    json = {"id": IDs.FMU_PRIMARY}

    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_json_route(mock_server_base, 'GET', fmu_url, json)


@pytest.fixture
def get_all_fmu(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": IDs.FMU_PRIMARY}, {"id": IDs.FMU_SECONDARY}]}}

    return with_json_route(
        mock_server_base, 'GET', f'{get_model_exes_url(IDs.WORKSPACE_PRIMARY)}', json
    )


@pytest.fixture
def download_fmu(sem_ver_check, mock_server_base):
    content = bytes(4)
    ws_url = f'api/workspaces/{IDs.WORKSPACE_PRIMARY}'
    url = f'{ws_url}/model-executables/{IDs.FMU_PRIMARY}/binary'
    return with_zip_route(mock_server_base, 'GET', url, content)


@pytest.fixture
def get_projects(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "items": [
                {"id": IDs.PROJECT_PRIMARY, "definition": {}, "projectType": "LOCAL"}
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
def get_all_experiments_for_class(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "items": [{"id": IDs.EXPERIMENT_PRIMARY}, {"id": IDs.EXPERIMENT_SECONDARY}]
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments?classPath={IDs.MODELICA_CLASS_PATH}',
        json,
    )


@pytest.fixture
def get_experiment(sem_ver_check, mock_server_base):
    json = {"id": IDs.EXPERIMENT_PRIMARY}

    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route(mock_server_base, 'GET', experiment_url, json)


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
        f'{get_model_exes_url(IDs.WORKSPACE_PRIMARY)}?getCached=true',
        json,
    )


@pytest.fixture
def get_fmu_id(mock_server_base):
    json = {
        "id": IDs.FMU_PRIMARY,
        "parameters": {"inertia1.J": 2},
    }

    return with_json_route(
        mock_server_base, 'POST', get_model_exes_url(IDs.WORKSPACE_PRIMARY), json
    )


@pytest.fixture
def model_compile(get_fmu_id, no_cached_fmu_id, mock_server_base):
    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_json_route_no_resp(mock_server_base, 'POST', f'{fmu_url}/compilation')


@pytest.fixture
def get_cached_fmu_id(mock_server_base):
    json = {
        "id": IDs.FMU_PRIMARY,
        "parameters": {},
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'{get_model_exes_url(IDs.WORKSPACE_PRIMARY)}?getCached=true',
        json,
    )


@pytest.fixture
def get_compile_log(sem_ver_check, mock_server_base):
    text = "Compiler arguments:..."

    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_text_route(mock_server_base, 'GET', f'{fmu_url}/compilation/log', text)


@pytest.fixture
def get_model_description(sem_ver_check, mock_server_base):
    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_xml_route(
        mock_server_base, 'GET', f'{fmu_url}/model-description', MODEL_DESCRIPTION_XML
    )


@pytest.fixture
def get_compile_status(sem_ver_check, mock_server_base):
    json = {
        "finished_executions": 0,
        "total_executions": 1,
        "status": "running",
        "progress": [{"message": "Compiling", "percentage": 0}],
    }

    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_json_route(mock_server_base, 'GET', f'{fmu_url}/compilation', json)


@pytest.fixture
def cancel_compile(sem_ver_check, mock_server_base):
    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_json_route_no_resp(mock_server_base, 'DELETE', f'{fmu_url}/compilation')


@pytest.fixture
def get_settable_parameters(sem_ver_check, mock_server_base):
    json = ["param1", "param3"]

    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_json_route(
        mock_server_base, 'GET', f'{fmu_url}/settable-parameters', json
    )


@pytest.fixture
def get_ss_fmu_metadata(sem_ver_check, mock_server_base):
    json = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }

    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_json_route(
        mock_server_base, 'POST', f'{fmu_url}/steady-state-metadata', json
    )


@pytest.fixture
def delete_fmu(sem_ver_check, mock_server_base):
    fmu_url = get_model_exe_url(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
    return with_json_route_no_resp(mock_server_base, 'DELETE', fmu_url)


@pytest.fixture
def experiment_execute(sem_ver_check, mock_server_base):
    experiment_url = get_experiment_url(IDs.WORKSPACE_SECONDARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route_no_resp(
        mock_server_base, 'POST', f'{experiment_url}/execution'
    )


@pytest.fixture
def set_experiment_label(sem_ver_check, mock_server_base):
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route_no_resp(mock_server_base, 'PUT', f'{experiment_url}')


@pytest.fixture
def delete_experiment(sem_ver_check, mock_server_base):
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route_no_resp(mock_server_base, 'DELETE', f'{experiment_url}')


@pytest.fixture
def experiment_status(sem_ver_check, mock_server_base):
    json = {
        "finished_executions": 1,
        "total_executions": 2,
        "status": "running",
        "progress": [{"message": "Simulating at 1.0", "percentage": 1}],
    }
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route(mock_server_base, 'GET', f'{experiment_url}/execution', json)


@pytest.fixture
def cancel_execute(sem_ver_check, mock_server_base):
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route_no_resp(
        mock_server_base, 'DELETE', f'{experiment_url}/execution'
    )


@pytest.fixture
def get_result_variables(sem_ver_check, mock_server_base):
    json = ["PI.J", "inertia.I"]
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route(mock_server_base, 'GET', f'{experiment_url}/variables', json)


@pytest.fixture
def get_trajectories(sem_ver_check, mock_server_base):
    json = [[[1.0, 1.0], [3.0, 3.0], [5.0, 5.0]]]
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route(
        mock_server_base, 'POST', f'{experiment_url}/trajectories', json
    )


@pytest.fixture
def get_last_point(sem_ver_check, mock_server_base):
    json = LAST_POINT_TRAJECTORY
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route(
        mock_server_base, 'POST', f'{experiment_url}/trajectories', json
    )


@pytest.fixture
def get_cases(sem_ver_check, mock_server_base):
    json = {"data": {"items": [{"id": IDs.CASE_PRIMARY}]}}
    experiment_url = get_experiment_url(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
    return with_json_route(mock_server_base, 'GET', f'{experiment_url}/cases', json)


@pytest.fixture
def get_case(sem_ver_check, mock_server_base):
    json = {"id": IDs.CASE_PRIMARY}
    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    return with_json_route(mock_server_base, 'GET', case_url, json)


@pytest.fixture
def put_case(sem_ver_check, mock_server_base):
    json = {"id": IDs.CASE_PRIMARY}
    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    return with_json_route(mock_server_base, 'PUT', f'{case_url}', json)


@pytest.fixture
def get_case_log(sem_ver_check, mock_server_base):
    text = "Simulation log.."
    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    return with_text_route(mock_server_base, 'GET', f'{case_url}/log', text)


@pytest.fixture
def get_mat_case_results(sem_ver_check, mock_server_base):
    binary = bytes(4)

    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    return with_octet_stream_route(
        mock_server_base,
        'GET',
        f'{case_url}/result',
        binary,
        content_header=get_content_header(
            'application/vnd.impact.mat.v1+octet-stream',
            "Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.mat",
        ),
    )


@pytest.fixture
def get_csv_case_results(sem_ver_check, mock_server_base):
    text = "1;2;3"

    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    return with_csv_route(
        mock_server_base,
        'GET',
        f'{case_url}/result',
        text,
        content_header=get_content_header(
            'text/csv', "Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.csv"
        ),
    )


@pytest.fixture
def get_case_artifact(sem_ver_check, mock_server_base):
    binary = bytes(4)

    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    return with_octet_stream_route(
        mock_server_base,
        'GET',
        f'{case_url}/custom-artifacts/{IDs.CUSTOM_ARTIFACT_ID}',
        binary,
        content_header=get_content_header(
            'application/octet-stream',
            "Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.mat",
        ),
    )


@pytest.fixture
def get_case_artifact_meta(sem_ver_check, mock_server_base):
    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    json = {
        "data": {
            "items": [{"id": IDs.CUSTOM_ARTIFACT_ID, "downloadAs": IDs.RESULT_MAT}]
        }
    }
    return with_json_route(
        mock_server_base, 'GET', f'{case_url}/custom-artifacts', json
    )


@pytest.fixture
def get_case_trajectories(sem_ver_check, mock_server_base):
    json = [[1.0, 2.0, 7.0], [2.0, 3.0, 5.0]]

    case_url = get_case_url(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, IDs.CASE_PRIMARY
    )
    return with_json_route(mock_server_base, 'POST', f'{case_url}/trajectories', json)


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


def get_custom_function_url(workspace_id, custom_function_name):
    return f'api/workspaces/{workspace_id}/custom-functions/{custom_function_name}'


@pytest.fixture
def get_custom_function_default_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"c_compiler": "gcc"}}

    custom_function_url = get_custom_function_url(IDs.WORKSPACE_PRIMARY, 'cust_func')
    return with_json_route(
        mock_server_base, 'GET', f'{custom_function_url}/default-options', json
    )


@pytest.fixture
def get_custom_function_options(sem_ver_check, mock_server_base):
    json = {"compiler": {"generate_html_diagnostics": True}}

    custom_function_url = get_custom_function_url(IDs.WORKSPACE_PRIMARY, 'cust_func')
    return with_json_route(
        mock_server_base, 'GET', f'{custom_function_url}/options', json
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
def project_options_get(sem_ver_check, mock_server_base):
    json = {
        "compiler": {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        },
        "runtime": {"log_level": 2},
        "simulation": {'dynamic_diagnostics': False, 'ncp': 500},
        "solver": {"rtol": 1e-5},
    }
    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/projects/{IDs.PROJECT_PRIMARY}/custom-functions/{IDs.DYNAMIC_CF}/options',
        json,
    )


@pytest.fixture
def project_default_options_get(sem_ver_check, mock_server_base):
    json = {"compiler": {"c_compiler": "gcc"}}
    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/custom-functions/{IDs.DYNAMIC_CF}/default-options',
        json,
    )


@pytest.fixture
def publish_workspace():
    service = MagicMock()
    ws_service = service.workspace
    import_service = service.imports
    import_service.get_import_status.return_value = {
        "data": {
            'id': IDs.IMPORT,
            'status': 'ready',
            'data': {
                'resourceUri': f'api/workspace-imports/{IDs.IMPORT}',
                'workspaceId': IDs.WORKSPACE_PRIMARY,
            },
        }
    }
    ws_service.workspace_get.return_value = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_PRIMARY,
        "sizeInfo": {"total": 7014},
    }
    ws_service.import_from_cloud.return_value = {
        "data": {"location": f"api/workspace-imports/{IDs.IMPORT}"}
    }
    definition = get_test_published_workspace_definition()
    ws_service.get_published_workspace.return_value = {
        "id": IDs.PUBLISHED_WORKSPACE_ID,
        **definition,
    }
    return PublishedWorkspaceMock(
        create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID,
            IDs.WORKSPACE_PRIMARY,
            definition=definition,
            service=service,
        ),
        service,
    )


@pytest.fixture
def workspace():
    service = MagicMock()
    export_service = service.exports
    ws_service = service.workspace
    custom_function_service = service.custom_function
    exp_service = service.experiment
    project_service = service.project
    import_service = service.imports
    import_service.get_import_status.return_value = {
        "data": {
            'id': IDs.IMPORT,
            'status': 'ready',
            'data': {
                'resourceUri': f'api/projects/{IDs.PROJECT_PRIMARY}',
                'projectId': IDs.PROJECT_PRIMARY,
            },
        }
    }
    export_service.export_download.return_value = b"undjnvsjnvj"
    ws_service.update_workspace.return_value = {
        "definition": get_test_workspace_definition(IDs.WORKSPACE_SECONDARY),
        "id": IDs.WORKSPACE_PRIMARY,
    }
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_PRIMARY
    }
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
    ws_service.workspace_get.return_value = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_PRIMARY,
        "sizeInfo": {"total": 7014},
    }
    ws_service.projects_get.return_value = {"data": {"items": [UNVERSIONED_PROJECT]}}
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
    ws_service.workspace_export_setup.return_value = {
        "data": {"location": f"api/workspace-exports/{IDs.EXPORT}"}
    }
    export_service.get_export_status.return_value = {
        "data": {
            "id": IDs.EXPORT,
            "status": "ready",
            "data": {"downloadUri": f"api/exports/{IDs.EXPORT}", "size": 10481015},
            "error": {},
        }
    }
    custom_function_service.custom_function_get.return_value = {
        'name': IDs.DYNAMIC_CF,
        'parameters': _custom_function_parameter_list(),
    }
    custom_function_service.custom_functions_get.return_value = {
        'data': {
            'items': [
                {
                    'name': IDs.DYNAMIC_CF,
                    'parameters': _custom_function_parameter_list(),
                }
            ]
        }
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    project_service.project_get.return_value = UNVERSIONED_PROJECT
    ws_service.import_project_from_zip.return_value = {
        "data": {
            "location": f"api/workspaces/{IDs.WORKSPACE_PRIMARY}/project-imports/{IDs.IMPORT}"
        }
    }
    ws_service.import_dependency_from_zip.return_value = {
        "data": {
            "location": f"api/workspaces/{IDs.WORKSPACE_PRIMARY}/dependency-imports/{IDs.IMPORT}"
        }
    }
    return WorkspaceMock(
        create_workspace_entity(IDs.WORKSPACE_PRIMARY, service=service), service
    )


@pytest.fixture
def workspace_execute_running():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_PRIMARY
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "running"}
    return create_workspace_entity(IDs.WORKSPACE_PRIMARY, service=service)


@pytest.fixture
def workspace_execute_cancelled():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_PRIMARY
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return create_workspace_entity(IDs.WORKSPACE_PRIMARY, service=service)


@pytest.fixture
def workspace_ops(single_workspace):
    client = Client(url=single_workspace.url, context=single_workspace.context)
    return client.get_workspace(IDs.WORKSPACE_PRIMARY)


@pytest.fixture
def custom_function():
    service = MagicMock()
    custom_function_service = service.custom_function
    custom_function_service.custom_function_get.return_value = {
        'name': IDs.DYNAMIC_CF,
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
        IDs.DYNAMIC_CF,
        _custom_function_parameter_list(),
        service,
    )


@pytest.fixture
def custom_function_no_param():
    service = MagicMock()
    custom_function_service = service.custom_function
    opts = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {},
        "simulation": {"ncp": 500},
        "solver": {},
    }
    custom_function_service.custom_function_options_get.return_value = opts
    return create_custom_function_entity(
        IDs.WORKSPACE_PRIMARY, IDs.DYNAMIC_CF, [], service=service
    )


@pytest.fixture
def model_compiled():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "done"}
    return create_model_entity(
        IDs.LOCAL_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_PRIMARY,
        IDs.PROJECT_PRIMARY,
        service,
    )


@pytest.fixture
def model_cached():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (IDs.FMU_PRIMARY, {})
    model_exe_service.compile_status.return_value = {"status": "done"}
    return create_model_entity(
        IDs.LOCAL_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_PRIMARY,
        IDs.PROJECT_PRIMARY,
        service,
    )


@pytest.fixture
def model_compiling():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "running"}
    return create_model_entity(
        IDs.LOCAL_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_PRIMARY,
        IDs.PROJECT_PRIMARY,
        service,
    )


@pytest.fixture
def model_compile_cancelled():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return create_model_entity(
        IDs.LOCAL_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_PRIMARY,
        IDs.PROJECT_PRIMARY,
        service,
    )


@pytest.fixture
def compiler_options():
    service = MagicMock()
    custom_function_service = service.custom_function
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
    service = MagicMock()
    custom_function_service = service.custom_function
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
    service = MagicMock()
    custom_function_service = service.custom_function
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
    service = MagicMock()
    custom_function_service = service.custom_function
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
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = get_test_get_fmu()
    ws_service.fmu_download.return_value = b'\x00\x00\x00\x00'
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.settable_parameters_get.return_value = ['h0', 'v']
    model_exe_service.compile_log.return_value = "Successful Log"
    model_exe_service.model_description_get.return_value = MODEL_DESCRIPTION_XML
    model_exe_service.fmu_setup.return_value = (IDs.FMU_PRIMARY, {})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return create_model_exe_entity(
        IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY, service=service
    )


@pytest.fixture
def fmu_with_modifiers():
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = get_test_get_fmu()
    ws_service.fmu_download.return_value = b'\x00\x00\x00\x00'
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.settable_parameters_get.return_value = ['h0', 'v']
    model_exe_service.compile_log.return_value = "Successful Log"
    model_exe_service.fmu_setup.return_value = (IDs.FMU_PRIMARY, {'PI.K': 20})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return create_model_exe_entity(
        IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY, service=service, modifiers={'PI.K': 20}
    )


@pytest.fixture
def model():
    service = MagicMock()
    import_service = service.imports
    import_service.get_import_status.return_value = {
        "data": {
            'id': IDs.IMPORT,
            'status': 'ready',
            'data': {
                "resourceUri": f"api/projects/{IDs.PROJECT_PRIMARY}/content/{IDs.PROJECT_CONTENT_PRIMARY}",
                "fmuClassPath": IDs.LOCAL_MODELICA_CLASS_PATH + '.test',
                "importWarnings": [],
            },
        }
    }
    project_service = service.project
    project_service.project_options_get.return_value = {
        "compiler": {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        },
        "runtime": {"log_level": 2},
        "simulation": {'dynamic_diagnostics': False, 'ncp': 500},
        "solver": {"rtol": 1e-5},
    }
    project_service.project_get.return_value = UNVERSIONED_PROJECT
    project_service.fmu_import.return_value = {
        "data": {
            "location": f"api/projects/{IDs.PROJECT_PRIMARY}/content/"
            f"{IDs.PROJECT_CONTENT_PRIMARY}/fmu-imports/{IDs.FMU_IMPORT_PRIMARY}"
        }
    }
    return ModelMock(
        create_model_entity(
            IDs.LOCAL_MODELICA_CLASS_PATH,
            IDs.WORKSPACE_PRIMARY,
            IDs.PROJECT_PRIMARY,
            service,
        ),
        service=service,
    )


@pytest.fixture
def fmu_compile_running():
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = {"run_info": {"status": "not_started"}}
    model_exe_service.compile_status.return_value = {"status": "running"}
    return create_model_exe_entity(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY, service)


@pytest.fixture
def fmu_compile_failed():
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = {"run_info": {"status": "failed"}}
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.compile_log.return_value = "Failed Log"
    return create_model_exe_entity(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY, service)


@pytest.fixture
def fmu_compile_cancelled():
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = {"run_info": {"status": "cancelled"}}
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return create_model_exe_entity(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY, service)


@pytest.fixture
def fmu_based_experiment():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.fmu_get.return_value = get_test_get_fmu()
    ws_service.experiment_get.return_value = get_test_fmu_experiment_definition()
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    return ExperimentMock(
        create_experiment_entity(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
        ),
        service,
    )


@pytest.fixture
def experiment():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_get.return_value = get_test_modelica_experiment_definition()
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.cases_get.return_value = {"data": {"items": [{"id": IDs.CASE_PRIMARY}]}}
    case_get_data = {
        "id": IDs.CASE_PRIMARY,
        "run_info": {
            "status": "successful",
            "consistent": True,
            "datetime_started": 1662964956945,
            "datetime_finished": 1662964957990,
        },
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
    exp_service.case_result_get.return_value = (bytes(4), IDs.RESULT_MAT)
    exp_service.case_artifacts_meta_get.return_value = {
        "data": {
            "items": [{"id": IDs.CUSTOM_ARTIFACT_ID, "downloadAs": IDs.RESULT_MAT}]
        }
    }
    exp_service.case_artifact_get.return_value = (bytes(4), IDs.RESULT_MAT)
    exp_service.trajectories_get.return_value = [[[1, 2, 3, 4]], [[5, 2, 9, 4]]]
    exp_service.case_trajectories_get.return_value = [[1, 2, 3, 4], [5, 2, 9, 4]]
    return ExperimentMock(
        create_experiment_entity(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
        ),
        service,
    )


@pytest.fixture
def experiment_last_time_point():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_get.return_value = get_test_modelica_experiment_definition()
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.trajectories_get.return_value = LAST_POINT_TRAJECTORY
    return ExperimentMock(
        create_experiment_entity(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
        ),
        service,
    )


@pytest.fixture
def experiment_running():
    service = MagicMock()
    exp_service = service.experiment
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.case_get.return_value = {"id": IDs.CASE_PRIMARY}
    exp_service.execute_status.return_value = {"status": "running"}
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service
    )


@pytest.fixture
def experiment_cancelled():
    service = MagicMock()
    exp_service = service.experiment
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_PRIMARY
    exp_service.case_get.return_value = {"id": IDs.CASE_PRIMARY}
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
    )


@pytest.fixture
def batch_experiment_with_case_filter():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
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
                {"id": IDs.CASE_PRIMARY, "meta": {"label": None}},
                {"id": "case_2", "meta": {"label": "Cruise operating point"}},
                {"id": "case_3", "meta": {"label": None}},
                {"id": "case_4", "meta": {"label": "Cruise operating point"}},
            ]
        }
    }
    exp_service.case_get.return_value = {
        "id": "case_3",
        "run_info": {
            "status": "successful",
            "consistent": True,
            "datetime_started": 1662964956945,
            "datetime_finished": 1662964957990,
        },
        "input": {"fmu_id": IDs.FMU_PRIMARY},
    }
    return ExperimentMock(
        create_experiment_entity(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service
        ),
        service,
    )


@pytest.fixture
def batch_experiment():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 0, "successful": 2, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.cases_get.return_value = {
        "data": {"items": [{"id": IDs.CASE_PRIMARY}, {"id": "case_2"}]}
    }
    exp_service.case_get.return_value = {
        "id": "case_2",
        "run_info": {
            "status": "successful",
            "consistent": True,
            "datetime_started": 1662964956945,
            "datetime_finished": 1662964957990,
        },
    }
    exp_service.case_get_log.return_value = "Successful Log"
    exp_service.case_result_get.return_value = (bytes(4), IDs.RESULT_MAT)
    exp_service.case_artifact_get.return_value = (bytes(4), IDs.RESULT_MAT)
    exp_service.trajectories_get.return_value = [
        [[1, 2, 3, 4], [14, 4, 4, 74]],
        [[5, 2, 9, 4], [11, 22, 32, 44]],
    ]
    exp_service.case_trajectories_get.return_value = [[14, 4, 4, 74], [11, 22, 32, 44]]
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
    )


@pytest.fixture
def batch_experiment_some_successful():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
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
                {"id": IDs.CASE_PRIMARY},
                {"id": "case_2"},
                {"id": "case_3"},
                {"id": "case_4"},
            ]
        }
    }
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
    )


@pytest.fixture
def running_experiment():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_get.return_value = {"run_info": {"status": "not_started"}}
    exp_service.execute_status.return_value = {"status": "running"}
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
    )


@pytest.fixture
def experiment_with_failed_case():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_get.return_value = {
        "run_info": {"status": "done", "failed": 1, "successful": 0, "cancelled": 0}
    }
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.cases_get.return_value = {"data": {"items": [{"id": IDs.CASE_PRIMARY}]}}
    exp_service.case_get.return_value = {
        "id": IDs.CASE_PRIMARY,
        "run_info": {
            "status": "failed",
            "consistent": True,
            "datetime_started": 1662964956945,
            "datetime_finished": 1662964957990,
        },
    }
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.trajectories_get.return_value = [[[1, 2, 3, 4]], [[5, 2, 9, 4]]]
    exp_service.case_trajectories_get.return_value = [[1, 2, 3, 4], [5, 2, 9, 4]]
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
    )


@pytest.fixture
def failed_experiment():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
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
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service=service
    )


@pytest.fixture
def cancelled_experiment():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_get.return_value = {
        "run_info": {
            "status": "cancelled",
            "failed": 0,
            "successful": 0,
            "cancelled": 1,
        }
    }
    exp_service.cases_get.return_value = {"data": {"items": [{"id": IDs.CASE_PRIMARY}]}}
    exp_service.case_get.return_value = {"id": IDs.CASE_PRIMARY}
    exp_service.execute_status.return_value = {
        "status": "cancelled",
        "consistent": True,
    }
    return create_experiment_entity(
        IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, service
    )


@pytest.fixture
def single_project(user_with_license):
    json = UNVERSIONED_PROJECT
    return with_json_route(
        user_with_license, 'GET', f'api/projects/{IDs.PROJECT_PRIMARY}', json
    )


@pytest.fixture
def multiple_projects(user_with_license):
    json = {"data": {"items": [UNVERSIONED_PROJECT]}}
    return with_json_route(user_with_license, 'GET', 'api/projects', json)


@pytest.fixture
def filtered_projects(user_with_license):
    json = {"data": {"items": [UNVERSIONED_PROJECT]}}
    return with_json_route(
        user_with_license, 'GET', 'api/projects?vcsInfo=False&type=LOCAL', json
    )


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
    service = MagicMock()
    project_service = service.project
    import_service = service.imports
    project_service.projects_get.return_value = {
        "data": {"items": [UNVERSIONED_PROJECT]}
    }
    project_service.project_get.return_value = UNVERSIONED_PROJECT
    project_service.project_content_get.return_value = {
        "id": IDs.PROJECT_CONTENT_SECONDARY,
        "relpath": "test.mo",
        "contentType": "MODELICA",
        "name": "test",
        "defaultDisabled": False,
    }
    project_url = f'api/projects/{IDs.PROJECT_PRIMARY}'
    project_service.project_content_upload.return_value = {
        "data": {"location": f'{project_url}/content-imports/{IDs.IMPORT}'}
    }
    content_url = f'{project_url}/content/{IDs.PROJECT_CONTENT_PRIMARY}'
    import_service.get_import_status.return_value = {
        "data": {
            'id': IDs.IMPORT,
            'status': 'ready',
            'data': {
                'resourceUri': content_url,
                'contentId': IDs.PROJECT_CONTENT_PRIMARY,
            },
        }
    }
    project_service.fmu_import.return_value = {
        "data": {
            "location": f"api/projects/{IDs.PROJECT_PRIMARY}/content/"
            f"{IDs.PROJECT_CONTENT_PRIMARY}/fmu-imports/{IDs.FMU_IMPORT_PRIMARY}"
        }
    }
    project_service.project_options_get.return_value = {
        "compiler": {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        },
        "runtime": {"log_level": 2},
        "simulation": {'dynamic_diagnostics': False, 'ncp': 500},
        "solver": {"rtol": 1e-5},
    }
    project_service.project_default_options_get.return_value = {
        "compiler": {"c_compiler": "gcc"}
    }
    return ProjectMock(
        create_project_entity(IDs.PROJECT_PRIMARY, service=service), service=service
    )


@pytest.fixture
def get_project_content(sem_ver_check, mock_server_base):
    json = {
        "id": IDs.PROJECT_CONTENT_SECONDARY,
        "relpath": "test.mo",
        "contentType": "MODELICA",
        "name": "test",
        "defaultDisabled": False,
    }
    base_url = f'api/projects/{IDs.PROJECT_PRIMARY}'
    url = f'{base_url}/content/{IDs.PROJECT_CONTENT_SECONDARY}'
    return with_json_route(mock_server_base, 'GET', url, json)


@pytest.fixture
def upload_project_content(sem_ver_check, mock_server_base):
    json = {"data": {"location": "some/location"}}
    url = f'api/projects/{IDs.PROJECT_PRIMARY}/content-imports'
    return with_json_route(mock_server_base, 'POST', url, json)


@pytest.fixture
def shared_definition_get(user_with_license, mock_server_base):
    git_url = 'https://github.com/project/test'
    vcs_uri = f'git+{git_url}.git@main:da6abb188a089527df1b54b27ace84274b819e4a'
    json = {
        "definition": {
            "name": "test",
            "projects": [
                {
                    "reference": {
                        "id": IDs.VERSIONED_PROJECT_REFERENCE,
                        "vcsUri": vcs_uri,
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
def get_project_upload_status(user_with_license, mock_server_base):
    json = {
        "data": {
            'id': IDs.IMPORT,
            'status': 'ready',
            'data': {
                'resourceUri': f'api/projects/{IDs.PROJECT_PRIMARY}',
                'projectId': IDs.PROJECT_PRIMARY,
            },
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/project-imports/{IDs.IMPORT}',
        json,
    )


@pytest.fixture
def get_workspace_upload_status(user_with_license, mock_server_base):
    json = {
        "data": {
            'id': IDs.IMPORT,
            'status': 'ready',
            'data': {
                'resourceUri': f'api/workspaces/{IDs.WORKSPACE_PRIMARY}',
                'workspaceId': IDs.WORKSPACE_PRIMARY,
            },
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspace-imports/{IDs.IMPORT}',
        json,
    )


@pytest.fixture
def get_successful_workspace_upload_status(user_with_license, mock_server_base):
    json = {
        "data": {
            "id": IDs.IMPORT,
            "status": "ready",
            "data": {
                'resourceUri': f'api/workspaces/{IDs.WORKSPACE_PRIMARY}',
                'workspaceId': IDs.WORKSPACE_PRIMARY,
            },
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspace-imports/{IDs.IMPORT}',
        json,
    )


@pytest.fixture
def get_failed_workspace_upload_status(user_with_license, mock_server_base):
    git_url = 'https://github.com/project/test'
    vcs_uri = f'git+{git_url}.git@main:da6abb188a089527df1b54b27ace84274b819e4a'
    json = {
        "data": {
            "id": IDs.IMPORT,
            "status": "error",
            "error": {
                "message": "Could not import workspace 'test'. Multiple existing "
                f"projects matches the URI {vcs_uri} and no selected matching was "
                "given",
                "code": 12102,
            },
        }
    }

    return with_json_route(
        mock_server_base,
        'GET',
        f'api/workspace-imports/{IDs.IMPORT}',
        json,
    )


@pytest.fixture
def import_workspace(sem_ver_check, mock_server_base):
    json = {"data": {"location": f"api/workspace-imports/{IDs.IMPORT}"}}

    return with_json_route(mock_server_base, 'POST', 'api/workspace-imports', json)


@pytest.fixture
def import_workspace_project(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "location": f"api/workspaces/{IDs.WORKSPACE_PRIMARY}/project-imports/{IDs.IMPORT}"
        }
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/project-imports',
        json,
    )


@pytest.fixture
def import_workspace_dependency(sem_ver_check, mock_server_base):
    json = {
        "data": {
            "location": f"api/workspaces/{IDs.WORKSPACE_PRIMARY}/dependency-imports/{IDs.IMPORT}"
        }
    }

    return with_json_route(
        mock_server_base,
        'POST',
        f'api/workspaces/{IDs.WORKSPACE_PRIMARY}/dependency-imports',
        json,
    )


@pytest.fixture
def import_project(sem_ver_check, mock_server_base):
    json = {"data": {"location": f"api/project-imports/{IDs.IMPORT}"}}

    return with_json_route(mock_server_base, 'POST', 'api/project-imports', json)


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


@pytest.fixture
def executions(user_with_license, mock_server_base):
    resp = {
        "data": {
            "items": [
                {
                    "status": "running",
                    "workspace": {"id": IDs.WORKSPACE_PRIMARY},
                    "kind": "COMPILATION",
                    "fmu": {"id": IDs.FMU_PRIMARY},
                },
                {
                    "status": "running",
                    "workspace": {"id": IDs.WORKSPACE_SECONDARY},
                    "kind": "EXPERIMENT",
                    "experiment": {"id": IDs.EXPERIMENT_PRIMARY},
                },
            ]
        }
    }
    return with_json_route(
        mock_server_base,
        'GET',
        'api/executions',
        resp,
    )
