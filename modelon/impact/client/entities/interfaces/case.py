from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service


class CaseInterface(ABC):
    def __init__(
        self,
        case_id: str,
        workspace_id: str,
        exp_id: str,
        service: Service,
        info: Dict[str, Any],
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._sal = service
        self._info = info

    @property
    @abstractmethod
    def id(self) -> str:
        """Case id."""
        raise NotImplementedError

    @property
    def experiment_id(self) -> str:
        """Experiment id."""
        raise NotImplementedError


class CaseReference(CaseInterface):
    def __init__(
        self,
        case_id: str,
        workspace_id: str,
        exp_id: str,
        service: Service,
        info: Dict[str, Any],
    ):
        super().__init__(case_id, workspace_id, exp_id, service, info)

    @property
    def id(self) -> str:
        """Case id."""
        return self._case_id

    @property
    def experiment_id(self) -> str:
        """Experiment id."""
        return self._exp_id
