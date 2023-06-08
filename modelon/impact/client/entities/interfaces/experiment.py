from abc import ABC, abstractmethod
from typing import Any


class ExperimentInterface(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """Experiment id."""
        raise NotImplementedError

    @abstractmethod
    def get_cases(self) -> Any:
        """Returns a list of case objects for an experiment."""
        raise NotImplementedError
