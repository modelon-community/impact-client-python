import pytest
from unittest.mock import MagicMock
from modelon.impact.client import Client
from modelon.impact.client.entities.workspace import Workspace, WorkspaceDefinition
from modelon.impact.client.entities.project import Project
import modelon.impact.client.exceptions as exceptions
import modelon.impact.client.sal.exceptions as sal_exceptions
from tests.files.paths import TEST_WORKSPACE_PATH

from tests.impact.client.helpers import (
    create_workspace_conversion_operation,
    create_workspace_entity,
    IDs,
    get_test_workspace_definition,
)


def test_create_workspace(create_workspace):
    client = Client(url=create_workspace.url, context=create_workspace.context)
    workspace = client.create_workspace(IDs.WORKSPACE_PRIMARY)
    assert workspace == create_workspace_entity(IDs.WORKSPACE_PRIMARY)
    assert workspace.id == IDs.WORKSPACE_PRIMARY


def test_get_workspace(single_workspace):
    client = Client(url=single_workspace.url, context=single_workspace.context)
    workspace = client.get_workspace(IDs.WORKSPACE_PRIMARY)
    assert workspace.id == IDs.WORKSPACE_PRIMARY


def test_get_workspaces(multiple_workspace):
    client = Client(url=multiple_workspace.url, context=multiple_workspace.context)
    workspaces = client.get_workspaces()
    assert len(workspaces) == 2
    assert workspaces[0].id == IDs.WORKSPACE_PRIMARY
    assert workspaces[1].id == IDs.WORKSPACE_SECONDARY


def test_get_workspaces_error(workspaces_error):
    client = Client(url=workspaces_error.url, context=workspaces_error.context)
    pytest.raises(sal_exceptions.HTTPError, client.get_workspaces)


def test_create_workspace_error(create_workspace_error):
    client = Client(
        url=create_workspace_error.url, context=create_workspace_error.context
    )
    pytest.raises(sal_exceptions.HTTPError, client.create_workspace, ':^-')


def test_semantic_version_error(semantic_version_error):
    with pytest.raises(exceptions.UnsupportedSemanticVersionError) as excinfo:
        Client(url=semantic_version_error.url, context=semantic_version_error.context)
    assert (
        "Version '1.0.0' of the HTTP REST API is not supported, must be in the "
        "range '>=4.0.0-beta.25,<5.0.0'! Updgrade or downgrade this package to a "
        "version that supports version '1.0.0' of the HTTP REST API."
        in str(excinfo.value)
    )


def assert_login_called(*, adapter, body):
    login_call = adapter.request_history[2]
    assert 'http://mock-impact.com/api/login' == login_call.url
    assert 'POST' == login_call.method
    assert body == login_call.json()


def test_client_login_api_key_from_credential_manager(user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = 'test_from_credential_manager_key'
    Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
    )

    assert_login_called(
        adapter=user_with_license.adapter,
        body={"secretKey": "test_from_credential_manager_key"},
    )


def test_client_login_api_key_missing(user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = None
    Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
    )

    assert_login_called(
        adapter=user_with_license.adapter,
        body={},
    )


def test_client_login_interactive_saves_key(user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = 'test_client_login_interactive_saves_key'

    Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.write_key_to_file.assert_called_with(
        'test_client_login_interactive_saves_key'
    )


def test_client_login_fail_interactive_dont_save_key(login_fails, user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = 'test_client_login_fails'
    cred_manager.get_key_from_prompt.return_value = 'test_client_login_still_fails'

    pytest.raises(
        sal_exceptions.HTTPError,
        Client,
        url=login_fails.url,
        context=login_fails.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.write_key_to_file.assert_not_called()


def test_client_login_fail_lets_user_enter_new_key(sem_ver_check, login_fails):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = 'test_client_login_fails'
    cred_manager.get_key_from_prompt.return_value = 'test_client_login_still_fails'

    pytest.raises(
        sal_exceptions.HTTPError,
        Client,
        url=login_fails.url,
        context=login_fails.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.get_key_from_prompt.assert_called()


def test_empty_api_key_when_login_then_anon_login_and_dont_save_key(user_with_license):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = ''
    Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    assert_login_called(adapter=user_with_license.adapter, body={})
    cred_manager.write_key_to_file.assert_not_called()


def test_client_connect_against_jupyterhub_can_authorize(jupyterhub_api):
    cred_manager = MagicMock()
    cred_manager.get_key.return_value = None
    jupyterhub_cred_manager = MagicMock()
    jupyterhub_cred_manager.get_key.return_value = 'secret-token'

    Client(
        url=jupyterhub_api.url,
        context=jupyterhub_api.context,
        credential_manager=cred_manager,
        interactive=True,
        jupyterhub_credential_manager=jupyterhub_cred_manager,
    )
    jupyterhub_cred_manager.write_key_to_file.assert_called_with('secret-token')


def test_no_assigned_license_error(user_with_no_license):
    with pytest.raises(exceptions.NoAssignedLicenseError):
        Client(url=user_with_no_license.url, context=user_with_no_license.context)


def test_get_project_matchings(
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
    expected_vcs_uri = f"git+{url}.git@main:da6abb188a089527df1b54b27ace84274b819e4a"
    assert project_matching_entries[0].vcs_uri == expected_vcs_uri
    assert len(project_matching_entries[0].projects) == 2
    assert project_matching_entries[0].projects[0].id == IDs.VERSIONED_PROJECT_PRIMARY
    assert project_matching_entries[0].projects[1].id == IDs.VERSIONED_PROJECT_SECONDARY


def test_import_workspace_from_zip(
    import_workspace,
    get_successful_workspace_upload_status,
    single_workspace,
):
    client = Client(
        url=import_workspace.url,
        context=import_workspace.context,
    )
    imported_workspace = client.import_workspace_from_zip(TEST_WORKSPACE_PATH).wait()
    assert isinstance(imported_workspace, Workspace)


def test_import_workspace_from_shared_definition(
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
    import_workspace, get_failed_workspace_upload_status
):
    client = Client(
        url=import_workspace.url,
        context=import_workspace.context,
    )
    definition = WorkspaceDefinition(get_test_workspace_definition())
    with pytest.raises(exceptions.IllegalWorkspaceImport):
        client.import_workspace_from_shared_definition(definition).wait()


def test_workspace_conversion(setup_workspace_conversion):
    client = Client(
        url=setup_workspace_conversion.url, context=setup_workspace_conversion.context
    )

    conversioin_op = client.convert_workspace(IDs.CONVERSION, 'backup')
    assert conversioin_op == create_workspace_conversion_operation(IDs.CONVERSION)


def test_import_project_from_zip(
    import_project,
    get_project_upload_status,
    single_project,
):
    client = Client(
        url=import_project.url,
        context=import_project.context,
    )
    imported_project = client.import_project_from_zip(TEST_WORKSPACE_PATH).wait()
    assert isinstance(imported_project, Project)
