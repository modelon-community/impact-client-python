from unittest.mock import MagicMock

import pytest

import modelon.impact.client.exceptions as exceptions
import modelon.impact.client.sal.exceptions as sal_exceptions
from modelon.impact.client import Client, ProjectType, StorageLocation
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.entities.project import Project
from modelon.impact.client.entities.workspace import Workspace, WorkspaceDefinition
from modelon.impact.client.operations.experiment import ExperimentOperation
from modelon.impact.client.operations.model_executable import ModelExecutableOperation
from tests.files.paths import get_archived_project_path, get_archived_workspace_path
from tests.impact.client.helpers import (
    ClientHelper,
    IDs,
    create_case_reference,
    create_experiment_reference,
    create_workspace_conversion_operation,
    get_test_workspace_definition,
)


class TestClient:
    @pytest.mark.vcr()
    def test_create_workspace(self, client_helper: ClientHelper):
        workspace = client_helper.client.create_workspace(IDs.WORKSPACE_ID_SECONDARY)
        assert workspace.id == IDs.WORKSPACE_ID_SECONDARY

    @pytest.mark.vcr()
    def test_get_workspace(self, client_helper: ClientHelper):
        workspace_id = client_helper.workspace.id
        workspace = client_helper.client.get_workspace(workspace_id)
        assert workspace.id == IDs.WORKSPACE_ID_PRIMARY

    @pytest.mark.vcr()
    def test_get_workspace_by_name(self, client_helper: ClientHelper):
        workspaces = client_helper.client.get_workspace_by_name(
            IDs.WORKSPACE_ID_PRIMARY
        )
        assert len(workspaces) == 1
        assert workspaces[0].id == IDs.WORKSPACE_ID_PRIMARY

    @pytest.mark.vcr()
    def test_get_workspaces(self, client_helper: ClientHelper):
        client = client_helper.client
        client.create_workspace(IDs.WORKSPACE_ID_SECONDARY)
        workspace_ids = [workspace.id for workspace in client.get_workspaces()]
        assert IDs.WORKSPACE_ID_PRIMARY in workspace_ids
        assert IDs.WORKSPACE_ID_SECONDARY in workspace_ids

    @pytest.mark.vcr()
    def test_get_workspace_filtered_by_name(self, client_helper: ClientHelper):
        client = client_helper.client
        client.create_workspace(IDs.WORKSPACE_ID_SECONDARY)
        workspaces = client.get_workspaces(name=IDs.WORKSPACE_ID_PRIMARY)
        assert len(workspaces) == 1
        assert workspaces[0].name == IDs.WORKSPACE_ID_PRIMARY

    def test_semantic_version_error(self, semantic_version_error):
        with pytest.raises(exceptions.UnsupportedSemanticVersionError) as excinfo:
            Client(
                url=semantic_version_error.url, context=semantic_version_error.context
            )
        assert (
            "Version '1.0.0' of the HTTP REST API is not supported, must be in the "
            "range '>=4.21.1,<5.0.0'! Updgrade or downgrade this package to a "
            "version that supports version '1.0.0' of the HTTP REST API."
            in str(excinfo.value)
        )

    def test_no_assigned_license_error(self, user_with_no_license):
        with pytest.raises(exceptions.NoAssignedLicenseError):
            Client(url=user_with_no_license.url, context=user_with_no_license.context)

    def test_get_project_matchings(
        self,
        get_project_matchings,
        get_versioned_projects,
        get_versioned_new_project_trunk,
        get_versioned_new_project_branch,
    ):
        client = Client(
            url=get_project_matchings.url, context=get_project_matchings.context
        )
        definition = WorkspaceDefinition(get_test_workspace_definition())
        project_matching_entries = client.get_project_matchings(definition).entries
        assert len(project_matching_entries) == 1
        assert project_matching_entries[0].entry_id == IDs.VERSIONED_PROJECT_REFERENCE
        url = "https://github.com/project/test"
        expected_vcs_uri = (
            f"git+{url}.git@main:da6abb188a089527df1b54b27ace84274b819e4a"
        )
        assert project_matching_entries[0].vcs_uri == expected_vcs_uri
        assert len(project_matching_entries[0].projects) == 2
        assert (
            project_matching_entries[0].projects[0].id == IDs.VERSIONED_PROJECT_PRIMARY
        )
        assert (
            project_matching_entries[0].projects[1].id
            == IDs.VERSIONED_PROJECT_SECONDARY
        )

    @pytest.mark.vcr()
    def test_import_workspace_from_zip(self, tmpdir, client_helper: ClientHelper):
        archieve_ws_path = get_archived_workspace_path(tmpdir)
        imported_workspace = client_helper.client.import_workspace_from_zip(
            archieve_ws_path
        ).wait()
        assert isinstance(imported_workspace, Workspace)
        assert imported_workspace.name == IDs.WORKSPACE_ID_SECONDARY

    @pytest.mark.vcr()
    def test_upload_workspace(self, tmpdir, client_helper: ClientHelper):
        archieve_ws_path = get_archived_workspace_path(tmpdir)
        uploaded_workspace = client_helper.client.upload_workspace(archieve_ws_path)
        assert isinstance(uploaded_workspace, Workspace)
        assert uploaded_workspace.name == IDs.WORKSPACE_ID_SECONDARY

    def test_import_workspace_from_shared_definition(
        self,
        import_workspace,
        get_successful_workspace_upload_status,
        single_workspace,
    ):
        client = Client(
            url=import_workspace.url,
            context=import_workspace.context,
        )
        definition = WorkspaceDefinition(get_test_workspace_definition())
        imported_workspace = client.import_workspace_from_shared_definition(
            definition
        ).wait()
        assert isinstance(imported_workspace, Workspace)

    def test_failed_import_from_shared_definition(
        self, import_workspace, get_failed_workspace_upload_status
    ):
        client = Client(
            url=import_workspace.url,
            context=import_workspace.context,
        )
        definition = WorkspaceDefinition(get_test_workspace_definition())
        with pytest.raises(exceptions.IllegalWorkspaceImport):
            client.import_workspace_from_shared_definition(definition).wait()

    def test_workspace_conversion(self, setup_workspace_conversion):
        client = Client(
            url=setup_workspace_conversion.url,
            context=setup_workspace_conversion.context,
        )

        conversioin_op = client.convert_workspace(IDs.CONVERSION_ID, "backup")
        assert conversioin_op == create_workspace_conversion_operation(
            IDs.CONVERSION_ID
        )

    @pytest.mark.vcr()
    def test_import_project_from_zip(self, tmpdir, client_helper: ClientHelper):
        archieve_prj_path = get_archived_project_path(tmpdir)
        imported_project = client_helper.client.import_project_from_zip(
            archieve_prj_path
        ).wait()
        assert isinstance(imported_project, Project)
        assert imported_project.name == IDs.PROJECT_NAME_PRIMARY
        prjs = client_helper.client.get_projects(
            project_type=ProjectType.LOCAL, storage_location=StorageLocation.USERSPACE
        )
        prj_ids = [prj.id for prj in prjs]
        assert prjs[0].id in prj_ids

    @pytest.mark.vcr()
    def test_get_system_projects(self, client_helper: ClientHelper):
        prjs = client_helper.client.get_projects(
            project_type=ProjectType.SYSTEM, storage_location=StorageLocation.SYSTEM
        )
        assert len(prjs) == 2
        assert prjs[0].name == "Modelica"
        assert prjs[1].name == "Modelica"

    @pytest.mark.vcr()
    def test_get_project(self, client_helper: ClientHelper):
        default_project_id = client_helper.workspace.get_default_project().id
        prj = client_helper.client.get_project(default_project_id)
        assert prj.id == default_project_id
        assert prj.name == IDs.DEFAULT_PROJECT_NAME

    @pytest.mark.vcr()
    def test_get_executions(self, client_helper: ClientHelper):
        client_helper.create_and_execute_experiment(wait_for_completion=False)
        client_helper.compile_fmu(wait_for_completion=False)
        executions = client_helper.client.get_executions()
        operations = list(executions)
        assert len(operations) == 2
        assert isinstance(operations[0], ExperimentOperation)
        assert isinstance(operations[1], ModelExecutableOperation)

        # Cleanup
        for operation in operations:
            operation.wait()

    @pytest.mark.vcr()
    def test_get_executions_for_workspace(self, client_helper: ClientHelper):
        client_helper.create_and_execute_experiment(wait_for_completion=False)
        executions = client_helper.client.get_executions(
            workspace_id=IDs.WORKSPACE_ID_PRIMARY
        )
        operations = list(executions)
        assert len(operations) == 1
        assert isinstance(operations[0], ExperimentOperation)

        # Cleanup
        for operation in operations:
            operation.wait()

        executions = client_helper.client.get_executions(
            workspace_id=IDs.WORKSPACE_ID_SECONDARY
        )
        operations = list(executions)
        assert len(operations) == 0

    @pytest.mark.vcr()
    def test_get_me(self, client_helper: ClientHelper):
        user = client_helper.client.get_me()
        assert user.tenant.id == IDs.TENANT_ID
        assert user.tenant.group_name == IDs.GROUP_NAME
        assert len(user.roles) == 8
        assert user.username == IDs.USERNAME
        assert IDs.PRO_LICENSE_ROLE in user.roles
        assert user.license == IDs.PRO_LICENSE_ROLE
        assert user.firstname is None
        assert user.last_name is None
        assert user.email == IDs.MOCK_EMAIL

    @pytest.mark.experimental
    @pytest.mark.vcr()
    def test_get_case_by_reference(self, client_helper: ClientHelper):
        case_ref = create_case_reference(
            workspace_id=IDs.WORKSPACE_ID_PRIMARY,
            case_id=IDs.CASE_ID_PRIMARY,
            exp_id=IDs.EXPERIMENT_ID_PRIMARY,
        )
        case = client_helper.client.get_case_by_reference(case_ref)
        assert isinstance(case, Case)

    @pytest.mark.experimental
    @pytest.mark.vcr()
    def test_get_experiment_by_reference(self, client_helper: ClientHelper):
        experiment_ref = create_experiment_reference(
            workspace_id=IDs.WORKSPACE_ID_PRIMARY, exp_id=IDs.EXPERIMENT_ID_PRIMARY
        )
        experiment = client_helper.client.get_experiment_by_reference(experiment_ref)
        assert isinstance(experiment, Experiment)


