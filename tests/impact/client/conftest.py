import collections
import copy
import os
from unittest.mock import MagicMock

import pytest
import requests
import requests_mock

from modelon.impact.client import Client
from modelon.impact.client.options import (
    CompilerOptions,
    SimulationOptions,
    SolverOptions,
)
from modelon.impact.client.sal import exceptions
from tests.impact.client.helpers import (
    UNVERSIONED_PROJECT,
    VERSIONED_PROJECT_BRANCH,
    VERSIONED_PROJECT_TRUNK,
    ClientHelper,
    IDs,
    create_custom_function_entity,
    create_experiment_entity,
    create_model_entity,
    create_model_exe_entity,
    create_published_workspace_entity,
    create_workspace_entity,
    get_test_get_fmu,
    get_test_published_workspace_definition,
    get_test_workspace_definition,
    with_exception,
    with_json_route,
)

ExperimentMock = collections.namedtuple("ExperimentMock", ["entity", "service"])
WorkspaceMock = collections.namedtuple("WorkspaceMock", ["entity", "service"])
PublishedWorkspaceMock = collections.namedtuple(
    "PublishedWorkspaceMock", ["entity", "service"]
)
ProjectMock = collections.namedtuple("ProjectMock", ["entity", "service"])
ModelMock = collections.namedtuple("ModelMock", ["entity", "service"])
MockedServer = collections.namedtuple("MockedServer", ["url", "context", "adapter"])


class MockContex:
    def __init__(self, session):
        self.session = session


@pytest.fixture
def mock_server_base():
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount("http://", adapter)
    mock_url = "http://mock-impact.com"

    mock_server_base = MockedServer(mock_url, MockContex(session), adapter)
    mock_server = with_json_route(
        mock_server_base,
        "GET",
        "hub/api/",
        {},
        extra_headers={},
    )
    return mock_server


@pytest.fixture
def sem_ver_check(mock_server_base):
    json = {"version": "4.18.0"}
    return with_json_route(mock_server_base, "GET", "api/", json)


@pytest.fixture
def user_with_license(sem_ver_check):
    json = {"data": {"license": "impact-pro"}}
    return with_json_route(sem_ver_check, "GET", "api/users/me", json)


@pytest.fixture
def user_with_no_license(sem_ver_check):
    json = {"data": {}}
    return with_json_route(sem_ver_check, "GET", "api/users/me", json)


@pytest.fixture
def key_validation_fails(mock_server_base):
    json = {"error": {"message": "no authorization", "code": 401}}

    return with_json_route(mock_server_base, "GET", "api/users/me", json, 401)


@pytest.fixture
def is_jh_url_uncaught_exception(mock_server_base):
    mock_server = with_exception(
        mock_server_base,
        "GET",
        "hub/api/",
        Exception,
    )
    return mock_server


@pytest.fixture
def is_jh_url_communication_error(mock_server_base):
    mock_server = with_exception(
        mock_server_base,
        "GET",
        "hub/api/",
        exceptions.CommunicationError,
    )
    return mock_server


@pytest.fixture
def create_workspace(user_with_license):
    json = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_ID_PRIMARY,
    }
    return with_json_route(user_with_license, "POST", "api/workspaces", json)


@pytest.fixture
def single_workspace(user_with_license):
    json = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_ID_PRIMARY,
    }
    return with_json_route(
        user_with_license, "GET", f"api/workspaces/{IDs.WORKSPACE_ID_PRIMARY}", json
    )


@pytest.fixture
def semantic_version_error(mock_server_base, user_with_license):
    json = {"version": "1.0.0"}

    return with_json_route(mock_server_base, "GET", "api/", json)


@pytest.fixture
def get_ok_empty_json(mock_server_base):
    return with_json_route(mock_server_base, "GET", "", {})


@pytest.fixture
def get_with_error(mock_server_base):
    json = {"error": {"message": "no authorization", "code": 123}}

    return with_json_route(mock_server_base, "GET", "", json, 401)


@pytest.fixture
def get_with_ssl_exception(mock_server_base):
    return with_exception(mock_server_base, "GET", "", requests.exceptions.SSLError)


