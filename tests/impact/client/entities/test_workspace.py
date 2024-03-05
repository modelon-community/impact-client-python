import os
import tempfile
import unittest.mock as mock

import pytest

from modelon.impact.client import AccessSettings, SimpleModelicaExperimentDefinition
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.entities.model import Model
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.operations.workspace.exports import WorkspaceExportOperation
from tests.files.paths import TEST_WORKSPACE_PATH
from tests.impact.client.helpers import (
    ClientHelper,
    IDs,
    create_published_workspace_entity,
    create_workspace_entity,
)
import modelon.impact.client.sal.exceptions as sal_exceptions

class TestPublishedWorkspace:
    def test_delete_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.delete()
        service.workspace.delete_published_workspace.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    @pytest.mark.experimental
    def test_revoke_user_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.revoke_user_access(IDs.USERNAME)
        service.workspace.revoke_user_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.USERNAME
        )

    @pytest.mark.experimental
    def test_grant_user_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.grant_user_access(IDs.USERNAME)
        service.workspace.grant_user_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.USERNAME
        )

    @pytest.mark.experimental
    def test_grant_community_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.grant_community_access()
        service.workspace.grant_community_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    @pytest.mark.experimental
    def test_revoke_community_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.revoke_community_access()
        service.workspace.revoke_community_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    @pytest.mark.experimental
    def test_grant_group_acess_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.grant_group_access()
        service.workspace.grant_group_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, None
        )
        workspace.grant_group_access(IDs.GROUP_NAME)
        service.workspace.grant_group_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.GROUP_NAME
        )

    @pytest.mark.experimental
    def test_revoke_group_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.revoke_group_access(IDs.GROUP_NAME)
        service.workspace.revoke_group_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.GROUP_NAME
        )

    def test_rename_published_workspace(self, publish_workspace):
        workspace = publish_workspace.entity
        service = publish_workspace.service

        new_workspace_name = IDs.WORKSPACE_SECONDARY
        assert workspace.name == IDs.WORKSPACE_PRIMARY
        workspace.name = new_workspace_name

        service.workspace.rename_published_workspace.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, new_workspace_name
        )
        service.workspace.get_published_workspace.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    def test_import_published_workspace(self, publish_workspace):
        workspace = publish_workspace.entity.import_to_userspace()
        assert workspace.id == IDs.WORKSPACE_PRIMARY

    @pytest.mark.experimental
    def test_get_published_workspace_acl(self, publish_workspace):
        pub_ws_acl = publish_workspace.entity.get_access_control_list()
        assert len(pub_ws_acl.shared_with) == 1
        assert pub_ws_acl.shared_with[0].username == IDs.USERNAME
        assert pub_ws_acl.shared_with[0].id == IDs.USER_ID
        assert pub_ws_acl.requested_by == []
        assert pub_ws_acl.role_names == []
        assert len(pub_ws_acl.group_names) == 1
        assert pub_ws_acl.group_names[0] == IDs.GROUP_NAME


