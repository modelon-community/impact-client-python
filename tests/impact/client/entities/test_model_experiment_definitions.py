from typing import Any, Dict, List
from urllib.parse import parse_qs, urlsplit

import pytest

from modelon.impact.client.entities.model import Model
from modelon.impact.client.sal.service import Service
from modelon.impact.client.sal.uri import URI
from tests.impact.client.helpers import (
    IDs,
    create_custom_function_entity,
    with_json_route,
)

pytestmark = pytest.mark.experimental

CHILD_MODEL = "Lib.Child"
PARENT_MODEL = "Lib.Base"
DEFINITION_ID = "expdef-1"
DEFINITIONS_PATH = (
    f"api/workspaces/{IDs.WORKSPACE_ID_PRIMARY}/models/{CHILD_MODEL}/"
    "experiment-definitions"
)
EXPERIMENT = {
    "base": {
        "model": {"modelica": {}},
        "analysis": {
            "type": IDs.DYNAMIC_CF,
            "parameters": [{"name": "final_time", "value": 50}],
        },
    }
}


class FakeModelingSession:
    def __init__(self, extends: List[str]):
        self._extends = extends

    def get_extends_clauses(self, class_name: str) -> List[str]:
        return self._extends

    def get_experiment_annotations(self, class_name: str) -> Dict[str, Any]:
        return {}


def definition_item(name: str) -> Dict[str, Any]:
    return {
        "id": DEFINITION_ID,
        "metadata": {
            "name": name,
            "modelName": CHILD_MODEL,
            "requestedModelName": CHILD_MODEL,
            "projectId": IDs.PROJECT_ID_PRIMARY,
            "created": "2026-11-20T15:43:22Z",
            "lastModified": "2026-11-21T07:28:42Z",
            "isDefault": False,
            "isReadOnly": False,
        },
        "experiment": EXPERIMENT,
    }


@pytest.fixture
def server(mock_server_base):
    with_json_route(
        mock_server_base,
        "GET",
        f"api/workspaces/{IDs.WORKSPACE_ID_PRIMARY}/custom-functions/{IDs.DYNAMIC_CF}",
        {
            "name": IDs.DYNAMIC_CF,
            "parameters": [{"name": "final_time", "type": "Number", "defaultValue": 1}],
        },
    )
    return mock_server_base


def model_in(server, extends: List[str]) -> Model:
    sal = Service(URI(server.url), "api-key", server.context)
    session = FakeModelingSession(extends)
    return Model(
        CHILD_MODEL,
        IDs.WORKSPACE_ID_PRIMARY,
        IDs.PROJECT_ID_PRIMARY,
        sal,
        modeling_sal_getter=lambda: session,
    )


def path_of(request) -> str:
    return urlsplit(request.url).path


def only_request(server, method: str, path: str):
    [request] = [
        r
        for r in server.adapter.request_history
        if r.method == method and path_of(r) == f"/{path}"
    ]
    return request


def query_of(request) -> Dict[str, List[str]]:
    return parse_qs(urlsplit(request.url).query)


def test_a_created_definition_is_posted_to_the_models_workspace_route(server):
    # Given a model whose template the server resolves
    with_json_route(
        server,
        "POST",
        f"api/workspaces/{IDs.WORKSPACE_ID_PRIMARY}/models/{CHILD_MODEL}/"
        "experiment-definition-template",
        {"data": {"metadata": {"name": "Template"}, "experiment": EXPERIMENT}},
    )
    with_json_route(
        server, "POST", DEFINITIONS_PATH, {"data": definition_item("My run")}
    )
    model = model_in(server, extends=[])
    dynamic = create_custom_function_entity(IDs.WORKSPACE_ID_PRIMARY, IDs.DYNAMIC_CF)

    # When a default experiment definition is created for it
    entry = model.create_default_experiment_definition(
        dynamic, name="My run", is_default=True
    )

    # Then it is posted to the workspace route of the model
    create_request = only_request(server, "POST", DEFINITIONS_PATH)
    assert create_request.json() == {
        "data": {
            "metadata": {"name": "My run", "setAsDefault": True},
            "experiment": EXPERIMENT,
        }
    }
    assert entry.id == DEFINITION_ID


def test_an_updated_definition_is_put_to_its_workspace_route_with_the_extends(
    server,
):
    # Given a model that extends a parent class, with a stored definition
    with_json_route(
        server,
        "GET",
        DEFINITIONS_PATH,
        {"data": {"items": [definition_item("My run")]}},
    )
    with_json_route(
        server,
        "PUT",
        f"{DEFINITIONS_PATH}/{DEFINITION_ID}",
        {"data": definition_item("Renamed run")},
    )
    model = model_in(server, extends=[PARENT_MODEL])
    [stored] = model.get_experiment_definitions()

    # When the definition is updated
    entry = model.update_experiment_definition(
        stored.id, stored.definition, name="Renamed run"
    )

    # Then it is put to the definition's workspace route along with the extends
    update_request = only_request(server, "PUT", f"{DEFINITIONS_PATH}/{DEFINITION_ID}")
    assert query_of(update_request) == {"extends": [PARENT_MODEL]}
    assert update_request.json()["data"]["metadata"] == {
        "name": "Renamed run",
        "setAsDefault": False,
    }
    assert entry.name == "Renamed run"


def test_an_update_of_a_model_without_extends_sends_no_extends(server):
    # Given a model that extends nothing, with a stored definition
    with_json_route(
        server,
        "GET",
        DEFINITIONS_PATH,
        {"data": {"items": [definition_item("My run")]}},
    )
    with_json_route(
        server,
        "PUT",
        f"{DEFINITIONS_PATH}/{DEFINITION_ID}",
        {"data": definition_item("My run")},
    )
    model = model_in(server, extends=[])
    [stored] = model.get_experiment_definitions()

    # When the definition is updated
    model.update_experiment_definition(stored.id, stored.definition)

    # Then the update carries no extends query
    update_request = only_request(server, "PUT", f"{DEFINITIONS_PATH}/{DEFINITION_ID}")
    assert query_of(update_request) == {}
