from typing import Union
from unittest.mock import MagicMock

from modelon.impact.client import Client, Range, SimpleModelicaExperimentDefinition
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.custom_artifact import CustomArtifact
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.entities.experiment import Experiment, _Workflow
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.interfaces.case import CaseReference
from modelon.impact.client.entities.interfaces.experiment import ExperimentReference
from modelon.impact.client.entities.model import CompilationOperations, Model
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.workspace import (
    PublishedWorkspace,
    PublishedWorkspaceDefinition,
    Workspace,
)
from modelon.impact.client.experiment_definition.fmu_based import (
    SimpleFMUExperimentDefinition,
)
from modelon.impact.client.operations.experiment import ExperimentOperation
from modelon.impact.client.operations.model_executable import (
    CachedModelExecutableOperation,
    ModelExecutableOperation,
)
from modelon.impact.client.operations.workspace.conversion import (
    WorkspaceConversionOperation,
)


def json_request_list_item(json_response, status_code=200, extra_headers=None):
    extra_headers = extra_headers or {}
    json_header = {"content-type": "application/json", **extra_headers}
    return {"json": json_response, "status_code": status_code, "headers": json_header}


def with_json_route(
    mock_server_base, method, url, json_response, status_code=200, extra_headers=None
):
    request_list = [json_request_list_item(json_response, status_code, extra_headers)]
    return with_json_request_list_route(mock_server_base, method, url, request_list)


def with_json_request_list_route(mock_server_base, method, url, request_list):
    mock_server_base.adapter.register_uri(
        method, f"{mock_server_base.url}/{url}", request_list
    )
    return mock_server_base


def with_exception(mock_server_base, method, url, exce):
    mock_server_base.adapter.register_uri(
        method, f"{mock_server_base.url}/{url}", exc=exce
    )
    return mock_server_base


def with_json_route_no_resp(mock_server_base, method, url, status_code=200):
    mock_server_base.adapter.register_uri(
        method,
        f"{mock_server_base.url}/{url}",
        status_code=status_code,
    )
    return mock_server_base


def with_zip_route(mock_server_base, method, url, zip_response, status_code=200):
    content = zip_response
    content_header = {"content-type": "application/zip"}
    mock_server_base.adapter.register_uri(
        method,
        f"{mock_server_base.url}/{url}",
        content=content,
        headers=content_header,
        status_code=status_code,
    )
    return mock_server_base


def with_text_route(mock_server_base, method, url, text_response, status_code=200):
    text = text_response
    text_header = {"content-type": "text/plain"}
    mock_server_base.adapter.register_uri(
        method,
        f"{mock_server_base.url}/{url}",
        text=text,
        headers=text_header,
        status_code=status_code,
    )
    return mock_server_base


def with_xml_route(mock_server_base, method, url, xml_response, status_code=200):
    xml = xml_response
    xml_header = {"content-type": "application/xml"}
    mock_server_base.adapter.register_uri(
        method,
        f"{mock_server_base.url}/{url}",
        text=xml,
        headers=xml_header,
        status_code=status_code,
    )
    return mock_server_base


def with_csv_route(
    mock_server_base, method, url, text_response, status_code=200, content_header=None
):
    text = text_response
    content_header = (
        {
            "content-type": "text/csv",
            "content-disposition": "attachment; "
            'filename="BouncingBall_2020-09-01_14-33_case_1.csv"',
            "connection": "close",
            "date": "Tue, 01 Sep 2020 14:33:56 GMT",
            "server": "127.0.0.1",
            "Transfer-Encoding": "chunked",
        }
        if content_header is None
        else content_header
    )
    mock_server_base.adapter.register_uri(
        method,
        f"{mock_server_base.url}/{url}",
        text=text,
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
            "content-type": "application/octet-stream",
            "content-disposition": "attachment; "
            'filename="BouncingBall_2020-09-01_14-33_case_1.mat"',
            "connection": "close",
            "date": "Tue, 01 Sep 2020 14:33:56 GMT",
            "server": "127.0.0.1",
            "Transfer-Encoding": "chunked",
        }
        if content_header is None
        else content_header
    )
    mock_server_base.adapter.register_uri(
        method,
        f"{mock_server_base.url}/{url}",
        content=content,
        headers=content_header,
        status_code=status_code,
    )
    return mock_server_base


