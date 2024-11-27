from abc import ABC, abstractmethod


class ModelInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Model name."""
        raise NotImplementedError
