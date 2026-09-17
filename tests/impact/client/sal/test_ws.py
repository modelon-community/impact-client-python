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


def answer_after(ws_connect, pushes, payload):
    """Queue server pushes ahead of the reply this request is waiting for."""
    ws_connect.return_value.recv.side_effect = [
        *[json.dumps(push) for push in pushes],
        json.dumps({"jsonrpc": "2.0", "id": 0, **payload}),
    ]


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


class TestServerPushes:
    """The connection carries notifications as well as replies.

    A notification is not an answer to anything, so a request waiting for its reply has
    to read past it. They are recognised by shape - a method and no id - rather than by
    name, because a client cannot know every push a server might grow.

    """

    def test_a_push_does_not_become_the_answer_to_a_request(self, service, ws_connect):
        answer_after(
            ws_connect,
            [
                {
                    "jsonrpc": "2.0",
                    "method": "impact/viewsChanged",
                    "params": {"className": "Unnamed.Test", "change": "updated"},
                }
            ],
            {"result": "pong"},
        )

        assert service.start_modeling_session("my-workspace") is not None

    def test_a_push_this_client_has_never_heard_of_is_skipped(
        self, service, ws_connect
    ):
        # Skipping by shape is the point: a server that grows a new notification must
        # not break a client released before it.
        answer_after(
            ws_connect,
            [{"jsonrpc": "2.0", "method": "impact/somethingFromTheFuture"}],
            {"result": "pong"},
        )

        assert service.start_modeling_session("my-workspace") is not None

    def test_several_pushes_in_a_row_are_read_past(self, service, ws_connect):
        # They queue up while the connection is idle, so a call can meet more than one.
        answer_after(
            ws_connect,
            [
                {"jsonrpc": "2.0", "method": "impact/viewsChanged", "params": {}},
                {
                    "jsonrpc": "2.0",
                    "method": "impact/workspace",
                    "params": {"message": "the workspace changed"},
                },
                {"jsonrpc": "2.0", "method": "impact/viewsChanged", "params": {}},
            ],
            {"result": "pong"},
        )

        assert service.start_modeling_session("my-workspace") is not None

    def test_an_error_reply_is_still_raised_and_not_mistaken_for_a_push(
        self, service, ws_connect
    ):
        # It carries an id, so it is an answer - the shape test must not swallow it.
        answer_with(
            ws_connect,
            {"error": {"code": -32603, "message": "Workspace 'nope' does not exist"}},
        )

        with pytest.raises(JsonRpcError):
            service.start_modeling_session("nope")
