from typing import Optional, Dict, Any
from abc import abstractmethod, ABC


class ExpansionAlgorithm(ABC):
    """Base class for an expansion algorithm."""

    @abstractmethod
    def __str__(self) -> str:
        "Returns a string representation of the expansion algorithm"

    @abstractmethod
    def get_parameters_as_dict(self) -> Optional[Dict[str, Any]]:
        "Returns parameters as a dictionary"