class IDs:
    MOCK_EMAIL = "test-user@modelon.com"
    MOCK_IMPACT_URL = "https://modelon-test.com/"
    _WORKSPACE_ID_PREFIX = "impact-python-client-"
    WORKSPACE_ID_PRIMARY = _WORKSPACE_ID_PREFIX + "workspace1"
    WORKSPACE_ID_SECONDARY = _WORKSPACE_ID_PREFIX + "workspace2"
    WORKSPACE_IDS = [WORKSPACE_ID_PRIMARY, WORKSPACE_ID_SECONDARY]
    WORKSPACE_NAMES = WORKSPACE_IDS
    USER_ID = "njcswjcjnscksnckjsnckndsk"
    USERNAME = "test-user"
    TENANT_ID = "org1"
    GROUP_NAME = "impact-tenant-org1"
    PRO_LICENSE_ROLE = "impact-pro"
    LICENSE_ROLES = [
        "impact-editor",
        "offline_access",
        "impact-viewer",
        "uma_authorization",
        "default-roles-modelon",
        PRO_LICENSE_ROLE,
        "impact-executor",
        "impact-workspace-publisher",
    ]
    UMA_ROLE = "impact-workspace-uma"
    PUBLISHED_WORKSPACE_ID = "ekdncjndjcndejncjsncsndcijdsnc"
    DEFAULT_PROJECT_NAME = "Project"
    PROJECT_NAME_PRIMARY = "Project1"
    PROJECT_ID_PRIMARY = "bf1e2f2a2fd55dcfd844bc1f252528f707254425"
    PROJECT_ID_SECONDARY = "xbhcdhcbdbchdbhcbdhbchdchdhcbhdbchdbch"
    PROJECT_CONTENT_ID_PRIMARY = "81ac23172d7a479db85126691e090b34"
    PROJECT_CONTENT_ID_SECONDARY = "f727f04210b94a0fac81f17f83b869e6"
    FMU_IMPORT_PRIMARY = "1nj2jn3jnjnjnfnvjewjnnmsjnjijiwwwll"
    VERSIONED_PROJECT_REFERENCE = "4019c58d4a3b41fc463934274ece3f9a0ac27436"
    VERSIONED_PROJECT_PRIMARY = "c1f1d74f0b612c6b67e4165bf9a1ad30b2630039"
    VERSIONED_PROJECT_SECONDARY = "da282cc77feaa60fc93879a7f39e27ab78304940"
    MSL_400_PROJECT_ID = "cdbde8922bd2c48c392b1b4bb740adc0273c737c"
    MSL_300_PROJECT_ID = "84fb1c37abe6ed97a53972fb7239630e1212438b"
    MSL_CONTENT_ID = "925cbe6daaf3ebde61dfcc2a26f93e6d0798085a"
    FMU_ID_PRIMARY = "test_pid_fmu_id"
    FMU_ID_SECONDARY = "test_filter_fmu_id"
    EXPERIMENT_ID_PRIMARY = "pid_20090615_134"
    EXPERIMENT_ID_SECONDARY = "filter_20090615_135"
    CASE_ID_PRIMARY = "case_1"
    CASE_ID_SECONDARY = "case_2"
    IMPORT_ID = "9a8fg798a7g"
    EXPORT_ID = "79sd8-3n2a4-e3t24"
    CONVERSION_ID = "t24e3-a43n2-d879s"
    DYNAMIC_CF = "dynamic"
    EXTERNAL_RESULT_ID = IMPORT_ID
    CUSTOM_ARTIFACT_ID = "ABCD"
    RESULT_MAT = "result.mat"
    PID_MODELICA_CLASS_PATH = "Modelica.Blocks.Examples.PID_Controller"
    BATCH_PLANT_MODELICA_CLASS_PATH = (
        "Modelica.Fluid.Examples.AST_BatchPlant.BatchPlant_StandardWater"
    )
    FILTER_MODELICA_CLASS_PATH = "Modelica.Blocks.Examples.Filter"
    LOCAL_PROJECT_MODELICA_CLASS_PATH = "Test.PID"
    EXPERIMENT_LABEL = "EXPERIMENT_LABEL"
    ARTIFACT_RESOURCE_URI = (
        f"impact-artifact://workspace/{EXPERIMENT_ID_PRIMARY}/"
        f"{CASE_ID_PRIMARY}/{CUSTOM_ARTIFACT_ID}"
    )
    MODELICA_RESOURCE_PATH = "Resources/Data/Electrical/Digital/Memory_Matrix.txt"
    MODELICA_RESOURCE_URI = f"modelica://Modelica/{MODELICA_RESOURCE_PATH}"


