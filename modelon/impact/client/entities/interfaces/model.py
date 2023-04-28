from typing import Protocol, runtime_checkable


@runtime_checkable
class ModelProtocol(Protocol):
    @property
    def name(self) -> str:
        """Class name."""
        ...
