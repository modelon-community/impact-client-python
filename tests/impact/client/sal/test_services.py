import collections
import pytest
import requests
import requests_mock
import modelon.impact.client.sal.service
import modelon.impact.client.sal.exceptions
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH, TEST_WORKSPACE_PATH

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
        'GET',
        f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def multiple_workspace(mock_server_base):
    json = {'data': {'items': [{'id': 'AwesomeWorkspace'}, {'id': 'BoringWorkspace'}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/workspaces', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def upload_workspace(mock_server_base):
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
def _get_export_id(mock_server_base):
    json = {"export_id": "0d96b08c8d", "file_size": 2156}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/Workspace/exports',
        json=json,
        headers=json_header,
    )


@pytest.fixture
def download_workspace(mock_server_base, _get_export_id):
    content = bytes(4)
    content_header = {'content-type': 'application/zip'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/Workspace/exports/0d96b08c8d',
        content=content,
        headers=content_header,
    )

    return mock_server_base


@pytest.fixture
def lock_workspace(mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST', f'{mock_server_base.url}/api/workspaces/Workspace/lock',
    )

    return mock_server_base


@pytest.fixture
def unlock_workspace(mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE', f'{mock_server_base.url}/api/workspaces/Workspace/lock',
    )

    return mock_server_base


@pytest.fixture
def clone_workspace(mock_server_base):
    json = {"workspace_id": "clone_44e8ad8c036"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/Workspace/clone',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def import_lib(mock_server_base):
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
def get_fmu(mock_server_base):
    json = {"id": "pid_20090615_134"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/pid_20090615_134',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def get_all_fmu(mock_server_base):
    json = {"data": {"items": [{"id": "as9f-3df5"}, {"id": "as9f-3df5"}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def get_all_experiments(mock_server_base):
    json = {"data": {"items": [{"id": "as9f-3df5"}, {"id": "as9f-3df5"}]}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def get_experiment(mock_server_base):
    json = {"id": "pid_20090615_134"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_20090615_134',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def experiment_create(mock_server_base):
    json = {"experiment_id": "pid_2009"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/experiments',
        json=json,
        headers=json_header,
    )
    return mock_server_base


@pytest.fixture
def experiment_execute(mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/experiments/pid_2009/execution',
    )

    return mock_server_base


@pytest.fixture
def _get_fmu_id(mock_server_base):
    json = {
        "id": "workspace_pid_controller_20090615_134530_as86g32",
        "parameters": {"inertia1.J": 2},
    }
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables',
        json=json,
        headers=json_header,
    )


@pytest.fixture
def model_compile(_get_fmu_id, mock_server_base):
    mock_server_base.adapter.register_uri(
        'POST',
        f'{mock_server_base.url}/api/workspaces/WS/model-executables/'
        'workspace_pid_controller_20090615_134530_as86g32/compilation',
    )

    return mock_server_base


@pytest.fixture
def get_custom_functions(mock_server_base):
    json = {"data": {"items": []}}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET',
        f'{mock_server_base.url}/api/workspaces/WS/custom-functions',
        json=json,
        headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def api_get_metadata(mock_server_base):
    json = {"version": "1.1.0"}
    json_header = {'content-type': 'application/json'}
    mock_server_base.adapter.register_uri(
        'GET', f'{mock_server_base.url}/api/', json=json, headers=json_header,
    )

    return mock_server_base


@pytest.fixture
def create_workspace(mock_server_base):
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
def delete_workspace(mock_server_base):
    mock_server_base.adapter.register_uri(
        'DELETE', f'{mock_server_base.url}/api/workspaces/AwesomeWorkspace'
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
    def test_api_get_meta_data(self, api_get_metadata):
        uri = modelon.impact.client.sal.service.URI(api_get_metadata.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=api_get_metadata.context
        )
        data = service.api_get_metadata()
        assert data == {'version': '1.1.0'}


class TestWorkspaceService:
    def test_get_workspaces(self, multiple_workspace):
        uri = modelon.impact.client.sal.service.URI(multiple_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_workspace.context
        )
        data = service.workspace.workspaces_get_all()
        assert data == {
            'data': {'items': [{'id': 'AwesomeWorkspace'}, {'id': 'BoringWorkspace'}]}
        }

    def test_get_workspace(self, single_workspace):
        uri = modelon.impact.client.sal.service.URI(single_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_workspace.context
        )
        data = service.workspace.workspaces_get('AwesomeWorkspace')
        assert data == {'data': {'items': [{'id': 'AwesomeWorkspace'}]}}

    def test_create_workspace(self, create_workspace):
        uri = modelon.impact.client.sal.service.URI(create_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace.context
        )
        data = service.workspace.workspaces_create('AwesomeWorkspace')
        assert data == {'id': 'newWorkspace'}

    def test_delete_workspace(self, delete_workspace):
        uri = modelon.impact.client.sal.service.URI(delete_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_workspace.context
        )
        service.workspace.workspaces_delete('AwesomeWorkspace')
        assert delete_workspace.adapter.called

    def test_library_import(self, import_lib):
        uri = modelon.impact.client.sal.service.URI(import_lib.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_lib.context
        )
        service.workspace.library_import('AwesomeWorkspace', SINGLE_FILE_LIBRARY_PATH)
        assert import_lib.adapter.called

    def test_workspaces_upload(self, upload_workspace):
        uri = modelon.impact.client.sal.service.URI(upload_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=upload_workspace.context
        )
        data = service.workspace.workspaces_upload(TEST_WORKSPACE_PATH)
        assert data == {'id': 'newWorkspace'}

    def test_lock_ws(self, lock_workspace):
        uri = modelon.impact.client.sal.service.URI(lock_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=lock_workspace.context
        )
        service.workspace.workspace_lock("Workspace")
        assert lock_workspace.adapter.called

    def test_unlock_ws(self, unlock_workspace):
        uri = modelon.impact.client.sal.service.URI(unlock_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=unlock_workspace.context
        )
        service.workspace.workspace_unlock("Workspace")
        assert unlock_workspace.adapter.called

    def test_clone_ws(self, clone_workspace):
        uri = modelon.impact.client.sal.service.URI(clone_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=clone_workspace.context
        )
        data = service.workspace.workspace_clone("Workspace")
        assert data == {'workspace_id': 'clone_44e8ad8c036'}

    def test_fmu_get(self, get_fmu):
        uri = modelon.impact.client.sal.service.URI(get_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_fmu.context
        )
        data = service.workspace.fmu_get("WS", "pid_20090615_134")
        assert data == {'id': 'pid_20090615_134'}

    def test_fmu_get_all(self, get_all_fmu):
        uri = modelon.impact.client.sal.service.URI(get_all_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_fmu.context
        )
        data = service.workspace.fmu_get_all("WS")
        assert data == {'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9f-3df5'}]}}

    def test_model_execute(self, experiment_execute):
        uri = modelon.impact.client.sal.service.URI(experiment_execute.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_execute.context
        )
        service.workspace.execute_experiment("WS", "pid_2009")
        assert experiment_execute.adapter.called

    def test_get_experiment(self, get_experiment):
        uri = modelon.impact.client.sal.service.URI(get_experiment.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_experiment.context
        )
        data = service.workspace.experiment_get("WS", 'pid_20090615_134')
        assert data == {'id': 'pid_20090615_134'}

    def test_get_experiments(self, get_all_experiments):
        uri = modelon.impact.client.sal.service.URI(get_all_experiments.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_experiments.context
        )
        data = service.workspace.experiment_get_all("WS")
        assert data == {'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9f-3df5'}]}}


class TestModelExecutbleService:
    def test_compile_model(self, model_compile):
        uri = modelon.impact.client.sal.service.URI(model_compile.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=model_compile.context
        )
        options = {
            "input": {
                "class_name": "Workspace.PID_Controller",
                "compiler_options": {},
                "runtime_options": {"log_level": 4},
                "compiler_log_level": "info",
                "fmi_target": "me",
                "fmi_version": "2.0",
                "platform": "win64",
            }
        }
        service.model_executable.compile_model("WS", options)
        assert model_compile.adapter.called


class TestCustomFunctionService:
    def test_get_all(self, get_custom_functions):
        http_client = modelon.impact.client.sal.service.HTTPClient(
            context=get_custom_functions.context
        )

        uri = modelon.impact.client.sal.service.URI(get_custom_functions.url)
        service = modelon.impact.client.sal.service.CustomFunctionService(
            uri, http_client
        )
        custom_functions = service.get_all('WS')
        assert {"data": {"items": []}} == custom_functions


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
