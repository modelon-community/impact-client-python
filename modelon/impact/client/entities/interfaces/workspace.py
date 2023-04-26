from abc import ABC, abstractmethod


class WorkspaceInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """Workspace id."""
        raise NotImplementedError
