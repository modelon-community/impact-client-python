"""WebSocket client class."""
import itertools
import json
import logging
from typing import Any, Optional

from websockets.sync.client import connect as ws_connect

from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.ws_response import JsonRpcResponse

logger = logging.getLogger(__name__)


class SyncWebSocketClient:
    def __init__(self, uri: URI, api_key: Optional[str] = None):
        url = (uri / "/api/modeling/rpc").resolve()
        headers = {"User-Agent": "impact-python-client"}
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
            if resp.get("method") == "impact/workspace":
                logger.info(resp.get("params", {}).get("message"))
                continue
            response = JsonRpcResponse(resp)
            if response.id == msg_id:
                return response.result
