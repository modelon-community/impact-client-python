import json
from unittest import mock

import pytest

from modelon.impact.client.sal.service import Service
from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.ws import SyncWebSocketClient
from modelon.impact.client.sal.ws_response import JsonRpcError


@pytest.fixture
def ws_connect():
    with mock.patch("modelon.impact.client.sal.ws.ws_connect") as connect:
        connect.return_value.id = "connection-1"
        yield connect


@pytest.fixture
def service(ws_connect):
    with mock.patch(
        "modelon.impact.client.sal.service.is_jupyterhub_url", return_value=False
    ):
        yield Service(URI("http://modelon.com"), "api-key")


def connected_url(ws_connect):
    return ws_connect.call_args[0][0]


def answer_with(ws_connect, payload):
    ws_connect.return_value.recv.return_value = json.dumps(
        {"jsonrpc": "2.0", "id": 0, **payload}
    )


def sent_request(ws_connect):
    return json.loads(ws_connect.return_value.send.call_args[0][0])


class TestSyncWebSocketClient:
    def test_the_address_names_the_workspace_the_connection_serves(self, ws_connect):
        SyncWebSocketClient(URI("ws://modelon.com"), "my-workspace")

        assert (
            connected_url(ws_connect)
            == "ws://modelon.com/api/modeling/rpc/my-workspace"
        )

    def test_a_workspace_id_is_escaped_into_a_single_path_segment(self, ws_connect):
        SyncWebSocketClient(URI("ws://modelon.com"), "awkward/id")

        assert (
            connected_url(ws_connect)
            == "ws://modelon.com/api/modeling/rpc/awkward%2Fid"
        )

    def test_a_base_uri_with_a_path_keeps_it(self, ws_connect):
        SyncWebSocketClient(URI("ws://modelon.com/impact"), "my-workspace")

        assert (
            connected_url(ws_connect)
            == "ws://modelon.com/impact/api/modeling/rpc/my-workspace"
        )


class TestStartModelingSession:
    def test_waits_for_the_workspace_before_handing_back_a_session(
        self, service, ws_connect
    ):
        answer_with(ws_connect, {"result": "pong"})

        service.start_modeling_session("my-workspace")

        assert sent_request(ws_connect)["method"] == "impact/ping"

    def test_a_workspace_that_cannot_be_opened_closes_the_connection(
        self, service, ws_connect
    ):
        answer_with(
            ws_connect,
            {"error": {"code": -32603, "message": "Workspace 'nope' does not exist"}},
        )

        with pytest.raises(JsonRpcError):
            service.start_modeling_session("nope")

        ws_connect.return_value.close.assert_called_once()
