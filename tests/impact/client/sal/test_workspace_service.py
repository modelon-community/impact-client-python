import unittest.mock as mock
from modelon.impact.client.sal.uri import URI
import modelon.impact.client.sal.service
from tests.impact.client.helpers import IDs, get_test_workspace_definition
from tests.files.paths import TEST_WORKSPACE_PATH
from tests.impact.client.fixtures import *


class TestWorkspaceService:
    def test_create_workspace(self, create_workspace):
        uri = URI(create_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace.context
        )
        data = service.workspace.workspace_create(IDs.WORKSPACE_PRIMARY)
        assert data == {
            'definition': get_test_workspace_definition(),
            'id': IDs.WORKSPACE_PRIMARY,
        }

    def test_delete_workspace(self, delete_workspace):
        uri = URI(delete_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_workspace.context
        )
        service.workspace.workspace_delete(IDs.WORKSPACE_PRIMARY)
        assert delete_workspace.adapter.called
        delete_call = delete_workspace.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}'
            == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_get_workspace(self, single_workspace):
        uri = URI(single_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_workspace.context
        )
        data = service.workspace.workspace_get(IDs.WORKSPACE_PRIMARY)
        assert data == {
            "definition": get_test_workspace_definition(),
            "id": IDs.WORKSPACE_PRIMARY,
        }

    def test_get_workspaces(self, multiple_workspace):
        uri = URI(multiple_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_workspace.context
        )
        data = service.workspace.workspaces_get()
        workspace_1_def = get_test_workspace_definition(IDs.WORKSPACE_PRIMARY)
        workspace_2_def = get_test_workspace_definition(IDs.WORKSPACE_SECONDARY)
        assert data == {
            'data': {
                'items': [
                    {'id': IDs.WORKSPACE_PRIMARY, 'definition': workspace_1_def},
                    {'id': IDs.WORKSPACE_SECONDARY, 'definition': workspace_2_def},
                ]
            }
        }

    def test_workspace_upload(self, upload_workspace):
        uri = URI(upload_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_workspace.context
        )
        data = service.workspace.workspace_upload(TEST_WORKSPACE_PATH)
        assert data == {'id': IDs.WORKSPACE_PRIMARY}

    def test_result_upload(self, upload_result):
        uri = URI(upload_result.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_result.context
        )
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            data = service.workspace.result_upload(IDs.WORKSPACE_PRIMARY, "test.mat")
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
                "workspaceId": IDs.WORKSPACE_PRIMARY,
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
                IDs.WORKSPACE_PRIMARY, "test.fmu", "Workspace"
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
            f'http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}/libraries/Workspace/models'
            == import_fmu_call.url
        )
        assert 'POST' == import_fmu_call.method

    def test_workspace_download(self, download_workspace):
        uri = URI(download_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=download_workspace.context
        )
        data = service.workspace.workspace_download(IDs.WORKSPACE_PRIMARY, '0d96b08c8d')
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
        data = service.workspace.fmu_get(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
        assert data == {'id': IDs.FMU_PRIMARY}

    def test_get_fmus(self, get_all_fmu):
        uri = URI(get_all_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_fmu.context
        )
        data = service.workspace.fmus_get(IDs.WORKSPACE_PRIMARY)
        assert data == {
            'data': {'items': [{'id': IDs.FMU_PRIMARY}, {'id': IDs.FMU_SECONDARY}]}
        }

    def test_fmu_download(self, download_fmu):
        uri = URI(download_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=download_fmu.context
        )
        data = service.workspace.fmu_download(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
        assert data == b'\x00\x00\x00\x00'

    def test_get_experiment(self, get_experiment):
        uri = URI(get_experiment.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_experiment.context
        )
        data = service.workspace.experiment_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        assert data == {'id': IDs.EXPERIMENT_PRIMARY}

    def test_get_experiments(self, get_all_experiments):
        uri = URI(get_all_experiments.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_experiments.context
        )
        data = service.workspace.experiments_get(IDs.WORKSPACE_PRIMARY)
        assert data == {
            'data': {
                'items': [
                    {'id': IDs.EXPERIMENT_PRIMARY},
                    {'id': IDs.EXPERIMENT_SECONDARY},
                ]
            }
        }

    def test_create_experiment(self, experiment_create):
        uri = URI(experiment_create.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_create.context
        )
        data = service.workspace.experiment_create(IDs.WORKSPACE_PRIMARY, {})
        assert experiment_create.adapter.called
        assert data == {"experiment_id": IDs.EXPERIMENT_PRIMARY}

        user_data = {"value": 42}
        data = service.workspace.experiment_create(IDs.WORKSPACE_PRIMARY, {}, user_data)
        request_data = experiment_create.adapter.request_history[1].json()
        assert request_data == {'userData': user_data}

    def test_get_projects(self, get_projects):
        uri = URI(get_projects.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_projects.context
        )
        data = service.workspace.projects_get(IDs.WORKSPACE_PRIMARY)
        assert data == {
            "data": {
                "items": [
                    {
                        "id": IDs.PROJECT_PRIMARY,
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
        data = service.workspace.project_create(IDs.WORKSPACE_PRIMARY, "my_project")
        assert data == {
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

    def test_get_dependencies(self, get_dependencies):
        uri = URI(get_dependencies.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_dependencies.context
        )
        data = service.workspace.dependencies_get(IDs.WORKSPACE_PRIMARY)
        assert data == {
            "data": {
                "items": [
                    {
                        "id": IDs.MSL_300_CONTENT_ID,
                        "definition": {},
                        "projectType": "SYSTEM",
                    },
                ]
            }
        }
