from tests.impact.client.fixtures import *
from tests.impact.client.helpers import (
    create_project_content_entity,
    create_project_entity,
    IDs,
)
from modelon.impact.client import ContentType
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH


class TestProject:
    def test_get_project_contents(self, project):
        contents = project.entity.get_contents()
        assert len(contents) == 1
        assert contents[0].id == IDs.PROJECT_CONTENT_PRIMARY
        assert contents[0].relpath == 'MyPackage'
        assert contents[0].content_type == ContentType.MODELICA
        assert contents[0].name == 'MyPackage'
        assert not contents[0].default_disabled

    def test_delete_project_contents(self, project):
        project_service = project.service
        content = create_project_content_entity(
            project_id=IDs.PROJECT_PRIMARY, project_service=project.service,
        )
        content.delete()
        project_service.project_content_delete.assert_called_with(
            IDs.PROJECT_PRIMARY, IDs.PROJECT_CONTENT_PRIMARY,
        )

    def test_delete_project(self, project):
        project_service = project.service
        project = create_project_entity(
            project_id=IDs.PROJECT_PRIMARY, project_service=project_service,
        )
        project.delete()
        project_service.project_delete.assert_called_with(IDs.PROJECT_PRIMARY)

    def test_upload_project_content(self, project):
        content = project.entity.upload_content(
            SINGLE_FILE_LIBRARY_PATH, content_type=ContentType.MODELICA
        )
        assert content.id == IDs.PROJECT_CONTENT_SECONDARY
        assert content.relpath == 'test.mo'
        assert content.content_type == ContentType.MODELICA
        assert content.name == 'test'
        assert not content.default_disabled

    def test_upload_modelica_library(self, project):
        content = project.entity.upload_modelica_library(SINGLE_FILE_LIBRARY_PATH)
        assert content.id == IDs.PROJECT_CONTENT_SECONDARY
        assert content.relpath == 'test.mo'
        assert content.content_type == ContentType.MODELICA
        assert content.name == 'test'
        assert not content.default_disabled
