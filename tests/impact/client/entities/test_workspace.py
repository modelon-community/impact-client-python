import os
import tempfile
import unittest.mock as mock

import pytest

from modelon.impact.client import AccessSettings
from tests.files.paths import TEST_WORKSPACE_PATH
from tests.impact.client.helpers import (
    IDs,
    create_experiment_operation,
    create_model_entity,
    create_model_exe_entity,
    create_project_entity,
    create_published_workspace_entity,
    create_workspace_entity,
    create_workspace_export_operation,
    get_test_workspace_definition,
)


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
    def test_revoke_published_workspace_access(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.revoke_access(IDs.USERNAME)
        service.workspace.revoke_published_workspace_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.USERNAME
        )

    @pytest.mark.experimental
    def test_grant_published_workspace_access(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_PRIMARY, service=service
        )
        workspace.grant_user_access(IDs.USERNAME)
        service.workspace.grant_published_workspace_access.assert_called_with(
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
        assert pub_ws_acl.role_permissions == []
        assert len(pub_ws_acl.group_permissions) == 1
        assert pub_ws_acl.group_permissions[0].id == IDs.PUBLISH_PERMISSIONS_PRIMARY_ID
        assert (
            pub_ws_acl.group_permissions[0].name == IDs.PUBLISH_PERMISSIONS_PRIMARY_NAME
        )


class TestWorkspace:
    def test_get_workspace_size(self, workspace):
        assert workspace.entity.size == 7014

    def test_rename_workspace(self, workspace):
        assert workspace.entity.name == IDs.WORKSPACE_PRIMARY
        workspace.entity.rename(IDs.WORKSPACE_SECONDARY)
        data = {
            "definition": get_test_workspace_definition(IDs.WORKSPACE_SECONDARY),
            "id": IDs.WORKSPACE_PRIMARY,
            "sizeInfo": {"total": 7014},
        }
        workspace.service.workspace.update_workspace.assert_called_with(
            IDs.WORKSPACE_PRIMARY, data
        )

    def test_get_custom_function(self, workspace):
        custom_function = workspace.entity.get_custom_function(IDs.DYNAMIC_CF)
        assert IDs.DYNAMIC_CF == custom_function.name

    def test_get_custom_functions(self, workspace):
        custom_function_list = [
            custom_function.name
            for custom_function in workspace.entity.get_custom_functions()
        ]
        assert [IDs.DYNAMIC_CF] == custom_function_list

    def test_delete(self):
        service = mock.MagicMock()
        workspace = create_workspace_entity(IDs.WORKSPACE_PRIMARY, service=service)
        workspace.delete()
        service.workspace.workspace_delete.assert_called_with(IDs.WORKSPACE_PRIMARY)

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

    def test_download_workspace(self, workspace):
        t = os.path.join(tempfile.gettempdir(), workspace.entity.id + '.zip')
        resp = workspace.entity.download(tempfile.gettempdir())
        assert resp == t

    def test_export_workspace(self, workspace):
        resp = workspace.entity.export()
        assert resp == create_workspace_export_operation(IDs.EXPORT)

    def test_publish_workspace_without_group_share(self, workspace):
        workspace_entity = workspace.entity
        service = workspace.service
        workspace_service = service.workspace
        workspace_entity.export(publish=True, access=AccessSettings(group_names=[]))
        access_settings = {'groupNames': []}
        workspace_service.workspace_export_setup.assert_has_calls(
            [mock.call(IDs.WORKSPACE_PRIMARY, True, None, access_settings)]
        )

    def test_publish_workspace(self, workspace):
        workspace_entity = workspace.entity
        service = workspace.service
        workspace_service = service.workspace
        workspace_entity.export(publish=True)
        workspace_service.workspace_export_setup.assert_has_calls(
            [mock.call(IDs.WORKSPACE_PRIMARY, True, None, None)]
        )

    def test_get_model(self, workspace):
        model = workspace.entity.get_model("Modelica.Blocks.PID")
        assert model == create_model_entity(
            "Modelica.Blocks.PID", workspace.entity.id, IDs.PROJECT_PRIMARY
        )

    def test_model_repr(self, workspace):
        model = create_model_entity(
            "Modelica.Blocks.PID", workspace.entity.id, IDs.PROJECT_PRIMARY
        )
        assert "Class name 'Modelica.Blocks.PID'" == model.__repr__()

    def test_get_fmus(self, workspace):
        fmus = workspace.entity.get_fmus()
        assert len(fmus) == 2
        assert fmus[0].id == IDs.FMU_PRIMARY
        assert fmus[1].id == IDs.FMU_SECONDARY

    def test_get_fmu(self, workspace):
        fmu = workspace.entity.get_fmu(IDs.FMU_PRIMARY)
        assert fmu == create_model_exe_entity(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)

    def test_get_experiment(self, workspace):
        exp = workspace.entity.get_experiment(IDs.EXPERIMENT_PRIMARY)
        assert exp.id == IDs.EXPERIMENT_PRIMARY

    def test_get_experiments(self, workspace):
        exps = workspace.entity.get_experiments()
        assert len(exps) == 2
        assert exps[0].id == IDs.EXPERIMENT_PRIMARY
        assert exps[1].id == IDs.EXPERIMENT_SECONDARY

    def test_create_experiment(self, workspace):
        exp = workspace.entity.create_experiment({})
        assert exp.id == IDs.EXPERIMENT_PRIMARY

    def test_create_experiment_with_user_data(self, workspace):
        workspace_entity = workspace.entity
        service = workspace.service
        workspace_service = service.workspace
        user_data = {"customWsGetKey": "customWsGetValue"}
        workspace_entity.create_experiment({}, user_data)

        workspace_service.experiment_create.assert_has_calls(
            [mock.call(IDs.WORKSPACE_PRIMARY, {}, user_data)]
        )

    def test_execute_options_dict(self, workspace):
        exp = workspace.entity.execute({})
        assert exp == create_experiment_operation(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )

    def test_get_default_project(self, workspace):
        project = workspace.entity.get_default_project()
        assert project.id == IDs.PROJECT_PRIMARY

    def test_get_projects(self, workspace):
        projects = workspace.entity.get_projects()
        assert projects == [
            create_project_entity(
                project_id=IDs.PROJECT_PRIMARY, project_name="NewProject"
            )
        ]

    def test_get_all_dependencies(self, workspace):
        dependencies = workspace.entity.get_dependencies()
        assert len(dependencies) == 2
        assert dependencies[0].id == IDs.MSL_300_PROJECT_ID
        assert dependencies[1].id == IDs.MSL_400_PROJECT_ID

    def test_create_project(self, workspace):
        project = workspace.entity.create_project("my_project")
        assert project.id == IDs.PROJECT_PRIMARY

    def test_import_dependency_from_zip(self, workspace):
        project = workspace.entity.import_dependency_from_zip(
            TEST_WORKSPACE_PATH
        ).wait()
        assert project.id == IDs.PROJECT_PRIMARY

    def test_import_project_from_zip(self, workspace):
        project = workspace.entity.import_project_from_zip(TEST_WORKSPACE_PATH).wait()
        assert project.id == IDs.PROJECT_PRIMARY

    def test_get_model_experiments(self, workspace):
        experiments = workspace.entity.get_experiments(IDs.MODELICA_CLASS_PATH)
        assert len(experiments) == 2
        assert experiments[0].id == IDs.EXPERIMENT_PRIMARY
        assert experiments[1].id == IDs.EXPERIMENT_SECONDARY
