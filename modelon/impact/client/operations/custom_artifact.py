from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from modelon.impact.client import exceptions
from modelon.impact.client.operations.base import (
    AsyncOperation,
    AsyncOperationStatus,
    Entity,
)

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import EntityFromOperation
    from modelon.impact.client.sal.service import Service


class CustomArtifactImportOperation(AsyncOperation[Entity]):
    """An operation class for the CustomArtifact class."""

    def __init__(
        self,
        location: str,
        workspace_id: str,
        exp_id: str,
        case_id: str,
        service: Service,
        create_entity: EntityFromOperation,
    ):
        super().__init__(create_entity)
        self._location = location
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._case_id = case_id
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Content import operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, CustomArtifactImportOperation)
            and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Custom artifact import id."""
        return self._location.split("/")[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Custom artifact import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def _get_artifact_download_name(self, artifact_id: str) -> str:
        resp = self._sal.experiment.case_artifacts_meta_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        meta = next(
            (meta for meta in resp["data"]["items"] if meta["id"] == artifact_id),
            None,
        )
        if not meta:
            raise exceptions.NoSuchCustomArtifactError(
                f"No custom artifact found with ID: {artifact_id}."
            )
        return meta["downloadAs"]

    def data(self) -> Entity:
        """Returns a new CustomArtifact class instance.

        Returns:
            A CustomArtifact class instance.

        """
        info = self._info()
        if info["status"] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalCustomArtifactImport(
                f"CustomArtifact import failed! Cause: {info['error'].get('message')}"
            )
        artifact_id = info["data"]["artifactId"]
        download_as = self._get_artifact_download_name(artifact_id)
        return self._create_entity(
            self,
            workspace_id=self._workspace_id,
            experiment_id=self._exp_id,
            case_id=self._case_id,
            artifact_id=artifact_id,
            download_as=download_as,
        )

    @property
    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            case.import_custom_artifact('path/to/artifact.csv').status

        """
        return AsyncOperationStatus(self._info()["status"])
