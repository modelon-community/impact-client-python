from pathlib import Path
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
from modelon.impact.client.entities.project import ProjectContent

from tests.impact.client.helpers import (
    create_project_content_entity,
    create_project_entity,
    create_workspace_entity,
    IDs,
)
from modelon.impact.client import ContentType
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from modelon.impact.client.operations.base import AsyncOperationStatus


class TestProject:
    def test_get_project_options(self, project, custom_function):
        options = project.entity.get_options(custom_function)
        assert options.to_dict() == {
            "compiler": {
                "c_compiler": "gcc",
                "generate_html_diagnostics": False,
                "include_protected_variables": False,
            },
            "runtime": {"log_level": 2},
            "simulation": {'dynamic_diagnostics': False, 'ncp': 500},
            "solver": {"rtol": 1e-5},
            'customFunction': IDs.DYNAMIC_CF,
        }

    def test_get_project_default_options(self, project, custom_function):
        options = project.entity.get_options(custom_function, use_defaults=True)
        assert options.to_dict() == {
            'compiler': {'c_compiler': 'gcc'},
            'customFunction': IDs.DYNAMIC_CF,
        }

    def test_get_project_contents(self, project):
        contents = project.entity.get_contents()
        assert len(contents) == 1
        assert contents[0].id == IDs.PROJECT_CONTENT_PRIMARY
        assert contents[0].relpath == Path('MyPackage')
        assert contents[0].content_type == ContentType.MODELICA
        assert contents[0].name == 'MyPackage'
        assert not contents[0].default_disabled

    def test_get_project_content_by_name(self, project):
        content = project.entity.get_content_by_name('MyPackage', ContentType.MODELICA)
        assert content.id == IDs.PROJECT_CONTENT_PRIMARY
        assert content.relpath == Path('MyPackage')
        assert content.content_type == ContentType.MODELICA
        assert content.name == 'MyPackage'
        assert not content.default_disabled

    def test_get_modelica_library_by_name(self, project):
        content = project.entity.get_modelica_library_by_name('MyPackage')
        assert content.id == IDs.PROJECT_CONTENT_PRIMARY
        assert content.relpath == Path('MyPackage')
        assert content.content_type == ContentType.MODELICA
        assert content.name == 'MyPackage'
        assert not content.default_disabled

    def test_delete_project_contents(self, project):
        service = project.service
        content = create_project_content_entity(
            project_id=IDs.PROJECT_PRIMARY,
            service=project.service,
        )
        content.delete()
        service.project.project_content_delete.assert_called_with(
            IDs.PROJECT_PRIMARY,
            IDs.PROJECT_CONTENT_PRIMARY,
        )

    def test_delete_project(self, project):
        service = project.service
        project = create_project_entity(
            project_id=IDs.PROJECT_PRIMARY,
            service=service,
        )
        project.delete()
        service.project.project_delete.assert_called_with(IDs.PROJECT_PRIMARY)

    def test_upload_project_content(self, project):
        content_operation = project.entity.upload_content(
            SINGLE_FILE_LIBRARY_PATH, content_type=ContentType.MODELICA
        )
        assert content_operation.status() == AsyncOperationStatus.READY
        content = content_operation.data()

        assert content.id == IDs.PROJECT_CONTENT_SECONDARY
        assert content.relpath == Path('test.mo')
        assert content.content_type == ContentType.MODELICA
        assert content.name == 'test'
        assert not content.default_disabled

    def test_upload_modelica_library(self, project):
        content_operation = project.entity.upload_modelica_library(
            SINGLE_FILE_LIBRARY_PATH
        )
        assert content_operation.status() == AsyncOperationStatus.READY

        content = content_operation.data()
        assert content.id == IDs.PROJECT_CONTENT_SECONDARY
        assert content.relpath == Path('test.mo')
        assert content.content_type == ContentType.MODELICA
        assert content.name == 'test'
        assert not content.default_disabled

    def test_upload_fmu(self, project):
        project_entity = project.entity
        project_service = project.service
        content: ProjectContent = project_entity.get_content_by_name('MyPackage')
        test_workspace = create_workspace_entity(IDs.WORKSPACE_PRIMARY)
        content.upload_fmu(test_workspace, "test.fmu", "Workspace")
        project_service.project.fmu_upload.assert_called_with(
            IDs.WORKSPACE_PRIMARY,
            IDs.PROJECT_PRIMARY,
            IDs.PROJECT_CONTENT_PRIMARY,
            'test.fmu',
            'Workspace',
            False,
            None,
            None,
            None,
            step_size=0.0,
        )
