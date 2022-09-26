import pytest
import requests.exceptions


from tests.impact.client.helpers import (
    with_json_route,
    with_text_route,
    with_exception,
)


@pytest.fixture
def get_user_ok(mock_server_base):
    jupyter_user_json = {'name': 'user-name', 'server': 'ok'}

    return with_json_route(
        mock_server_base,
        'GET',
        'hub/api/authorizations/token/secret-token',
        jupyter_user_json,
    )


@pytest.fixture
def get_user_auth_error(mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        'hub/api/authorizations/token/secret-token',
        {},
        status_code=403,
    )


@pytest.fixture
def get_user_no_such_resource_error(mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        'hub/api/authorizations/token/secret-token',
        {},
        status_code=404,
    )


@pytest.fixture
def get_user_unknown_error(mock_server_base):
    return with_json_route(
        mock_server_base,
        'GET',
        'hub/api/authorizations/token/secret-token',
        {},
        status_code=500,
    )


@pytest.fixture
def get_user_response_missing_fields(mock_server_base):
    return with_json_route(
        mock_server_base, 'GET', 'hub/api/authorizations/token/secret-token', {},
    )


@pytest.fixture
def token_response_not_json(mock_server_base):
    return with_text_route(
        mock_server_base,
        'GET',
        'hub/api/authorizations/token/secret-token',
        'not JSON',
    )


@pytest.fixture
def token_no_response_exception(mock_server_base):
    return with_exception(
        mock_server_base,
        'GET',
        'hub/api/authorizations/token/secret-token',
        requests.exceptions.RequestException,
    )
