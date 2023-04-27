from __future__ import annotations


class BaseCustomFunction:
    def __init__(self, name: str):
        self._name = name

    def __repr__(self) -> str:
        return f"Custom function '{self._name}'"

    @property
    def name(self) -> str:
        "Custom function name"
        return self._name