UNVERSIONED_PROJECT = {
    "id": IDs.PROJECT_ID_PRIMARY,
    "definition": {
        "name": "NewProject",
        "format": "1.0",
        "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
        "content": [
            {
                "id": IDs.PROJECT_CONTENT_ID_PRIMARY,
                "relpath": IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
                "contentType": "MODELICA",
                "name": IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
                "defaultDisabled": False,
            }
        ],
        "executionOptions": [],
    },
    "projectType": "LOCAL",
    "storageLocation": "USERSPACE",
    "size": 1008,
}

VERSIONED_PROJECT_TRUNK = {
    "id": IDs.VERSIONED_PROJECT_PRIMARY,
    "definition": {
        "name": "NewProjectTrunk",
        "format": "1.0",
        "content": [
            {
                "id": IDs.PROJECT_CONTENT_ID_PRIMARY,
                "relpath": "MyPackage",
                "contentType": "MODELICA",
                "name": "MyPackage",
                "defaultDisabled": False,
            }
        ],
    },
    "projectType": "LOCAL",
    "storageLocation": "USERSPACE",
    "vcsUri": {
        "serviceKind": "git",
        "serviceUrl": "https://github.com",
        "repoUrl": {
            "url": "github.com/project/test.git",
            "refname": "master",
            "sha1": "cd8fe4f6e2bff02f88fc1baeb7260c83160ee927",
        },
        "protocol": "https",
        "subdir": ".",
    },
}
VERSIONED_PROJECT_BRANCH = {
    "id": IDs.VERSIONED_PROJECT_SECONDARY,
    "definition": {
        "name": "NewProjectBranch",
        "format": "1.0",
        "content": [
            {
                "id": IDs.PROJECT_CONTENT_ID_SECONDARY,
                "relpath": "MyPackage",
                "contentType": "MODELICA",
                "name": "MyPackage",
                "defaultDisabled": False,
            }
        ],
    },
    "projectType": "LOCAL",
    "storageLocation": "USERSPACE",
    "vcsUri": {
        "serviceKind": "git",
        "serviceUrl": "https://github.com",
        "repoUrl": {
            "url": "github.com/project/test.git",
            "refname": "master",
            "sha1": "incndcj6e2bff02f88fc1baeb7260c83160ee927",
        },
        "protocol": "https",
        "subdir": ".",
    },
}


def get_test_get_fmu():
    return {
        "id": IDs.FMU_ID_PRIMARY,
        "input": {
            "class_name": IDs.PID_MODELICA_CLASS_PATH,
            "compiler_options": {"c_compiler": "gcc"},
            "runtime_options": {"a": 1},
            "compiler_log_level": "w",
            "fmi_target": "me",
            "fmi_version": "2.0",
            "platform": "auto",
            "model_snapshot": "1610523986117",
            "toolchain_version": "0.0.1",
            "compiled_on_sys": "win32",
        },
        "run_info": {
            "status": "successful",
            "datetime_started": 1610523986193,
            "errors": [],
            "datetime_finished": 1610523990763,
        },
        "meta": {
            "created_epoch": 1610523986,
            "input_hash": "f47e0d051a804eee3cde3e3d98da5f39",
            "fmu_file": "model.fmu",
        },
    }


def get_test_fmu_experiment_definition():
    return {
        "id": IDs.EXPERIMENT_ID_PRIMARY,
        "experiment": {
            "version": 2,
            "base": {
                "model": {"fmu": {"id": IDs.FMU_ID_PRIMARY}},
                "modifiers": {"variables": {}},
                "analysis": {
                    "type": "dynamic",
                    "parameters": {"start_time": 0, "final_time": 1, "interval": 0},
                    "simulationOptions": {"ncp": 500, "dynamic_diagnostics": False},
                    "solverOptions": {"solver": "Cvode"},
                    "simulationLogLevel": "WARNING",
                },
            },
            "extensions": [],
        },
        "meta_data": {
            "created_epoch": 1682399802,
            "experiment_hash": "7a9aac52afbe7452f236105f4c864ae4",
            "label": "",
            "model_names": [IDs.PID_MODELICA_CLASS_PATH],
        },
        "run_info": {
            "status": "done",
            "datetime_started": 1682399802753,
            "datetime_finished": 1682399803066,
            "failed": 0,
            "successful": 1,
            "cancelled": 0,
            "not_started": 0,
        },
    }