def get_upload_status_data(status):
    resource_uri = f"api/external-result/{IDs.EXTERNAL_RESULT_ID}"
    status_data = {
        "data": {
            "id": IDs.IMPORT_ID,
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
    return {"data": {"location": f"api/uploads/results/{IDs.IMPORT_ID}"}}


def get_external_result_data():
    return {
        "data": {
            "id": IDs.EXTERNAL_RESULT_ID,
            "createdAt": "2021-09-02T08:26:49.612000",
            "name": "result_for_PID",
            "description": "This is a result file for PID controller",
            "workspaceId": IDs.WORKSPACE_ID_PRIMARY,
        }
    }


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
        "GET",
        f"api/uploads/results/{IDs.IMPORT_ID}",
        get_upload_result_ready_data(),
    )


@pytest.fixture
def upload_result(sem_ver_check, mock_server_base):
    return with_json_route(
        mock_server_base, "POST", "api/uploads/results", get_result_upload_post_data()
    )


@pytest.fixture
def upload_result_meta(sem_ver_check, mock_server_base):
    return with_json_route(
        mock_server_base,
        "GET",
        f"api/external-result/{IDs.EXTERNAL_RESULT_ID}",
        get_external_result_data(),
    )


@pytest.fixture
def setup_workspace_conversion(sem_ver_check, user_with_license, mock_server_base):
    json = {"data": {"location": f"api/workspace-conversions/{IDs.CONVERSION_ID}"}}
    return with_json_route(mock_server_base, "POST", "api/workspace-conversions", json)


def get_custom_function_url(workspace_id, custom_function_name):
    return f"api/workspaces/{workspace_id}/custom-functions/{custom_function_name}"


def _custom_function_parameter_list():
    return [
        {"name": "p1", "defaultValue": 1.0, "type": "Number"},
        {"name": "p2", "defaultValue": True, "type": "Boolean"},
        {
            "name": "p3",
            "defaultValue": "hej",
            "type": "Enumeration",
            "values": ["hej", "då"],
        },
        {"name": "p4", "defaultValue": "a string", "type": "String"},
        {"name": "p5", "defaultValue": 0.0, "type": "Number"},
        {"name": "p6", "defaultValue": "", "type": "ExperimentResult"},
        {"name": "p7", "defaultValue": "", "type": "CaseResult"},
        {"name": "p8", "defaultValue": "", "type": "FileURI"},
        {"name": "p9", "defaultValue": "", "type": "FileURI"},
        {"name": "p10", "defaultValue": [], "type": "VariableNames"},
    ]


@pytest.fixture
def publish_workspace():
    service = MagicMock()
    ws_service = service.workspace
    import_service = service.imports
    import_service.get_import_status.return_value = {
        "data": {
            "id": IDs.IMPORT_ID,
            "status": "ready",
            "data": {
                "resourceUri": f"api/workspace-imports/{IDs.IMPORT_ID}",
                "workspaceId": IDs.WORKSPACE_ID_PRIMARY,
            },
        }
    }
    ws_service.workspace_get.return_value = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_ID_PRIMARY,
        "sizeInfo": {"total": 7014},
    }
    ws_service.import_from_cloud.return_value = {
        "data": {"location": f"api/workspace-imports/{IDs.IMPORT_ID}"}
    }
    definition = get_test_published_workspace_definition()
    ws_service.get_published_workspace.return_value = {
        "id": IDs.PUBLISHED_WORKSPACE_ID,
        **definition,
    }
    ws_service.get_published_workspace_acl.return_value = {
        "roleNames": [],
        "groupNames": [IDs.GROUP_NAME],
        "sharedWith": [
            {
                "id": IDs.USER_ID,
                "username": IDs.USERNAME,
            }
        ],
        "requestedBy": [],
    }
    return PublishedWorkspaceMock(
        create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID,
            IDs.WORKSPACE_ID_PRIMARY,
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
            "id": IDs.IMPORT_ID,
            "status": "ready",
            "data": {
                "resourceUri": f"api/projects/{IDs.PROJECT_ID_PRIMARY}",
                "projectId": IDs.PROJECT_ID_PRIMARY,
            },
        }
    }
    export_service.export_download.return_value = b"undjnvsjnvj"
    ws_service.update_workspace.return_value = {
        "definition": get_test_workspace_definition(IDs.WORKSPACE_ID_SECONDARY),
        "id": IDs.WORKSPACE_ID_PRIMARY,
    }
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_ID_PRIMARY
    }
    ws_service.fmus_get.return_value = {
        "data": {"items": [{"id": IDs.FMU_ID_PRIMARY}, {"id": IDs.FMU_ID_SECONDARY}]}
    }
    ws_service.fmu_get.return_value = {"id": IDs.FMU_ID_PRIMARY}
    ws_service.project_create.return_value = {
        "id": IDs.PROJECT_ID_PRIMARY,
        "definition": {
            "name": "my_project",
            "format": "1.0",
            "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
            "content": [
                {
                    "id": IDs.PROJECT_CONTENT_ID_PRIMARY,
                    "relpath": "MyPackage",
                    "contentType": "MODELICA",
                    "name": "MyPackage",
                    "defaultDisabled": False,
                }
            ],
            "executionOptions": [],
        },
        "projectType": "LOCAL",
        "storageLocation": "USERSPACE",
    }
    ws_service.experiment_get.return_value = {"id": IDs.EXPERIMENT_ID_PRIMARY}
    exp_service.execute_status.return_value = {"status": "done"}
    ws_service.experiments_get.return_value = {
        "data": {
            "items": [
                {"id": IDs.EXPERIMENT_ID_PRIMARY},
                {"id": IDs.EXPERIMENT_ID_SECONDARY},
            ]
        }
    }
    ws_service.workspace_download.return_value = b"\x00\x00\x00\x00"
    ws_service.workspace_get.return_value = {
        "definition": get_test_workspace_definition(),
        "id": IDs.WORKSPACE_ID_PRIMARY,
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
                    "storageLocation": "SYSTEM",
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
                    "storageLocation": "SYSTEM",
                },
            ]
        }
    }
    ws_service.workspace_export_setup.return_value = {
        "data": {"location": f"api/workspace-exports/{IDs.EXPORT_ID}"}
    }
    export_service.get_export_status.return_value = {
        "data": {
            "id": IDs.EXPORT_ID,
            "status": "ready",
            "data": {"downloadUri": f"api/exports/{IDs.EXPORT_ID}", "size": 10481015},
            "error": {},
        }
    }
    custom_function_service.custom_function_get.return_value = {
        "name": IDs.DYNAMIC_CF,
        "parameters": _custom_function_parameter_list(),
    }
    custom_function_service.custom_functions_get.return_value = {
        "data": {
            "items": [
                {
                    "name": IDs.DYNAMIC_CF,
                    "parameters": _custom_function_parameter_list(),
                }
            ]
        }
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_ID_PRIMARY
    project_service.project_get.return_value = UNVERSIONED_PROJECT
    ws_service.import_project_from_zip.return_value = {
        "data": {
            "location": f"api/workspaces/{IDs.WORKSPACE_ID_PRIMARY}/project-imports"
            f"/{IDs.IMPORT_ID}"
        }
    }
    ws_service.import_dependency_from_zip.return_value = {
        "data": {
            "location": f"api/workspaces/{IDs.WORKSPACE_ID_PRIMARY}/dependency-imports/"
            f"{IDs.IMPORT_ID}"
        }
    }
    return WorkspaceMock(
        create_workspace_entity(IDs.WORKSPACE_ID_PRIMARY, service=service), service
    )


@pytest.fixture
def workspace_execute_running():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_ID_PRIMARY
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_ID_PRIMARY
    exp_service.execute_status.return_value = {"status": "running"}
    return create_workspace_entity(IDs.WORKSPACE_ID_PRIMARY, service=service)


@pytest.fixture
def workspace_execute_cancelled():
    service = MagicMock()
    ws_service = service.workspace
    exp_service = service.experiment
    ws_service.experiment_create.return_value = {
        "experiment_id": IDs.EXPERIMENT_ID_PRIMARY
    }
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_ID_PRIMARY
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return create_workspace_entity(IDs.WORKSPACE_ID_PRIMARY, service=service)


@pytest.fixture
def workspace_ops(single_workspace):
    client = Client(url=single_workspace.url, context=single_workspace.context)
    return client.get_workspace(IDs.WORKSPACE_ID_PRIMARY)


@pytest.fixture
def custom_function():
    service = MagicMock()
    custom_function_service = service.custom_function
    custom_function_service.custom_function_get.return_value = {
        "name": IDs.DYNAMIC_CF,
        "parameters": _custom_function_parameter_list(),
    }
    custom_function_service.custom_function_options_get.return_value = {
        "compiler": {"c_compiler": "gcc"},
        "runtime": {"cs_solver": 0},
        "simulation": {"ncp": 500},
        "solver": {"atol": 1e-7, "rtol": 1e-9},
    }
    custom_function_service.custom_function_default_options_get.return_value = {
        "compiler": {"c_compiler": "msvs"},
        "runtime": {"log_level": 2},
        "simulation": {"ncp": 500},
        "solver": {"rtol": 1e-5},
    }
    return create_custom_function_entity(
        IDs.WORKSPACE_ID_PRIMARY,
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
        IDs.WORKSPACE_ID_PRIMARY, IDs.DYNAMIC_CF, [], service=service
    )


@pytest.fixture
def model_compiled():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_ID_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "done"}
    return create_model_entity(
        IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_ID_PRIMARY,
        IDs.PROJECT_ID_PRIMARY,
        service,
    )


