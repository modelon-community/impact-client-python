from abc import ABC, abstractmethod


class CaseInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """Case id."""
        raise NotImplementedError
