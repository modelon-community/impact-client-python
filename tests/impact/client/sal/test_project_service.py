from modelon.impact.client.sal.uri import URI
import modelon.impact.client.sal.service
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from tests.impact.client.fixtures import *


class TestProjectService:
    def test_delete_project(self, delete_project):
        uri = URI(delete_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_project.context
        )
        service.project.project_delete('0ecf178e8b7d4a8b9c5d605e966e9096')
        assert delete_project.adapter.called
        delete_call = delete_project.adapter.request_history[0]
        assert (
            'http://mock-impact.com/api/projects/0ecf178e8b7d4a8b9c5d605e966e9096'
            == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_get_project(self, single_project):
        uri = URI(single_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_project.context
        )
        data = service.project.project_get('0ecf178e8b7d4a8b9c5d605e966e9096')
        assert data == {
            "id": "bf1e2f2a2fd55dcfd844bc1f252528f707254425",
            "definition": {
                "name": "NewProject",
                "format": "1.0",
                "dependencies": [{"name": "MSL", "versionSpecifier": "4.0.0"}],
                "content": [
                    {
                        "id": "81ac23172d7a479db85126691e090b34",
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
        data = service.project.projects_get()
        assert data == {
            "data": {
                "items": [
                    {
                        "id": "bf1e2f2a2fd55dcfd844bc1f252528f707254425",
                        "definition": {
                            "name": "NewProject",
                            "format": "1.0",
                            "dependencies": [
                                {"name": "MSL", "versionSpecifier": "4.0.0"}
                            ],
                            "content": [
                                {
                                    "id": "81ac23172d7a479db85126691e090b34",
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
            '0ecf178e8b7d4a8b9c5d605e966e9096',
            'dfdd9d2175e59ba02e2e188703cfb30b949abc71',
        )
        assert delete_project_content.adapter.called
        delete_call = delete_project_content.adapter.request_history[0]
        assert (
            'http://mock-impact.com/api/projects/0ecf178e8b7d4a8b9c5d605e966e9096/content/dfdd9d2175e59ba02e2e188703cfb30b949abc71'
            == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_project_content_upload(self, upload_project_content):
        uri = URI(upload_project_content.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_project_content.context
        )
        data = service.project.project_content_upload(
            SINGLE_FILE_LIBRARY_PATH, "f727f04210b94a0fac81f17f83b869e6", "MODELICA",
        )
        assert data == {
            "id": "f727f04210b94a0fac81f17f83b869e6",
            "relpath": "test.mo",
            "contentType": "MODELICA",
            "name": "test",
            "defaultDisabled": False,
        }
