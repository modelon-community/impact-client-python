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
def sem_ver_check(mock_server_base):
    json = {"version": "1.2.1"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def single_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'AwesomeWorkspace'}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def multiple_workspace(sem_ver_check, mock_server_base):
    json = {'data': {'items': [{'id': 'AwesomeWorkspace'}, {'id': 'BoringWorkspace'}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/workspaces', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def create_workspace(sem_ver_check, mock_server_base):
    json = {'id': 'newWorkspace'}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def workspaces_error(sem_ver_check, mock_server_base):
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
def create_workspace_error(sem_ver_check, mock_server_base):
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


@pytest.fixture
def semantic_version_error(sem_ver_check, mock_server_base):
    json = {"version": "3.1.0"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/', json=json, headers=json_header,
    )

    return mock_server_base


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


def test_create_workspace(create_workspace):
    client = modelon.impact.client.Client(
        url=create_workspace.url, context=create_workspace.context
    )
    workspace = client.create_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('newWorkspace')
    assert workspace.id == 'newWorkspace'


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
        "range '>=1.2.1,<2.0.0'! Updgrade or downgrade this package to a version"
        " that supports version '3.1.0' of the HTTP REST API." in str(excinfo.value)
    )
