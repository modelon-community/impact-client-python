from __future__ import annotations

import os
import tempfile
from typing import Any, Optional, Text, Union

from modelon.impact.client.entities.file_uri import CustomArtifactURI
from modelon.impact.client.entities.interfaces.custom_artifact import (
    CustomArtifactInterface,
)
from modelon.impact.client.operations.base import BaseOperation
from modelon.impact.client.operations.custom_artifact import (
    CustomArtifactImportOperation,
)
from modelon.impact.client.sal.experiment import ExperimentService


class CustomArtifact(CustomArtifactInterface):
    """CustomArtifact class."""

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
        super().__init__(
            workspace_id, experiment_id, case_id, artifact_id, download_as, exp_sal
        )

    @property
    def id(self) -> str:
        """Id of the custom artifact."""
        return self._artifact_id

    @property
    def download_as(self) -> str:
        """File name for the downloaded artifact."""
        return self._download_as

    def download(self, path: Optional[str] = None) -> str:
        """Downloads a custom artifact. Returns the local path to the downloaded
        artifact.

        Args:
            path: The local path to the directory to store the downloaded custom
                artifact. Default: None. If no path is given, custom artifact
                will be downloaded in a temporary directory.

        Returns:
            path: Local path to the downloaded custom artifact.

        Example::

            artifact_path = artifact.download()
            artifact_path = artifact.download('/home/Downloads')

        """
        artifact, _ = self._exp_sal.case_artifact_get(
            self._workspace_id, self._exp_id, self._case_id, self.id
        )
        if path is None:
            path = os.path.join(tempfile.gettempdir(), "impact-downloads")
        os.makedirs(path, exist_ok=True)
        artifact_path = os.path.join(path, self.download_as)
        with open(artifact_path, mode="wb") as f:
            f.write(artifact)
        return artifact_path

    def get_data(self) -> Union[Text, bytes]:
        """Returns the custom artifact stream.

        Returns:
            artifact: The artifact byte stream.

        Example::

            artifact = case.get_artifact("ABCD")
            data = artifact.get_data() # may raise exception on communication error
            with open(artifact.download_as, "wb") as f:
                f.write(data)

        """
        result_stream, _ = self._exp_sal.case_artifact_get(
            self._workspace_id, self._exp_id, self._case_id, self.id
        )

        return result_stream

    def get_uri(self) -> CustomArtifactURI:
        """Returns a CustomArtifactURI class.

        Returns:
            The CustomArtifactURI class object.

        Example::

            artifact_file_uri = artifact.get_uri()

        """
        return CustomArtifactURI(self._exp_id, self._case_id, self._artifact_id)

    @classmethod
    def from_operation(
        cls, operation: BaseOperation[CustomArtifact], **kwargs: Any
    ) -> CustomArtifact:
        assert isinstance(operation, CustomArtifactImportOperation)
        return cls(**kwargs, exp_sal=operation._sal.experiment)
