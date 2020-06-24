import collections

import pytest
import requests
import requests_mock

import modelon.impact.client.sal.service
import modelon.impact.client.sal.exceptions


MockedServer = collections.namedtuple('MockedServer', ['url', 'context', 'adapter'])


class MockContex:
    def __init__(self, session):
        self.session = session


@pytest.fixture
def mock_server_base():
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount('http://', adapter)
    mock_url = 'http://mock-impact.com'

    return MockedServer(mock_url, MockContex(session), adapter)


@pytest.fixture
def get_ok_empty_json(mock_server_base):
    json = {}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', mock_server_base.url, json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def get_with_error(mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', mock_server_base.url, json=json, headers=json_header, status_code=401,
    )

    return mock_server_base


def test_get(get_ok_empty_json):
    service = modelon.impact.client.sal.service.Service(
        uri=get_ok_empty_json.url, context=get_ok_empty_json.context
    )
    resp = service.get('/')
    assert resp.data == {}


def test_get_error(get_with_error):
    service = modelon.impact.client.sal.service.Service(
        uri=get_with_error.url, context=get_with_error.context
    )
    pytest.raises(modelon.impact.client.sal.exceptions.HTTPError, service.get, '/')


def test_get_error_no_check(get_with_error):
    service = modelon.impact.client.sal.service.Service(
        uri=get_with_error.url, context=get_with_error.context
    )
    resp = service.get('/', check_return=False)
    with pytest.raises(modelon.impact.client.sal.exceptions.HTTPError):
        resp.data

    assert resp.error.code == 123
    assert resp.error.message == 'no authroization'