@pytest.fixture
def model_cached():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (IDs.FMU_ID_PRIMARY, {})
    model_exe_service.compile_status.return_value = {"status": "done"}
    return create_model_entity(
        IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_ID_PRIMARY,
        IDs.PROJECT_ID_PRIMARY,
        service,
    )


@pytest.fixture
def model_compiling():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_ID_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "running"}
    return create_model_entity(
        IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_ID_PRIMARY,
        IDs.PROJECT_ID_PRIMARY,
        service,
    )


@pytest.fixture
def model_compile_cancelled():
    service = MagicMock()
    model_exe_service = service.model_executable
    model_exe_service.fmu_setup.return_value = (None, {})
    model_exe_service.compile_model.return_value = IDs.FMU_ID_PRIMARY
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return create_model_entity(
        IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
        IDs.WORKSPACE_ID_PRIMARY,
        IDs.PROJECT_ID_PRIMARY,
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
    ws_service.fmu_download.return_value = b"\x00\x00\x00\x00"
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.settable_parameters_get.return_value = ["h0", "v"]
    model_exe_service.compile_log.return_value = "Successful Log"
    model_exe_service.fmu_setup.return_value = (IDs.FMU_ID_PRIMARY, {})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return create_model_exe_entity(
        IDs.WORKSPACE_ID_PRIMARY, IDs.FMU_ID_PRIMARY, service=service
    )


@pytest.fixture
def fmu_with_modifiers():
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = get_test_get_fmu()
    ws_service.fmu_download.return_value = b"\x00\x00\x00\x00"
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.settable_parameters_get.return_value = ["h0", "v"]
    model_exe_service.compile_log.return_value = "Successful Log"
    model_exe_service.fmu_setup.return_value = (IDs.FMU_ID_PRIMARY, {"PI.K": 20})
    model_exe_service.ss_fmu_metadata_get.return_value = {
        "steady_state": {"residual_variable_count": 1, "iteration_variable_count": 2}
    }
    return create_model_exe_entity(
        IDs.WORKSPACE_ID_PRIMARY,
        IDs.FMU_ID_PRIMARY,
        service=service,
        modifiers={"PI.K": 20},
    )


@pytest.fixture
def model():
    service = MagicMock()
    import_service = service.imports
    import_service.get_import_status.return_value = {
        "data": {
            "id": IDs.IMPORT_ID,
            "status": "ready",
            "data": {
                "resourceUri": f"api/projects/{IDs.PROJECT_ID_PRIMARY}/content"
                f"/{IDs.PROJECT_CONTENT_ID_PRIMARY}",
                "fmuClassPath": IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH + ".test",
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
        "simulation": {"dynamic_diagnostics": False, "ncp": 500},
        "solver": {"rtol": 1e-5},
    }
    project_service.project_get.return_value = UNVERSIONED_PROJECT
    project_service.fmu_import.return_value = {
        "data": {
            "location": f"api/projects/{IDs.PROJECT_ID_PRIMARY}/content/"
            f"{IDs.PROJECT_CONTENT_ID_PRIMARY}/fmu-imports/{IDs.FMU_IMPORT_PRIMARY}"
        }
    }
    return ModelMock(
        create_model_entity(
            IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
            IDs.WORKSPACE_ID_PRIMARY,
            IDs.PROJECT_ID_PRIMARY,
            service,
        ),
        service=service,
    )


@pytest.fixture
def fmu_compile_failed():
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = {"run_info": {"status": "failed"}}
    model_exe_service.compile_status.return_value = {"status": "done"}
    model_exe_service.compile_log.return_value = "Failed Log"
    return create_model_exe_entity(
        IDs.WORKSPACE_ID_PRIMARY, IDs.FMU_ID_PRIMARY, service
    )


@pytest.fixture
def fmu_compile_cancelled():
    service = MagicMock()
    ws_service = service.workspace
    model_exe_service = service.model_executable
    ws_service.fmu_get.return_value = {"run_info": {"status": "cancelled"}}
    model_exe_service.compile_status.return_value = {"status": "cancelled"}
    return create_model_exe_entity(
        IDs.WORKSPACE_ID_PRIMARY, IDs.FMU_ID_PRIMARY, service
    )


@pytest.fixture
def experiment():
    service = MagicMock()
    exp_service = service.experiment
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_ID_PRIMARY
    exp_service.execute_status.return_value = {"status": "done"}
    exp_service.result_variables_get.return_value = ["inertia.I", "time"]
    exp_service.cases_get.return_value = {
        "data": {"items": [{"id": IDs.CASE_ID_PRIMARY}]}
    }
    case_get_data = {
        "id": IDs.CASE_ID_PRIMARY,
        "run_info": {
            "status": "successful",
            "consistent": True,
            "datetime_started": 1662964956945,
            "datetime_finished": 1662964957990,
        },
        "input": {
            "fmuId": IDs.FMU_ID_PRIMARY,
            "analysis": {},
            "parametrization": {},
        },
        "meta": {"label": "Cruise operating point"},
    }
    case_put_return = copy.deepcopy(case_get_data)
    case_put_return["run_info"]["consistent"] = False

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
            IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY, service=service
        ),
        service,
    )


@pytest.fixture
def experiment_running():
    service = MagicMock()
    exp_service = service.experiment
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_ID_PRIMARY
    exp_service.case_get.return_value = {"id": IDs.CASE_ID_PRIMARY}
    exp_service.execute_status.return_value = {"status": "running"}
    return create_experiment_entity(
        IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY, service
    )


@pytest.fixture
def experiment_cancelled():
    service = MagicMock()
    exp_service = service.experiment
    exp_service.experiment_execute.return_value = IDs.EXPERIMENT_ID_PRIMARY
    exp_service.case_get.return_value = {"id": IDs.CASE_ID_PRIMARY}
    exp_service.execute_status.return_value = {"status": "cancelled"}
    return create_experiment_entity(
        IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY, service=service
    )


@pytest.fixture
def get_successful_workspace_upload_status(user_with_license, mock_server_base):
    json = {
        "data": {
            "id": IDs.IMPORT_ID,
            "status": "ready",
            "data": {
                "resourceUri": f"api/workspaces/{IDs.WORKSPACE_ID_PRIMARY}",
                "workspaceId": IDs.WORKSPACE_ID_PRIMARY,
            },
        }
    }

    return with_json_route(
        mock_server_base,
        "GET",
        f"api/workspace-imports/{IDs.IMPORT_ID}",
        json,
    )


@pytest.fixture
def get_failed_workspace_upload_status(user_with_license, mock_server_base):
    git_url = "https://github.com/project/test"
    vcs_uri = f"git+{git_url}.git@main:da6abb188a089527df1b54b27ace84274b819e4a"
    json = {
        "data": {
            "id": IDs.IMPORT_ID,
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
        "GET",
        f"api/workspace-imports/{IDs.IMPORT_ID}",
        json,
    )


@pytest.fixture
def import_workspace(sem_ver_check, mock_server_base):
    json = {"data": {"location": f"api/workspace-imports/{IDs.IMPORT_ID}"}}

    return with_json_route(mock_server_base, "POST", "api/workspace-imports", json)


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
        mock_server_base, "POST", "api/workspace-imports-matchings", json
    )


@pytest.fixture
def get_versioned_projects(user_with_license, mock_server_base):
    json = {"data": {"items": [VERSIONED_PROJECT_TRUNK, VERSIONED_PROJECT_BRANCH]}}

    return with_json_route(mock_server_base, "GET", "api/projects?vcsInfo=true", json)


@pytest.fixture
def get_versioned_new_project_trunk(user_with_license, mock_server_base):
    return with_json_route(
        mock_server_base,
        "GET",
        f"api/projects/{IDs.VERSIONED_PROJECT_PRIMARY}?vcsInfo=true",
        VERSIONED_PROJECT_TRUNK,
    )


@pytest.fixture
def get_versioned_new_project_branch(user_with_license, mock_server_base):
    return with_json_route(
        mock_server_base,
        "GET",
        f"api/projects/{IDs.VERSIONED_PROJECT_SECONDARY}?vcsInfo=true",
        VERSIONED_PROJECT_BRANCH,
    )


@pytest.fixture(name="client_helper")
def setup_client():
    if os.environ.get("UPDATE_CASSETTE", "False") not in ["True", "1"]:
        os.environ["MODELON_IMPACT_CLIENT_API_KEY"] = "dummy"
        os.environ["MODELON_IMPACT_USERNAME"] = IDs.USERNAME
    client = Client()
    assert client._sal.users.get_me()["data"]["username"].lower() in [
        os.environ.get("MODELON_IMPACT_USERNAME", "").lower(),
        IDs.USERNAME,
        os.environ.get("JUPYTERHUB_USER"),
    ]
    _clean_workspace_and_its_projects(client)
    yield ClientHelper(client)
    _clean_workspace_and_its_projects(client)


def _clean_workspace_and_its_projects(client: Client):
    for workspace in client.get_workspaces():
        if any(
            workspace.name.startswith(workspace_name)
            for workspace_name in IDs.WORKSPACE_NAMES
        ):
            for project in workspace.get_projects():
                project.delete()
            workspace.delete()
