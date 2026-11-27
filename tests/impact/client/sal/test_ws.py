from unittest.mock import MagicMock, patch

from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.ws import SyncWebSocketClient


class TestSyncWebSocketClient:
    def test_connects_to_the_endpoint_of_the_given_workspace(self):
        with patch(
            "modelon.impact.client.sal.ws.ws_connect", return_value=MagicMock()
        ) as ws_connect:
            SyncWebSocketClient(URI("ws://modelon.com/impact"), "ws-id")

        (url,) = ws_connect.call_args.args
        assert url == "ws://modelon.com/impact/api/modeling/rpc/ws-id"
