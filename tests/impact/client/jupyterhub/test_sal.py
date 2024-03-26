import pytest

import modelon.impact.client.jupyterhub.exceptions as exceptions
from modelon.impact.client.jupyterhub.sal import JupyterContext, JupyterHubService
from modelon.impact.client.sal.uri import URI


def test_given_no_jupyter_error_when_get_user(get_user_ok):
    uri = URI(get_user_ok.url)
    context = JupyterContext(get_user_ok.context)
    context.token = "secret-token"

    user = JupyterHubService.get_user_data(uri, context)

    expected_impact_user_uri = uri / "user/user-name/impact"
    assert user.server_running() is True
    assert user.impact_server_uri(uri).resolve() == expected_impact_user_uri.resolve()


def test_given_jupyter_auth_error_when_get_user(get_user_auth_error):
    uri = URI(get_user_auth_error.url)
    context = JupyterContext(get_user_auth_error.context)
    context.token = "secret-token"

    pytest.raises(
        exceptions.JupyterHubAuthrizationError,
        JupyterHubService.get_user_data,
        uri,
        context,
    )


def test_given_jupyter_no_such_resource_error_when_get_user(
    get_user_no_such_resource_error,
):
    uri = URI(get_user_no_such_resource_error.url)
    context = JupyterContext(get_user_no_such_resource_error.context)
    context.token = "secret-token"

    pytest.raises(
        exceptions.NotAJupyterHubUrl, JupyterHubService.get_user_data, uri, context
    )


def test_given_jupyter_unknown_error_when_get_user(get_user_unknown_error):
    uri = URI(get_user_unknown_error.url)
    context = JupyterContext(get_user_unknown_error.context)
    context.token = "secret-token"

    pytest.raises(
        exceptions.UnknownJupyterHubError, JupyterHubService.get_user_data, uri, context
    )


def test_given_jupyter_response_misses_fields_when_get_user(
    get_user_response_missing_fields,
):
    uri = URI(get_user_response_missing_fields.url)
    context = JupyterContext(get_user_response_missing_fields.context)
    context.token = "secret-token"

    pytest.raises(
        exceptions.NotAJupyterHubUrl, JupyterHubService.get_user_data, uri, context
    )


def test_given_jupyter_response_not_json_when_get_user(token_response_not_json):
    uri = URI(token_response_not_json.url)
    context = JupyterContext(token_response_not_json.context)
    context.token = "secret-token"

    pytest.raises(
        exceptions.NotAJupyterHubUrl, JupyterHubService.get_user_data, uri, context
    )


def test_given_jupyter_no_response_when_get_user(token_no_response_exception):
    uri = URI(token_no_response_exception.url)
    context = JupyterContext(token_no_response_exception.context)
    context.token = "secret-token"

    pytest.raises(
        exceptions.NotAJupyterHubUrl, JupyterHubService.get_user_data, uri, context
    )
