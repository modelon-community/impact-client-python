import unittest.mock as mock
from modelon.impact.client.sal.uri import URI
import modelon.impact.client.sal.service
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH, TEST_WORKSPACE_PATH
from tests.impact.client.fixtures import *


class TestWorkspaceService:
    def test_create_workspace(self, create_workspace):
        uri = URI(create_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace.context
        )
        data = service.workspace.workspace_create('newWorkspace')
        assert data == {
            'definition': TEST_WORKSPACE_DEFINITION,
            'id': 'newWorkspace',
        }

    def test_delete_workspace(self, delete_workspace):
        uri = URI(delete_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_workspace.context
        )
        service.workspace.workspace_delete('AwesomeWorkspace')
        assert delete_workspace.adapter.called
        delete_call = delete_workspace.adapter.request_history[0]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace' == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_get_workspace(self, single_workspace):
        uri = URI(single_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_workspace.context
        )
        data = service.workspace.workspace_get('AwesomeWorkspace')
        assert data == {
            "definition": TEST_WORKSPACE_DEFINITION,
            "id": "AwesomeWorkspace",
        }

    def test_get_workspaces(self, multiple_workspace):
        uri = URI(multiple_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_workspace.context
        )
        data = service.workspace.workspaces_get()
        workspace_1_def = TEST_WORKSPACE_DEFINITION.copy()
        workspace_1_def["name"] = 'workspace_1'
        workspace_2_def = TEST_WORKSPACE_DEFINITION.copy()
        workspace_2_def["name"] = 'workspace_2'
        assert data == {
            'data': {
                'items': [
                    {'id': 'workspace_1', 'definition': workspace_1_def},
                    {'id': 'workspace_2', 'definition': workspace_2_def},
                ]
            }
        }

    def test_library_import(self, import_lib):
        uri = URI(import_lib.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_lib.context
        )
        service.workspace.library_import('AwesomeWorkspace', SINGLE_FILE_LIBRARY_PATH)
        assert import_lib.adapter.called
        import_call = import_lib.adapter.request_history[0]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/libraries'
            == import_call.url
        )
        assert 'POST' == import_call.method

    def test_workspace_upload(self, upload_workspace):
        uri = URI(upload_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_workspace.context
        )
        data = service.workspace.workspace_upload(TEST_WORKSPACE_PATH)
        assert data == {'id': 'newWorkspace'}

    def test_result_upload(self, upload_result):
        uri = URI(upload_result.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result.context
        )
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            data = service.workspace.result_upload("AwesomeWorkspace", "test.mat")
            mock_file.assert_called_with("test.mat", "rb")

        assert data == {
            "data": {
                "id": "2f036b9fab6f45c788cc466da327cc78workspace",
                "status": "running",
            }
        }

    def test_result_upload_status(self, upload_result_status_ready):
        uri = URI(upload_result_status_ready.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result_status_ready.context
        )
        data = service.workspace.get_result_upload_status(
            "2f036b9fab6f45c788cc466da327cc78workspace"
        )

        assert data == {
            "data": {
                "id": "2f036b9fab6f45c788cc466da327cc78workspace",
                "status": "ready",
                "data": {
                    "resourceUri": "api/external-result/2f036b9fab6f45c788cc466da327cc78workspace"
                },
            }
        }

    def test_result_upload_meta(self, upload_result_meta):
        uri = URI(upload_result_meta.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result_meta.context
        )
        data = service.workspace.get_uploaded_result_meta(
            "2f036b9fab6f45c788cc466da327cc78workspace"
        )

        assert data == {
            "data": {
                "id": "2f036b9fab6f45c788cc466da327cc78workspace",
                "createdAt": "2021-09-02T08:26:49.612000",
                "name": "result_for_PID",
                "description": "This is a result file for PID controller",
                "workspaceId": "workspace",
            }
        }

    def test_delete_result_upload(self, upload_result_delete):
        uri = URI(upload_result_delete.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result_delete.context
        )
        service.workspace.delete_uploaded_result(
            "2f036b9fab6f45c788cc466da327cc78workspace"
        )
        assert upload_result_delete.adapter.called

    def test_fmu_upload(self, import_fmu):
        uri = URI(import_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_fmu.context
        )
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            data = service.workspace.fmu_import(
                "AwesomeWorkspace", "test.fmu", "Workspace"
            )
            mock_file.assert_called_with("test.fmu", "rb")

        assert data == {
            "fmuClassPath": "Workspace.PID_Controller.Model",
            "importWarnings": [
                "Specified argument for 'top_level_inputs=['a']' does not match any variable"
            ],
            "library": {"id": "Workspace", "uses": {}, "name": "Workspace"},
        }

        import_fmu_call = import_fmu.adapter.request_history[0]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/libraries/Workspace/models'
            == import_fmu_call.url
        )
        assert 'POST' == import_fmu_call.method

    def test_workspace_download(self, download_workspace):
        uri = URI(download_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=download_workspace.context
        )
        data = service.workspace.workspace_download("Workspace", '0d96b08c8d')
        assert data == b'\x00\x00\x00\x00'

    # TODO: Cloning workspace is not implemented on feature branch
    # def test_clone_workspace(self, clone_workspace):
    #     uri = URI(clone_workspace.url)
    #     service = modelon.impact.client.sal.service.Service(
    #         uri=uri, context=clone_workspace.context
    #     )
    #     data = service.workspace.workspace_clone("Workspace")
    #     assert data == {'workspace_id': 'clone_44e8ad8c036'}

    def test_get_fmu(self, get_fmu):
        uri = URI(get_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_fmu.context
        )
        data = service.workspace.fmu_get("WS", "pid_20090615_134")
        assert data == {'id': 'pid_20090615_134'}

    def test_get_fmus(self, get_all_fmu):
        uri = URI(get_all_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_fmu.context
        )
        data = service.workspace.fmus_get("WS")
        assert data == {'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9f-3df5'}]}}

    def test_fmu_download(self, download_fmu):
        uri = URI(download_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=download_fmu.context
        )
        data = service.workspace.fmu_download("WS", 'pid_20090615_134')
        assert data == b'\x00\x00\x00\x00'

    def test_get_experiment(self, get_experiment):
        uri = URI(get_experiment.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_experiment.context
        )
        data = service.workspace.experiment_get("WS", 'pid_20090615_134')
        assert data == {'id': 'pid_20090615_134'}

    def test_get_experiments(self, get_all_experiments):
        uri = URI(get_all_experiments.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_experiments.context
        )
        data = service.workspace.experiments_get("WS")
        assert data == {'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9f-3df5'}]}}

    def test_create_experiment(self, experiment_create):
        uri = URI(experiment_create.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_create.context
        )
        data = service.workspace.experiment_create("WS", {})
        assert experiment_create.adapter.called
        assert data == {"experiment_id": "pid_2009"}

        user_data = {"value": 42}
        data = service.workspace.experiment_create("WS", {}, user_data)
        request_data = experiment_create.adapter.request_history[1].json()
        assert request_data == {'userData': user_data}

    def test_get_projects(self, get_projects):
        uri = URI(get_projects.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_projects.context
        )
        data = service.workspace.projects_get("WS")
        assert data == {
            "data": {
                "items": [
                    {
                        "id": "659573e31fcd7e6809a00171f734c13497acdf7f",
                        "definition": {},
                        "projectType": "LOCAL",
                    }
                ]
            }
        }

    def test_create_project(self, create_project):
        uri = URI(create_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_project.context
        )
        data = service.workspace.project_create("WS", "my_project")
        assert data == {
            "id": "2d45026ab0733e7dc4eca0510369144e46caf1f6",
            "definition": {
                "name": "my_project",
                "format": "1.0",
                "dependencies": [],
                "content": [],
                "executionOptions": [],
            },
            "projectType": "LOCAL",
        }

    def test_get_dependencies(self, get_dependencies):
        uri = URI(get_dependencies.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_dependencies.context
        )
        data = service.workspace.dependencies_get("WS")
        assert data == {
            "data": {
                "items": [
                    {
                        "id": "84fb1c37abe6ed97a53972fb7239630e1212438b",
                        "definition": {},
                        "projectType": "SYSTEM",
                    },
                ]
            }
        }
