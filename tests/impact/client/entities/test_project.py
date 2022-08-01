from tests.impact.client.fixtures import *
from tests.impact.client.helpers import (
    create_project_content_entity,
    create_project_entity,
)
from modelon.impact.client import ContentType
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH


class TestProject:
    def test_get_project_contents(self, project):
        contents = project.entity.get_contents()
        assert contents == [
            create_project_content_entity(
                project_id="bf1e2f2a2fd55dcfd844bc1f252528f707254425",
                project_service=project.service,
            )
        ]

    def test_get_project_contents(self, project):
        project_service = project.service
        content = create_project_content_entity(
            project_id="bf1e2f2a2fd55dcfd844bc1f252528f707254425",
            project_service=project.service,
        )
        content.delete()
        project_service.project_content_delete.assert_called_with(
            "bf1e2f2a2fd55dcfd844bc1f252528f707254425",
            "81ac23172d7a479db85126691e090b34",
        )

    def test_delete_project(self, project):
        project_service = project.service
        project = create_project_entity(
            project_id="bf1e2f2a2fd55dcfd844bc1f252528f707254425",
            project_service=project_service,
        )
        project.delete()
        project_service.project_delete.assert_called_with(
            "bf1e2f2a2fd55dcfd844bc1f252528f707254425"
        )

    def test_upload_project_content(self, project):
        content = project.entity.upload_content(
            SINGLE_FILE_LIBRARY_PATH, content_type=ContentType.MODELICA
        )
        assert content == create_project_content_entity(
            project_id="bf1e2f2a2fd55dcfd844bc1f252528f707254425",
            content={
                "id": "f727f04210b94a0fac81f17f83b869e6",
                "relpath": "test.mo",
                "contentType": "MODELICA",
                "name": "test",
                "defaultDisabled": False,
            },
            project_service=project.service,
        )

    def test_upload_modelica_library(self, project):
        content = project.entity.upload_modelica_library(SINGLE_FILE_LIBRARY_PATH)
        assert content == create_project_content_entity(
            project_id="bf1e2f2a2fd55dcfd844bc1f252528f707254425",
            content={
                "id": "f727f04210b94a0fac81f17f83b869e6",
                "relpath": "test.mo",
                "contentType": "MODELICA",
                "name": "test",
                "defaultDisabled": False,
            },
            project_service=project.service,
        )

