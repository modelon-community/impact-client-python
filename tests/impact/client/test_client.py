import pytest
import unittest.mock
import modelon.impact.client
import modelon.impact.client.sal.exceptions
from tests.impact.client.fixtures import *


def test_create_workspace(create_workspace):
    client = modelon.impact.client.Client(
        url=create_workspace.url, context=create_workspace.context
    )
    workspace = client.create_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('newWorkspace')
    assert workspace.id == 'newWorkspace'


def test_get_workspace(single_workspace):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspace = client.get_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('AwesomeWorkspace')
    assert workspace.id == 'AwesomeWorkspace'


def test_get_workspaces(multiple_workspace):
    client = modelon.impact.client.Client(
        url=multiple_workspace.url, context=multiple_workspace.context
    )
    workspaces = client.get_workspaces()
    assert workspaces == [
        modelon.impact.client.entities.Workspace('AwesomeWorkspace'),
        modelon.impact.client.entities.Workspace('BoringWorkspace'),
    ]
    workspace_id = ['AwesomeWorkspace', 'BoringWorkspace']
    assert [workspace.id for workspace in workspaces] == workspace_id


def test_get_workspaces_error(workspaces_error):
    client = modelon.impact.client.Client(
        url=workspaces_error.url, context=workspaces_error.context
    )
    pytest.raises(modelon.impact.client.sal.exceptions.HTTPError, client.get_workspaces)


def test_create_workspace_error(create_workspace_error):
    client = modelon.impact.client.Client(
        url=create_workspace_error.url, context=create_workspace_error.context
    )
    pytest.raises(
        modelon.impact.client.sal.exceptions.HTTPError, client.create_workspace, ':^-'
    )


def test_semantic_version_error(semantic_version_error):
    with pytest.raises(
        modelon.impact.client.exceptions.UnsupportedSemanticVersionError
    ) as excinfo:
        modelon.impact.client.Client(
            url=semantic_version_error.url, context=semantic_version_error.context
        )
    assert (
        "Version '3.1.0' of the HTTP REST API is not supported, must be in the "
        "range '>=1.21.0,<3.0.0'! Updgrade or downgrade this package to a version"
        " that supports version '3.1.0' of the HTTP REST API." in str(excinfo.value)
    )


def assert_login_called(*, adapter, body):
    login_call = adapter.request_history[1]
    assert 'http://mock-impact.com/api/login' == login_call.url
    assert 'POST' == login_call.method
    assert body == login_call.json()


def test_client_login_api_key_from_credential_manager(user_with_license):
    cred_manager = unittest.mock.MagicMock()
    cred_manager.get_key.return_value = 'test_from_credential_manager_key'
    modelon.impact.client.Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
    )

    assert_login_called(
        adapter=user_with_license.adapter,
        body={"secretKey": "test_from_credential_manager_key"},
    )


def test_client_login_api_key_missing(user_with_license):
    cred_manager = unittest.mock.MagicMock()
    cred_manager.get_key.return_value = None
    modelon.impact.client.Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
    )

    assert_login_called(
        adapter=user_with_license.adapter, body={},
    )


def test_client_login_interactive_saves_key(user_with_license):
    cred_manager = unittest.mock.MagicMock()
    cred_manager.get_key.return_value = 'test_client_login_interactive_saves_key'

    modelon.impact.client.Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.write_key_to_file.assert_called_with(
        'test_client_login_interactive_saves_key'
    )


def test_client_login_fail_interactive_dont_save_key(login_fails, user_with_license):
    cred_manager = unittest.mock.MagicMock()
    cred_manager.get_key.return_value = 'test_client_login_fails'
    cred_manager.get_key_from_prompt.return_value = 'test_client_login_still_fails'

    pytest.raises(
        modelon.impact.client.sal.exceptions.HTTPError,
        modelon.impact.client.Client,
        url=login_fails.url,
        context=login_fails.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.write_key_to_file.assert_not_called()


def test_client_login_fail_lets_user_enter_new_key(sem_ver_check, login_fails):
    cred_manager = unittest.mock.MagicMock()
    cred_manager.get_key.return_value = 'test_client_login_fails'
    cred_manager.get_key_from_prompt.return_value = 'test_client_login_still_fails'

    pytest.raises(
        modelon.impact.client.sal.exceptions.HTTPError,
        modelon.impact.client.Client,
        url=login_fails.url,
        context=login_fails.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    cred_manager.get_key_from_prompt.assert_called()


def test_empty_api_key_when_login_then_anon_login_and_dont_save_key(user_with_license):
    cred_manager = unittest.mock.MagicMock()
    cred_manager.get_key.return_value = ''
    modelon.impact.client.Client(
        url=user_with_license.url,
        context=user_with_license.context,
        credential_manager=cred_manager,
        interactive=True,
    )

    assert_login_called(adapter=user_with_license.adapter, body={})
    cred_manager.write_key_to_file.assert_not_called()


def test_client_connect_against_jupyterhub_can_authorize(jupyterhub_api):
    cred_manager = unittest.mock.MagicMock()
    cred_manager.get_key.return_value = None
    jupyterhub_cred_manager = unittest.mock.MagicMock()
    jupyterhub_cred_manager.get_key.return_value = 'secret-token'

    client = modelon.impact.client.Client(
        url=jupyterhub_api.url,
        context=jupyterhub_api.context,
        credential_manager=cred_manager,
        interactive=True,
        jupyterhub_credential_manager=jupyterhub_cred_manager,
    )
    jupyterhub_cred_manager.write_key_to_file.assert_called_with('secret-token')


def test_no_assigned_license_error(user_with_no_license):
    with pytest.raises(modelon.impact.client.exceptions.NoAssignedLicenseError):
        modelon.impact.client.Client(
            url=user_with_no_license.url, context=user_with_no_license.context
        )
