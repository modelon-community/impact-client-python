import unittest.mock

import pytest

from modelon.impact.client.jupyterhub.authorize import authorize
from modelon.impact.client.jupyterhub.sal import JupyterUser
from modelon.impact.client.sal.service import URI
import modelon.impact.client.jupyterhub.exceptions as exceptions


TEST_URI = URI('https//:impact-mock.com')


def test_given_token_when_authorize_then_ok():
    cred_manager = unittest.mock.MagicMock()
    service = unittest.mock.MagicMock()
    context = unittest.mock.MagicMock()

    # Given
    interactive = False
    cred_manager.get_key.return_value = 'ok-secret'

    # When
    _, context = authorize(
        TEST_URI,
        interactive,
        context=context,
        credential_manager=cred_manager,
        service=service,
    )

    # Then
    assert context.token == 'ok-secret'
    cred_manager.write_key_to_file.assert_not_called()
    cred_manager.get_key.assert_called()


def test_given_token_interactive_when_authorize_then_save_token():
    cred_manager = unittest.mock.MagicMock()
    service = unittest.mock.MagicMock()
    context = unittest.mock.MagicMock()

    # Given
    interactive = True
    cred_manager.get_key.return_value = 'ok-secret'

    # When
    _, context = authorize(
        TEST_URI,
        interactive,
        context=context,
        credential_manager=cred_manager,
        service=service,
    )

    # Then
    assert context.token == 'ok-secret'
    cred_manager.write_key_to_file.assert_called_with('ok-secret')
    cred_manager.get_key.assert_called()


def test_given_no_token_when_authorize_then_no_token_error():
    cred_manager = unittest.mock.MagicMock()
    service = unittest.mock.MagicMock()
    context = unittest.mock.MagicMock()

    # Given
    interactive = False
    cred_manager.get_key.return_value = None

    # When
    pytest.raises(
        exceptions.NoJupyterHubTokenError,
        authorize,
        TEST_URI,
        interactive,
        context=context,
        credential_manager=cred_manager,
        service=service,
    )

    # Then
    cred_manager.write_key_to_file.assert_not_called()
    cred_manager.get_key.assert_called()


def test_given_wrong_token_when_authorize_then_error():
    cred_manager = unittest.mock.MagicMock()
    service = unittest.mock.MagicMock()
    context = unittest.mock.MagicMock()

    # Given
    interactive = False
    cred_manager.get_key.return_value = 'wrong-secret'
    service.get_user_data.side_effect = exceptions.JupyterHubAuthrizationError('oh no')

    # When
    pytest.raises(
        exceptions.JupyterHubAuthrizationError,
        authorize,
        TEST_URI,
        interactive,
        context=context,
        credential_manager=cred_manager,
        service=service,
    )

    # Then
    cred_manager.write_key_to_file.assert_not_called()
    cred_manager.get_key_from_prompt.assert_not_called()


def test_given_wrong_token_and_interactive_when_authorize_then_prompt_for_key_and_write():
    cred_manager = unittest.mock.MagicMock()
    service = unittest.mock.MagicMock()
    context = unittest.mock.MagicMock()

    # Given
    interactive = True
    cred_manager.get_key.return_value = 'wrong-secret'
    cred_manager.get_key_from_prompt.return_value = 'ok-secret'
    service.get_user_data.side_effect = [
        exceptions.JupyterHubAuthrizationError('oh no'),
        unittest.mock.MagicMock(),
    ]

    # When
    _, context = authorize(
        TEST_URI,
        interactive,
        context=context,
        credential_manager=cred_manager,
        service=service,
    )

    # Then
    assert context.token == 'ok-secret'
    cred_manager.write_key_to_file.assert_called_with('ok-secret')
    cred_manager.get_key_from_prompt.assert_called()


def test_given_wrong_token_many_times_and_interactive_when_authorize_then_prompt_for_key_but_fail():
    cred_manager = unittest.mock.MagicMock()
    service = unittest.mock.MagicMock()
    context = unittest.mock.MagicMock()

    # Given
    interactive = True
    cred_manager.get_key.return_value = 'wrong-secret'
    cred_manager.get_key_from_prompt.return_value = 'wrong-secret'
    service.get_user_data.side_effect = exceptions.JupyterHubAuthrizationError('oh no')

    # When
    pytest.raises(
        exceptions.JupyterHubAuthrizationError,
        authorize,
        TEST_URI,
        interactive,
        context=context,
        credential_manager=cred_manager,
        service=service,
    )

    # Then
    cred_manager.write_key_to_file.assert_not_called()
    cred_manager.get_key_from_prompt.assert_called()


def test_given_user_has_no_server_when_authorize_then_error():
    cred_manager = unittest.mock.MagicMock()
    service = unittest.mock.MagicMock()
    context = unittest.mock.MagicMock()

    # Given
    service.get_user_data.return_value = JupyterUser('some-user', None)

    # When, then
    pytest.raises(
        exceptions.NoJupyterHubServerRunningError,
        authorize,
        TEST_URI,
        True,
        context=context,
        credential_manager=cred_manager,
        service=service,
    )
