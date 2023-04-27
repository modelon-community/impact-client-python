class BaseExternalResult:
    def __init__(self, result_id: str):
        self._result_id = result_id

    def __repr__(self) -> str:
        return f"Result id '{self._result_id}'"

    @property
    def id(self) -> str:
        """Result id."""
        return self._result_id