def assert_key_validate_called(*, adapter, key):
    login_call = adapter.request_history[1]
    assert "http://mock-impact.com/api/users/me" == login_call.url
    assert "GET" == login_call.method
    assert key == login_call.headers["impact-api-key"]


def test_validate_api_key_from_credential_manager(user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = "test_from_credential_manager_key"
    Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
    )

    assert_key_validate_called(
        adapter=user_with_license.adapter,
        key="test_from_credential_manager_key",
    )


def test_api_key_missing(user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = None
    pytest.raises(
        exceptions.AuthenticationError,
        Client,
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
    )


def test_api_key_set_interactive_saves_key(user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = "test_api_key_set_interactive_saves_key"

    Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.write_key_to_file.assert_called_with(
        "test_api_key_set_interactive_saves_key"
    )


def test_api_key_validation_fail_interactive_dont_save_key(key_validation_fails):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = "test_api_key_validation_fails"
    cred_manager.get_key_from_prompt.return_value = (
        "test_api_key_validation_still_fails"
    )

    pytest.raises(
        sal_exceptions.HTTPError,
        Client,
        url=key_validation_fails.url,
        context=key_validation_fails.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.write_key_to_file.assert_not_called()


def test_client_login_fail_lets_user_enter_new_key(key_validation_fails):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = "test_client_key_validation_fails"
    cred_manager.get_key_from_prompt.return_value = "test_client_login_still_fails"

    pytest.raises(
        sal_exceptions.HTTPError,
        Client,
        url=key_validation_fails.url,
        context=key_validation_fails.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.get_key_from_prompt.assert_called()