class TestWorkspace:
    @pytest.mark.vcr()
    def test_get_workspace_size(self, client_helper: ClientHelper):
        assert client_helper.workspace.id == IDs.WORKSPACE_PRIMARY
        assert isinstance(client_helper.workspace.size, int)

    @pytest.mark.vcr()
    def test_rename_workspace(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        assert workspace.name == IDs.WORKSPACE_PRIMARY
        workspace.rename(IDs.WORKSPACE_SECONDARY)
        workspace = client_helper.client.get_workspace(IDs.WORKSPACE_PRIMARY)
        assert workspace.name == IDs.WORKSPACE_SECONDARY

    @pytest.mark.vcr()
    def test_get_custom_function(self, client_helper: ClientHelper):
        custom_function = client_helper.workspace.get_custom_function(IDs.DYNAMIC_CF)
        assert IDs.DYNAMIC_CF == custom_function.name

    @pytest.mark.vcr()
    def test_get_custom_functions(self, client_helper: ClientHelper):
        custom_function_list = [
            custom_function.name
            for custom_function in client_helper.workspace.get_custom_functions()
        ]
        assert IDs.DYNAMIC_CF in custom_function_list

    @pytest.mark.vcr()
    def test_delete(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        workspace.delete()
        with pytest.raises(sal_exceptions.HTTPError) as err:
            client_helper.client.get_workspace(workspace.id)
        assert str(err.value) == f"The workspace '{workspace.id}' does not exist"

    def test_upload_result(self, external_result_sal_upload):
        external_result_service = external_result_sal_upload.external_result
        workspace = create_workspace_entity(
            IDs.WORKSPACE_PRIMARY, service=external_result_sal_upload
        )
        upload_op = workspace.upload_result("test.mat", "Workspace")
        external_result_service.result_upload.assert_called_with(
            IDs.WORKSPACE_PRIMARY, 'test.mat', description=None, label='Workspace'
        )
        assert upload_op.id == IDs.IMPORT

    @pytest.mark.vcr()
    def test_download_workspace(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        temp_dir = tempfile.gettempdir()
        resp = workspace.download(temp_dir)
        download_path = os.path.join(temp_dir, workspace.id + '.zip')
        assert resp == download_path

    @pytest.mark.vcr()
    def test_export_workspace(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        ops = workspace.export()
        assert isinstance(ops, WorkspaceExportOperation)
        temp_dir = tempfile.gettempdir()
        download_path = os.path.join(temp_dir, workspace.id + '.zip')
        path = ops.wait().download_as(download_path)
        assert path == download_path

    def test_publish_workspace_without_group_share(self, workspace):
        workspace_entity = workspace.entity
        service = workspace.service
        workspace_service = service.workspace
        workspace_entity.export(publish=True, access=AccessSettings(group_names=[]))
        access_settings = {'groupNames': []}
        workspace_service.workspace_export_setup.assert_has_calls(
            [mock.call(IDs.WORKSPACE_PRIMARY, True, None, access_settings)]
        )

    @pytest.mark.vcr()
    def test_publish_workspace(self, client_helper: ClientHelper):
        pwc = client_helper.client.get_published_workspaces_client()
        pub_ws_id = client_helper.workspace.export(publish=True).wait().id
        pw = pwc.get_by_id(pub_ws_id)
        assert pw
        assert pw.name == client_helper.workspace.name

    @pytest.mark.vcr()
    def test_get_model(self, client_helper: ClientHelper):
        model_name = IDs.MODELICA_CLASS_PATH
        model = client_helper.workspace.get_model(model_name)
        assert isinstance(model, Model)
        assert model.name == model_name

    @pytest.mark.vcr()
    def test_model_repr(self, client_helper: ClientHelper):
        model_name = IDs.MODELICA_CLASS_PATH
        model = client_helper.workspace.get_model(model_name)
        assert f"Class name '{model_name}'" == model.__repr__()

    @pytest.mark.vcr()
    def test_get_fmus(self, client_helper: ClientHelper):
        client_helper.create_and_execute_experiment()
        fmus = client_helper.workspace.get_fmus()
        assert len(fmus) == 2

    @pytest.mark.vcr()
    def test_get_fmu(self, client_helper: ClientHelper):
        client_helper.create_and_execute_experiment(modifiers={})
        fmus = client_helper.workspace.get_fmus()
        assert len(fmus) == 1
        fmu = client_helper.workspace.get_fmu(fmus[0].id)
        assert isinstance(fmu, ModelExecutable)

    @pytest.mark.vcr()
    def test_get_experiment(self, client_helper: ClientHelper):
        exp = client_helper.create_experiment(modifiers={})
        exp = client_helper.workspace.get_experiment(exp.id)
        assert isinstance(exp, Experiment)

    @pytest.mark.vcr()
    def test_get_experiments(self, client_helper: ClientHelper):
        client_helper.create_experiment(modifiers={})
        client_helper.create_experiment(modifiers={})
        exps = client_helper.workspace.get_experiments()
        assert len(exps) == 2

    @pytest.mark.vcr()
    def test_create_experiment(self, client_helper: ClientHelper):
        exp = client_helper.create_experiment(modifiers={})
        assert isinstance(exp, Experiment)
        assert exp.id

    @pytest.mark.vcr()
    def test_create_experiment_with_user_data(self, client_helper: ClientHelper):
        expected_user_data = {"customWsGetKey": "customWsGetValue"}
        exp = client_helper.create_experiment(user_data=expected_user_data)
        user_data = exp.metadata.user_data
        assert user_data == expected_user_data

    @pytest.mark.vcr()
    def test_experiment_def_as_dict(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        dynamic = workspace.get_custom_function('dynamic')
        model = workspace.get_model(IDs.MODELICA_CLASS_PATH)
        experiment_definition = SimpleModelicaExperimentDefinition(
            model, dynamic
        ).to_dict()
        exp = workspace.execute(experiment_definition).wait()
        assert isinstance(exp, Experiment)

    @pytest.mark.vcr()
    def test_get_default_project(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        project = workspace.get_default_project()
        assert project.name == IDs.DEFAULT_PROJECT_NAME

    @pytest.mark.vcr()
    def test_get_projects(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        workspace.create_project(IDs.PROJECT_NAME_PRIMARY)
        projects = workspace.get_projects()
        assert len(projects) == 2

    @pytest.mark.vcr()
    def test_get_all_dependencies(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        dependencies = workspace.get_dependencies()
        assert len(dependencies) == 1
        assert dependencies[0].name == "Modelica"

    @pytest.mark.vcr()
    def test_create_project(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        project = workspace.create_project(IDs.PROJECT_NAME_PRIMARY)
        assert project.name == IDs.PROJECT_NAME_PRIMARY

    def test_import_dependency_from_zip(self, workspace):
        project = workspace.entity.import_dependency_from_zip(
            TEST_WORKSPACE_PATH
        ).wait()
        assert project.id == IDs.PROJECT_PRIMARY

    def test_import_project_from_zip(self, workspace):
        project = workspace.entity.import_project_from_zip(TEST_WORKSPACE_PATH).wait()
        assert project.id == IDs.PROJECT_PRIMARY

    @pytest.mark.vcr()
    def test_get_model_experiments(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        client_helper.create_experiment()
        experiments = workspace.get_experiments(IDs.MODELICA_CLASS_PATH)
        assert len(experiments) == 1