def get_test_modelica_experiment_definition():
    return {
        "id": IDs.EXPERIMENT_ID_PRIMARY,
        "experiment": {
            "version": 2,
            "base": {
                "model": {
                    "modelica": {
                        "className": IDs.PID_MODELICA_CLASS_PATH,
                        "compilerOptions": {
                            "c_compiler": "gcc",
                        },
                        "runtimeOptions": {"a": 1},
                        "compilerLogLevel": "warning",
                        "fmiTarget": "me",
                        "fmiVersion": "2.0",
                        "platform": "auto",
                    }
                },
                "modifiers": {"variables": {}},
                "analysis": {
                    "type": "dynamic",
                    "parameters": {"start_time": 0, "final_time": 1, "interval": 0},
                    "simulationOptions": {"ncp": 500, "dynamic_diagnostics": False},
                    "solverOptions": {"solver": "Cvode"},
                    "simulationLogLevel": "WARNING",
                },
                "expansion": {"algorithm": "FULLFACTORIAL"},
            },
            "extensions": [],
        },
        "meta_data": {
            "created_epoch": 1682399102,
            "experiment_hash": "c32aa5210e066950a62db469158aeb43",
            "label": IDs.EXPERIMENT_LABEL,
            "model_names": [IDs.PID_MODELICA_CLASS_PATH],
        },
        "run_info": {
            "status": "done",
            "datetime_started": 1682399102855,
            "datetime_finished": 1682399106597,
            "failed": 0,
            "successful": 1,
            "cancelled": 0,
            "not_started": 0,
        },
    }


def get_test_published_workspace_definition(name=None):
    return {
        "createdAt": 0,
        "ownerUsername": IDs.USERNAME,
        "size": 10,
        "status": "created",
        "tenantId": IDs.TENANT_ID,
        "workspaceName": name if name else IDs.WORKSPACE_ID_PRIMARY,
    }


def get_test_workspace_definition(name=None):
    git_url = "https://github.com/project/test"
    vcs_uri = f"git+{git_url}.git@main:da6abb188a089527df1b54b27ace84274b819e4a"
    return {
        "name": name if name else IDs.WORKSPACE_ID_PRIMARY,
        "format": "1.0",
        "description": "",
        "createdBy": "local-installation-user-id",
        "createdAt": "1659072911361",
        "defaultProjectId": IDs.PROJECT_ID_PRIMARY,
        "projects": [
            {
                "reference": {"id": IDs.PROJECT_ID_PRIMARY},
                "disabled": False,
                "disabledContent": [],
            },
            {
                "reference": {
                    "id": IDs.VERSIONED_PROJECT_REFERENCE,
                    "vcsUri": vcs_uri,
                },
                "disabled": True,
                "disabledContent": [],
            },
        ],
        "dependencies": [
            {
                "reference": {
                    "id": IDs.MSL_300_PROJECT_ID,
                    "name": "MSL",
                    "version": "3.2.3",
                },
                "disabled": True,
                "disabledContent": [],
            },
            {
                "reference": {
                    "id": IDs.MSL_400_PROJECT_ID,
                    "name": "MSL",
                    "version": "4.0.0",
                },
                "disabled": False,
                "disabledContent": [],
            },
        ],
    }


def create_workspace_entity(workspace_id, definition=None, service=None):
    service = service or MagicMock()
    if definition:
        service.workspace_get.return_value = {
            "definition": definition,
            "id": workspace_id,
        }
    return Workspace(workspace_id, service or MagicMock())


def create_published_workspace_entity(id, name, definition=None, service=None):
    definition = definition or get_test_published_workspace_definition(name)
    definition = PublishedWorkspaceDefinition.from_dict(definition)
    return PublishedWorkspace(id, definition, service or MagicMock())


def create_model_entity(class_name, workspace_id, project_id, service=None):
    return Model(class_name, workspace_id, project_id, service or MagicMock())


def create_model_exe_entity(
    workspace_id, fmu_id, service=None, info=None, modifiers=None
):
    return ModelExecutable(
        workspace_id, fmu_id, service or MagicMock(), info, modifiers
    )


def create_experiment_entity(workspace_id, exp_id, service=None, info=None):
    return Experiment(workspace_id, exp_id, service or MagicMock(), info)


