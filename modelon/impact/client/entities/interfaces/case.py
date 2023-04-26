from __future__ import annotations


class BaseCase:
    def __init__(self, case_id: str):
        self._case_id = case_id

    def __repr__(self) -> str:
        return f"Case with id '{self._case_id}'"

    @property
    def id(self) -> str:
        """Case id."""
        return self._case_id
