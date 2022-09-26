import unittest.mock as mock
from modelon.impact.client.sal.uri import URI
import modelon.impact.client.sal.service
from tests.impact.client.helpers import IDs
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH


class TestProjectService:
    def test_delete_project(self, delete_project):
        uri = URI(delete_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_project.context
        )
        service.project.project_delete(IDs.PROJECT_PRIMARY)
        assert delete_project.adapter.called
        delete_call = delete_project.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/projects/{IDs.PROJECT_PRIMARY}'
            == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_get_project(self, single_project):
        uri = URI(single_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_project.context
        )
        data = service.project.project_get(IDs.PROJECT_PRIMARY, vcs_info=False)
        assert data == {
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

    def test_get_projects(self, multiple_projects):
        uri = URI(multiple_projects.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_projects.context
        )
        data = service.project.projects_get(vcs_info=False)
        assert data == {
            "data": {
                "items": [
                    {
                        "id": IDs.PROJECT_PRIMARY,
                        "definition": {
                            "name": "NewProject",
                            "format": "1.0",
                            "dependencies": [
                                {"name": "MSL", "versionSpecifier": "4.0.0"}
                            ],
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

    def test_delete_project_content(self, delete_project_content):
        uri = URI(delete_project_content.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_project_content.context
        )
        service.project.project_content_delete(
            IDs.PROJECT_PRIMARY, IDs.PROJECT_CONTENT_PRIMARY,
        )
        assert delete_project_content.adapter.called
        delete_call = delete_project_content.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/projects/{IDs.PROJECT_PRIMARY}/content/{IDs.PROJECT_CONTENT_PRIMARY}'
            == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_get_project_content(self, get_project_content):
        uri = URI(get_project_content.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_project_content.context
        )
        data = service.project.project_content_get(
            IDs.PROJECT_PRIMARY, IDs.PROJECT_CONTENT_SECONDARY,
        )
        assert data == {
            "id": IDs.PROJECT_CONTENT_SECONDARY,
            "relpath": "test.mo",
            "contentType": "MODELICA",
            "name": "test",
            "defaultDisabled": False,
        }

    def test_project_content_upload(self, upload_project_content):
        uri = URI(upload_project_content.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_project_content.context
        )
        data = service.project.project_content_upload(
            SINGLE_FILE_LIBRARY_PATH, IDs.PROJECT_PRIMARY, "MODELICA",
        )
        assert 'data' in data

    def test_fmu_upload(self, import_fmu):
        uri = URI(import_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_fmu.context
        )
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            data = service.project.fmu_upload(
                IDs.WORKSPACE_PRIMARY,
                IDs.PROJECT_PRIMARY,
                IDs.PROJECT_CONTENT_PRIMARY,
                "test.fmu",
                "Workspace",
            )
            mock_file.assert_called_with("test.fmu", "rb")

        assert data == {
            "fmuClassPath": "Workspace.PID_Controller.Model",
            "importWarnings": [
                "Specified argument for 'top_level_inputs=['a']' does not match any variable"
            ],
            "library": {
                'project_id': IDs.PROJECT_PRIMARY,
                'content_id': IDs.PROJECT_CONTENT_PRIMARY,
            },
        }

        import_fmu_call = import_fmu.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}/projects/{IDs.PROJECT_PRIMARY}/content/{IDs.PROJECT_CONTENT_PRIMARY}/models'
            == import_fmu_call.url
        )
        assert 'POST' == import_fmu_call.method

    def test_get_project_options(self, project_options_get):
        uri = URI(project_options_get.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=project_options_get.context
        )
        data = service.project.project_options_get(IDs.PROJECT_PRIMARY, 'dynamic')
        assert data == {
            "compiler": {
                "c_compiler": "gcc",
                "generate_html_diagnostics": False,
                "include_protected_variables": False,
            },
            "runtime": {"log_level": 2},
            "simulation": {'dynamic_diagnostics': False, 'ncp': 500},
            "solver": {"rtol": 1e-5},
        }

    def test_get_default_project_options(self, project_default_options_get):
        uri = URI(project_default_options_get.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=project_default_options_get.context
        )
        data = service.project.project_default_options_get(
            IDs.PROJECT_PRIMARY, 'dynamic'
        )
        assert data == {'compiler': {'c_compiler': 'gcc'}}
