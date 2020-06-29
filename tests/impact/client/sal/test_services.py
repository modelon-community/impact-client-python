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
def single_workspace(mock_server_base):
    json = {'data': {'items': [{'id': 'AwesomeWorkspace'}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/workspaces', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def create_workspace(mock_server_base):
    json = {'workspaceId': 'newWorkspace'}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def workspaces_error(mock_server_base):
    json = {'error': {'message': 'no authroization', 'code': 123}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
        status_code=401,
    )

    return mock_server_base


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


class TestService:
    def test_get_workspaces(self, single_workspace):
        uri = modelon.impact.client.sal.service.URI(single_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_workspace.context
        )
        data = service.workspaces_get_all()
        assert data == {'data': {'items': [{'id': 'AwesomeWorkspace'}]}}

    def test_create_workspace(self, create_workspace):
        uri = modelon.impact.client.sal.service.URI(create_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace.context
        )
        data = service.workspaces_create('AwesomeWorkspace')
        assert data == {'workspaceId': 'newWorkspace'}


class TestHTTPClient:
    def test_get_json_error(self, get_with_error):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_with_error.context
        )
        pytest.raises(
            modelon.impact.client.sal.exceptions.HTTPError,
            client.get_json,
            get_with_error.url,
        )

    def test_get_json_ok(self, get_ok_empty_json):
        client = modelon.impact.client.sal.service.HTTPClient(
            context=get_ok_empty_json.context
        )
        data = client.get_json(get_ok_empty_json.url)
        assert data == {}
