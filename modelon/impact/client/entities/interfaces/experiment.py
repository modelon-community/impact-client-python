from abc import ABC, abstractmethod
from typing import Any


class BaseExperiment(ABC):
    def __init__(self, exp_id: str):
        self._exp_id = exp_id

    def __repr__(self) -> str:
        return f"Experiment with id '{self._exp_id}'"

    @property
    def id(self) -> str:
        """Experiment id."""
        return self._exp_id

    @abstractmethod
    def get_cases(self) -> Any:
        pass