def create_experiment_reference(workspace_id, exp_id, service=None, info=None):
    return ExperimentReference(workspace_id, exp_id, service or MagicMock(), info)


def create_case_reference(workspace_id, case_id, exp_id, service=None, info=None):
    return CaseReference(case_id, workspace_id, exp_id, service or MagicMock(), info)


def create_case_entity(case_id, workspace_id, exp_id, service=None, info=None):
    return Case(
        case_id, workspace_id, exp_id, service or MagicMock(), info or MagicMock()
    )


def create_custom_artifact_entity(
    case_id, workspace_id, exp_id, artifact_id, download_as
):
    return CustomArtifact(
        workspace_id, exp_id, case_id, artifact_id, download_as, exp_sal=MagicMock()
    )


def create_external_result_entity(result_id, service=None):
    return ExternalResult(result_id, service or MagicMock())


def create_custom_function_entity(
    workspace_id, name, parameter_data=None, service=None
):
    return CustomFunction(
        workspace_id, name, parameter_data or [], service or MagicMock()
    )


def create_experiment_operation(workspace_id, exp_id, service=None):
    return ExperimentOperation[Experiment](
        workspace_id, exp_id, service or MagicMock(), Experiment.from_operation
    )


def create_cached_model_exe_operation(
    workspace_id, fmu_id, service=None, info=None, modifiers=None
):
    return CachedModelExecutableOperation[ModelExecutable](
        workspace_id,
        fmu_id,
        service or MagicMock(),
        ModelExecutable.from_operation,
        info=info,
        modifiers=modifiers,
    )


def create_model_exe_operation(workspace_id, fmu_id, service=None):
    return ModelExecutableOperation[ModelExecutable](
        workspace_id, fmu_id, service or MagicMock(), ModelExecutable.from_operation
    )


def create_workspace_conversion_operation(ws_conversion_id, service=None):
    return WorkspaceConversionOperation[Workspace](
        f"api/workspace-conversions/{ws_conversion_id}",
        service or MagicMock(),
        Workspace.from_conversion_operation,
    )


class ClientHelper:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.workspace = self.client.create_workspace(IDs.WORKSPACE_ID_PRIMARY)

    def create_and_execute_experiment(
        self,
        model_path=IDs.PID_MODELICA_CLASS_PATH,
        workflow=_Workflow.CLASS_BASED,
        modifiers=None,
        user_data=None,
        custom_function_params=None,
        wait_for_completion=True,
    ) -> Union[Experiment, ExperimentOperation]:
        exp = self.create_experiment(
            model_path, workflow, modifiers, user_data, custom_function_params
        ).execute()
        if wait_for_completion:
            return exp.wait()
        return exp

    def compile_fmu(
        self,
        model_path=IDs.PID_MODELICA_CLASS_PATH,
        custom_function_name="dynamic",
        custom_function_params=None,
        wait_for_completion=True,
    ):
        custom_function = self.workspace.get_custom_function(custom_function_name)
        if custom_function_params:
            custom_function = custom_function.with_parameters(**custom_function_params)
        model = self.workspace.get_model(model_path)
        ops: CompilationOperations = model.compile(
            compiler_options=custom_function.get_compiler_options()
        )
        if wait_for_completion:
            fmu: ModelExecutable = ops.wait()
            return fmu
        return ops

    def create_experiment(
        self,
        model_path=IDs.PID_MODELICA_CLASS_PATH,
        workflow=_Workflow.CLASS_BASED,
        modifiers=None,
        user_data=None,
        custom_function_params=None,
    ) -> Experiment:
        dynamic = self.workspace.get_custom_function("dynamic")
        if custom_function_params:
            dynamic = dynamic.with_parameters(**custom_function_params)
        model = self.workspace.get_model(model_path)
        if workflow == _Workflow.CLASS_BASED:
            experiment_definition = SimpleModelicaExperimentDefinition(model, dynamic)
        else:
            fmu = model.compile(compiler_options=dynamic.get_compiler_options()).wait()
            experiment_definition = SimpleFMUExperimentDefinition(fmu, dynamic)
        if modifiers is None:
            modifiers = {"PI.yMax": Range(12, 13, 2)}
        experiment_definition = experiment_definition.with_modifiers(modifiers)
        exp = self.workspace.create_experiment(experiment_definition, user_data)
        return exp
