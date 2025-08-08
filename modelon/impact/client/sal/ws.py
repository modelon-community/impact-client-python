"""WebSocket client class."""
import asyncio
import itertools
import json
import logging
import threading
from typing import Any, Dict, Optional

import websockets

from modelon.impact.client.sal.uri import URI
from modelon.impact.client.sal.ws_response import JsonRpcResponse

logger = logging.getLogger(__name__)


class WebSocketRPCClient:
    def __init__(self, uri: URI, api_key: Optional[str] = None):
        self._uri = (uri / "/api/modeling/rpc").resolve()
        self._api_key = api_key
        self._msg_id_gen = itertools.count()
        self._pending: Dict[int, asyncio.Future] = {}
        self._conn = None
        self._session_id = None
        self._listener_task: Optional[asyncio.Task] = None

    @property
    def session_id(self) -> str:
        if not self._session_id:
            logger.error("WebSocket connection is not established.")
            return ""
        return str(self._session_id)

    async def connect(self) -> None:
        headers = {"User-Agent": "impact-python-client"}
        if self._api_key:
            headers["impact-api-key"] = self._api_key

        self._conn = await websockets.connect(
            self._uri,
            additional_headers=headers,
        )  # type: ignore
        self._session_id = self._conn.id  # type: ignore
        logger.info(f"Connected to {self._uri}")
        self._listener_task = asyncio.create_task(self._listen())

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
        if self._listener_task:
            self._listener_task.cancel()
        logger.info("WebSocket connection closed")

    async def _listen(self) -> None:
        if not self._conn:
            logger.error("WebSocket connection is not established.")
            return
        try:
            async for message in self._conn:
                logger.debug(f"Received message: {message}")
                resp = json.loads(message)
                if resp.get("method") == "impact/workspace":
                    logger.info(resp.get("params", {}).get("message"))
                    continue
                response = JsonRpcResponse(resp)
                msg_id = response.id
                future = self._pending.pop(msg_id, None)
                if future:
                    future.set_result(response)
        except asyncio.CancelledError:
            logger.info("WebSocket listener cancelled")
        except Exception as e:
            logger.exception(f"Error in WebSocket listener. Cause {e}")

    async def send_rpc(
        self, method: str, params: Any, timeout: Optional[float] = 10.0
    ) -> Any:
        if not self._conn:
            raise RuntimeError("WebSocket is not connected")

        msg_id = next(self._msg_id_gen)
        request = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params}
        future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = future
        await self._conn.send(json.dumps(request))
        logger.debug(f"Sent message: {request}")
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            self._pending.pop(msg_id, None)
            raise TimeoutError(f"Timeout waiting for response to msg_id {msg_id}")


class SyncWebSocketClient:
    def __init__(self, websocket_rpc_client: WebSocketRPCClient):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._start_loop, daemon=True)
        self._thread.start()
        self._client = websocket_rpc_client
        self._run(self._client.connect())

    def _start_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run(self, coro: Any) -> Any:
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    @property
    def session_id(self) -> str:
        return self._client.session_id

    def close(self) -> None:
        self._run(self._client.close())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()

    def get_json_response(
        self,
        method: str,
        params: Any = None,
    ) -> Any:
        response = self._run(self._client.send_rpc(method, params, timeout=10))
        return response.result
