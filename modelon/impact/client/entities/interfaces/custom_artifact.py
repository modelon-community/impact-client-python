from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelon.impact.client.sal.experiment import ExperimentService


class CustomArtifactInterface(ABC):
    def __init__(
        self,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        artifact_id: str,
        download_as: str,
        exp_sal: ExperimentService,
    ):
        self._workspace_id = workspace_id
        self._exp_id = experiment_id
        self._case_id = case_id
        self._artifact_id = artifact_id
        self._download_as = download_as
        self._exp_sal = exp_sal

    @property
    @abstractmethod
    def id(self) -> str:
        """Custom artifact id."""
        raise NotImplementedError
