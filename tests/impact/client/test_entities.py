import collections

import pytest
import requests
import requests_mock
import unittest.mock

import modelon.impact.client
import modelon.impact.client.sal.exceptions
import modelon.impact.client.sal.service
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from modelon.impact.client.entities import CustomFunction

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

    mock_server_base = MockedServer(mock_url, MockContex(session), adapter)
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST', f'{mock_server_base.url}/api/login', headers=json_header, json={}
    )

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
def delete_ws(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace',
        status_code=200,
    )

    return mock_server_base


@pytest.fixture
def import_lib(sem_ver_check, mock_server_base):
    json = {
        "name": "Single",
        "uses": {"Modelica": {"version": "3.2.2"}, "ThermalPower": {"version": "1.14"}},
    }
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace/libraries',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def lock_ws(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace/lock',
        status_code=200,
    )

    return mock_server_base


@pytest.fixture
def unlock_ws(sem_ver_check, mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace/lock',
        status_code=200,
    )

    return mock_server_base


def test_del_workspace(single_workspace, delete_ws):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspace = client.get_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('AwesomeWorkspace')
    workspace.delete()


def test_import_lib(single_workspace, import_lib):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspace = client.get_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('AwesomeWorkspace')
    resp = workspace.import_library(SINGLE_FILE_LIBRARY_PATH)
    assert resp == {
        "name": "Single",
        "uses": {"Modelica": {"version": "3.2.2"}, "ThermalPower": {"version": "1.14"}},
    }


def test_lock_workspace(single_workspace, lock_ws):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspace = client.get_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('AwesomeWorkspace')
    workspace.lock()


def test_unlock_workspace(single_workspace, unlock_ws):
    client = modelon.impact.client.Client(
        url=single_workspace.url, context=single_workspace.context
    )
    workspace = client.get_workspace('AwesomeWorkspace')
    assert workspace == modelon.impact.client.entities.Workspace('AwesomeWorkspace')
    workspace.unlock()


@pytest.fixture
def custom_function_parameter_list():
    return [
        {'name': 'p1', 'defaultValue': 1.0, 'type': 'Number'},
        {'name': 'p2', 'defaultValue': True, 'type': 'Boolean'},
        {
            'name': 'p3',
            'defaultValue': 'hej',
            'type': 'Enumeration',
            'values': ['hej', 'då'],
        },
        {'name': 'p4', 'defaultValue': 'a string', 'type': 'String'},
    ]


@pytest.fixture
def custom_function(custom_function_parameter_list):
    custom_function_service = unittest.mock.MagicMock()
    return CustomFunction(
        'ws', 'test', custom_function_parameter_list, custom_function_service
    )


def test_workspace_get_custom_function(custom_function_parameter_list):
    custom_function_service = unittest.mock.MagicMock()
    custom_function_service.custom_function_get.return_value = {
        'name': 'dynamic',
        'parameters': custom_function_parameter_list,
    }
    ws = modelon.impact.client.entities.Workspace(
        'AwesomeWorkspace', custom_function_service=custom_function_service
    )
    custom_function = ws.get_custom_function('dynamic')
    assert 'dynamic' == custom_function.name


def test_workspace_get_custom_functions(custom_function_parameter_list):
    custom_function_service = unittest.mock.MagicMock()
    custom_function_service.custom_functions_get.return_value = {
        'data': {
            'items': [{'name': 'dynamic', 'parameters': custom_function_parameter_list}]
        }
    }
    ws = modelon.impact.client.entities.Workspace(
        'AwesomeWorkspace', custom_function_service=custom_function_service
    )
    custom_function_list = [
        custom_function.name for custom_function in ws.get_custom_functions()
    ]
    assert ['dynamic'] == custom_function_list


def test_custom_function_with_parameters_ok(custom_function):
    new = custom_function.with_parameters(p1=3.4, p2=False, p3='då', p4='new string')
    assert new.parameter_values == {
        'p1': 3.4,
        'p2': False,
        'p3': 'då',
        'p4': 'new string',
    }


def test_custom_function_with_parameters_no_such_parameter(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, does_not_exist=3.4)


def test_custom_function_with_parameters_cannot_set_number_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p1='not a number')


def test_custom_function_with_parameters_cannot_set_boolean_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p2='not a boolean')


def test_custom_function_with_parameters_cannot_set_enumeration_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p3=4.6)


def test_custom_function_with_parameters_cannot_set_string_type(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p4=4.6)


def test_custom_function_with_parameters_cannot_set_enumeration_value(custom_function):
    pytest.raises(ValueError, custom_function.with_parameters, p3='not in values')
