from abc import ABC, abstractmethod


class ModelExecutableInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """FMU id."""
        raise NotImplementedError
