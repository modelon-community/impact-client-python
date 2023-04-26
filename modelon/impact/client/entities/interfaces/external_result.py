from abc import ABC, abstractmethod


class ExternalResultInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """Result id."""
        raise NotImplementedError
