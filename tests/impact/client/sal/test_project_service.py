import unittest.mock as mock

import modelon.impact.client.sal.service
from modelon.impact.client import ProjectType
from modelon.impact.client.sal.uri import URI
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH, TEST_WORKSPACE_PATH
from tests.impact.client.helpers import UNVERSIONED_PROJECT, IDs


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
        data = service.project.project_get(
            IDs.PROJECT_PRIMARY, vcs_info=False, size_info=False
        )
        assert data == UNVERSIONED_PROJECT

    def test_get_projects_with_filter(self, filtered_projects):
        uri = URI(filtered_projects.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=filtered_projects.context
        )
        service.project.projects_get(vcs_info=False, project_type=ProjectType.LOCAL)
        assert filtered_projects.adapter.called
        fetch_call = filtered_projects.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/projects?vcsInfo=False&type=LOCAL'
            == fetch_call.url
        )
        assert 'GET' == fetch_call.method

    def test_get_projects(self, multiple_projects):
        uri = URI(multiple_projects.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_projects.context
        )
        data = service.project.projects_get(vcs_info=False)
        assert data == {"data": {"items": [UNVERSIONED_PROJECT]}}

    def test_delete_project_content(self, delete_project_content):
        uri = URI(delete_project_content.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_project_content.context
        )
        service.project.project_content_delete(
            IDs.PROJECT_PRIMARY,
            IDs.PROJECT_CONTENT_PRIMARY,
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
            IDs.PROJECT_PRIMARY,
            IDs.PROJECT_CONTENT_SECONDARY,
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
            SINGLE_FILE_LIBRARY_PATH,
            IDs.PROJECT_PRIMARY,
            "MODELICA",
        )
        assert 'data' in data

    def test_fmu_upload(self, import_fmu):
        uri = URI(import_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_fmu.context
        )
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            data = service.project.fmu_import(
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
            f'http://mock-impact.com/api/projects/{IDs.PROJECT_PRIMARY}'
            f'/content/{IDs.PROJECT_CONTENT_PRIMARY}/fmu-imports' == import_fmu_call.url
        )
        assert 'POST' == import_fmu_call.method

    def test_get_project_options(self, project_options_get):
        uri = URI(project_options_get.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=project_options_get.context
        )
        data = service.project.project_options_get(
            IDs.PROJECT_PRIMARY, IDs.WORKSPACE_PRIMARY, IDs.DYNAMIC_CF
        )
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
            IDs.WORKSPACE_PRIMARY, IDs.DYNAMIC_CF
        )
        assert data == {'compiler': {'c_compiler': 'gcc'}}

    def test_project_import_from_zip(self, import_project):
        uri = URI(import_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_project.context
        )
        data = service.project.import_from_zip(TEST_WORKSPACE_PATH)
        assert data == {"data": {"location": f"api/project-imports/{IDs.IMPORT}"}}
