"""WebSocket client class."""

import itertools
import json
import logging
import urllib.parse
from typing import Any, Dict, Optional

from websockets.sync.client import connect as ws_connect

from modelon.impact.client.sal.context import Context
from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.ws_response import JsonRpcResponse

logger = logging.getLogger(__name__)


# Headers the HTTP transport and the WebSocket handshake set themselves. A session's
# values for these, requests' defaults among them, must not reach the handshake:
# "Connection: keep-alive" in place of "Upgrade" would break it.
_TRANSPORT_HEADERS = frozenset(
    {
        "accept",
        "accept-encoding",
        "connection",
        "content-length",
        "content-type",
        "host",
        "keep-alive",
        "proxy-connection",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
        "user-agent",
    }
)


def _caller_headers(context: Optional[Context]) -> Dict[str, str]:
    """The headers set on the context's session, as REST requests send them."""
    if context is None:
        return {}
    return {
        # requests allows bytes values; HTTP header values are Latin-1.
        name: value if isinstance(value, str) else value.decode("latin-1")
        for name, value in context.session.headers.items()
        if name.lower() not in _TRANSPORT_HEADERS
        and not name.lower().startswith("sec-websocket-")
    }


class SyncWebSocketClient:
    def __init__(
        self,
        uri: URI,
        workspace_id: str,
        api_key: Optional[str] = None,
        context: Optional[Context] = None,
    ):
        workspace_path = urllib.parse.quote(workspace_id, safe="")
        url = (uri / f"/api/modeling/rpc/{workspace_path}").resolve()
        headers = {**_caller_headers(context), "User-Agent": "impact-python-client"}
        if api_key:
            headers["impact-api-key"] = api_key
        self._conn = ws_connect(str(url), additional_headers=headers)
        self._session_id = str(self._conn.id)
        self._msg_id_gen = itertools.count()
        logger.info(f"Connected to {url}")

    @property
    def session_id(self) -> str:
        return self._session_id

    def close(self) -> None:
        self._conn.close()
        logger.info("WebSocket connection closed")

    def get_json_response(
        self,
        method: str,
        params: Any = None,
        timeout: float = 10.0,
    ) -> Any:
        msg_id = next(self._msg_id_gen)
        request = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params}
        self._conn.send(json.dumps(request))
        logger.debug(f"Sent message: {request}")
        while True:
            try:
                message = self._conn.recv(timeout=timeout)
            except TimeoutError:
                raise TimeoutError(f"Timeout waiting for response to msg_id {msg_id}")
            msg_str = message.decode() if isinstance(message, bytes) else message
            logger.debug(f"Received message: {msg_str}")
            resp = json.loads(message)
            if "method" in resp and "id" not in resp:
                # A notification: the server telling this connection
                # something, not answering it. Recognized by its shape rather
                # than by its method name, so a push this client has never heard
                # of is skipped rather than read as a malformed response - a
                # response without an id raises when its id is looked up.
                if resp.get("method") == "impact/workspace":
                    logger.info(resp.get("params", {}).get("message"))
                continue
            response = JsonRpcResponse(resp)
            if response.id == msg_id:
                return response.result
