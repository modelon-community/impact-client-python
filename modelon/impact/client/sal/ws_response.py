from typing import Any, Dict, Optional


class JsonRpcError(Exception):
    def __init__(self, message: str, code: int, data: Optional[Any] = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(f"[{code}] {message}")


class JsonRpcResponse:
    def __init__(self, resp_obj: Dict[str, Any]):
        if "jsonrpc" not in resp_obj or resp_obj["jsonrpc"] != "2.0":
            raise ValueError(f"Invalid JSON-RPC response: {resp_obj}")
        self._resp_obj = resp_obj

    @property
    def id(self) -> int:
        msg_id = self._resp_obj.get("id")
        if msg_id is None:
            raise ValueError(
                f"Expected 'msg_id' field in JSON-RPC response: {self._resp_obj}"
            )
        return msg_id

    @property
    def ok(self) -> bool:
        return "result" in self._resp_obj

    @property
    def result(self) -> Any:
        if not self.ok:
            error = self.error
            if error is None:
                raise ValueError("Expected 'error' field in JSON-RPC error response")
            raise JsonRpcError(
                message=error.get("message", "Unknown error"),
                code=error.get("code", -32000),
                data=error.get("data"),
            )
        return self._resp_obj["result"]

    @property
    def error(self) -> Optional[Dict[str, Any]]:
        err = self._resp_obj.get("error")
        if err is None:
            raise ValueError("No error in response")
        return err
