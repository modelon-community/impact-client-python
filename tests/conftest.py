"""
conftest.py
"""
from glob import glob
import requests_mock
import requests
import pytest
import collections
from tests.impact.client.helpers import with_json_route

MockedServer = collections.namedtuple('MockedServer', ['url', 'context', 'adapter'])


def py_file_path_to_module_path(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")


pytest_plugins = [
    py_file_path_to_module_path(fixture)
    for fixture in glob("tests/impact/client/fixtures/*.py")
    if "__" not in fixture
]


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
    mock_server = with_json_route(mock_server_base, 'POST', 'api/login', {})
    mock_server = with_json_route(
        mock_server,
        'GET',
        'hub/api/',
        {},
        extra_headers={},
    )
    return mock_server
