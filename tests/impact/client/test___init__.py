import collections

import pytest
import requests
import requests_mock

import modelon.impact.client
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
def create_workspace_error(mock_server_base):
    json = {'error': {'message': 'name not ok', 'code': 123}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
        status_code=400,
    )

    return mock_server_base


def test_get_workspaces(single_workspace):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspaces = client.get_workspaces()
    assert workspaces == [modelon.impact.client.entities.Workspace('AwesomeWorkspace')]


def test_get_workspaces_error(workspaces_error):
    client = modelon.impact.client.Client(
        url=workspaces_error.url, context=workspaces_error.context
    )
    pytest.raises(modelon.impact.client.sal.exceptions.HTTPError, client.get_workspaces)


def test_get_workspace(single_workspace):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspace = client.get_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('AwesomeWorkspace')


def test_create_workspace(create_workspace):
    client = modelon.impact.client.Client(
        url=create_workspace.url, context=create_workspace.context
    )
    workspace = client.create_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('newWorkspace')


def test_create_workspace_error(create_workspace_error):
    client = modelon.impact.client.Client(
        url=create_workspace_error.url, context=create_workspace_error.context
    )
    pytest.raises(
        modelon.impact.client.sal.exceptions.HTTPError, client.create_workspace, ':^-'
    )
