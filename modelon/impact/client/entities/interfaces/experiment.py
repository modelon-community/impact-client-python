from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service


class ExperimentInterface(ABC):
    def __init__(
        self,
        workspace_id: str,
        exp_id: str,
        service: Service,
        info: Optional[Dict[str, Any]] = None,
    ):
        self._exp_id = exp_id
        self._workspace_id = workspace_id
        self._sal = service
        self._info = info

    @property
    @abstractmethod
    def id(self) -> str:
        """Experiment id."""
        raise NotImplementedError

    @abstractmethod
    def get_cases(self) -> Any:
        """Returns a list of case objects for an experiment."""
        raise NotImplementedError


class ExperimentReference(ExperimentInterface):
    def __init__(
        self,
        workspace_id: str,
        exp_id: str,
        service: Service,
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(workspace_id, exp_id, service, info)

    @property
    def id(self) -> str:
        """Experiment id."""
        return self._exp_id

    def get_cases(self) -> Any:
        """Returns a list of case objects for an experiment."""
        raise NotImplementedError
