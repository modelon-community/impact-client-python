from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseExperimentDefinition(ABC):
    """Base class for an Experiment definition class."""

    @abstractmethod
    def validate(self) -> None:
        """Validates the modifiers appended to the experiment definition."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Returns the experiment definition as a dictionary."""
