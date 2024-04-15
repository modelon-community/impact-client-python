from pathlib import Path

import pytest

from modelon.impact.client import ContentType
from modelon.impact.client.operations.base import AsyncOperationStatus
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from tests.impact.client.helpers import ClientHelper, IDs


class TestProject:
    @pytest.mark.vcr()
    def test_get_project_size(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        assert project.size == 5308.0

    @pytest.mark.vcr()
    def test_get_project_options(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        dynamic = client_helper.workspace.get_custom_function("dynamic")
        options = project.get_options(dynamic)
        assert options.to_dict() == {
            "compiler": {
                "c_compiler": "gcc",
                "generate_html_diagnostics": False,
                "include_protected_variables": False,
            },
            "runtime": {},
            "simulation": {"dynamic_diagnostics": False, "ncp": 500},
            "solver": {},
            "customFunction": IDs.DYNAMIC_CF,
        }

    @pytest.mark.vcr()
    def test_get_project_default_options(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        dynamic = client_helper.workspace.get_custom_function("dynamic")
        options = project.get_options(dynamic, use_defaults=True)
        assert options.to_dict() == {
            "compiler": {
                "c_compiler": "gcc",
                "generate_html_diagnostics": False,
                "include_protected_variables": False,
            },
            "runtime": {},
            "solver": {},
            "simulation": {"dynamic_diagnostics": False, "ncp": 500},
            "customFunction": IDs.DYNAMIC_CF,
        }

    @pytest.mark.vcr()
    def test_get_project_contents(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        contents = project.get_contents()
        assert len(contents) == 6
        assert contents[0].id
        assert contents[0].relpath == Path("Resources/Views")
        assert contents[0].content_type == ContentType.VIEWS
        assert not contents[0].name
        assert not contents[0].default_disabled

    @pytest.mark.vcr()
    def test_get_project_content_by_id(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        contents = project.get_contents()
        content = project.get_content(contents[0].id)
        assert content.id
        assert content.relpath == Path("Resources/Views")
        assert content.content_type == ContentType.VIEWS
        assert not content.name
        assert not content.default_disabled

    @pytest.mark.vcr()
    def test_get_project_content_by_name(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        content = project.import_modelica_library(SINGLE_FILE_LIBRARY_PATH).wait()
        assert content.name == "Single"

        content = project.get_content_by_name("Single")
        assert content.id
        assert content.relpath == Path("Single.mo")
        assert content.content_type == ContentType.MODELICA
        assert content.name == "Single"
        assert not content.default_disabled

    @pytest.mark.vcr()
    def test_get_modelica_library_by_name(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        content = project.import_modelica_library(SINGLE_FILE_LIBRARY_PATH).wait()
        assert content.name == "Single"

        content = project.get_modelica_library_by_name("Single")
        assert content.id
        assert content.relpath == Path("Single.mo")
        assert content.content_type == ContentType.MODELICA
        assert content.name == "Single"
        assert not content.default_disabled

    @pytest.mark.vcr()
    def test_delete_project_contents(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        content = project.import_modelica_library(SINGLE_FILE_LIBRARY_PATH).wait()
        assert content.name == "Single"

        content.delete()

        assert project.get_content_by_name(content.name) is None

    @pytest.mark.vcr()
    def test_delete_project(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        assert client_helper.workspace.definition.default_project_id

        project.delete()

        assert not client_helper.workspace.definition.default_project_id

    @pytest.mark.vcr()
    def test_import_content(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        content_operation = project.import_content(
            SINGLE_FILE_LIBRARY_PATH, content_type=ContentType.MODELICA
        )
        assert content_operation.status == AsyncOperationStatus.READY
        content = content_operation.data()

        assert content.id
        assert content.relpath == Path("Single.mo")
        assert content.content_type == ContentType.MODELICA
        assert content.name == "Single"
        assert not content.default_disabled

    @pytest.mark.vcr()
    def test_import_modelica_library(self, client_helper: ClientHelper):
        project = client_helper.workspace.get_default_project()
        content_operation = project.import_modelica_library(SINGLE_FILE_LIBRARY_PATH)
        assert content_operation.status == AsyncOperationStatus.READY

        content = content_operation.data()
        assert content.id
        assert content.relpath == Path("Single.mo")
        assert content.content_type == ContentType.MODELICA
        assert content.name == "Single"
        assert not content.default_disabled
