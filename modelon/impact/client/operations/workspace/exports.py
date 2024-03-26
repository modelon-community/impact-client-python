from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict

from modelon.impact.client import exceptions
from modelon.impact.client.operations.base import (
    AsyncOperation,
    AsyncOperationStatus,
    BaseOperation,
    Entity,
)

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import EntityFromOperation
    from modelon.impact.client.sal.exports import ExportService
    from modelon.impact.client.sal.service import Service


class Export:
    def __init__(self, export_service: ExportService, download_uri: str):
        self._export_sal = export_service
        self._download_uri = download_uri

    @property
    def id(self) -> str:
        """ID of the export."""
        return self._download_uri.split("/")[-1]

    def download_as(self, path_to_download: str) -> str:
        """Writes the binary archive to a file. Returns the path to downloaded archive.

        Args:
            path_to_download: The path to store the downloaded workspace.

        Returns:
            local path to the downloaded archive.

        Example::

            path = workspace.export().wait().download_as('/home/workspace.zip')
            path = workspace.export().wait().download_as('workspace.zip')

        """
        data = self._export_sal.export_download(self._download_uri)
        os.makedirs(os.path.dirname(path_to_download), exist_ok=True)
        with open(path_to_download, "wb") as f:
            f.write(data)
        return path_to_download

    @classmethod
    def from_operation(cls, operation: BaseOperation[Export], **kwargs: Any) -> Export:
        assert isinstance(operation, WorkspaceExportOperation)
        return cls(**kwargs, export_service=operation._sal.exports)


class WorkspaceExportOperation(AsyncOperation[Entity]):
    """An export operation class for the Workspace class."""

    def __init__(
        self, location: str, service: Service, create_entity: EntityFromOperation
    ):
        super().__init__(create_entity)
        self._location = location
        self._sal = service

    def __repr__(self) -> str:
        return f"Workspace export operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, WorkspaceExportOperation)
            and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Workspace export id."""
        return self._location.split("/")[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Workspace export"

    def _info(self) -> Dict[str, Any]:
        return self._sal.exports.get_export_status(self._location)["data"]

    def data(self) -> Entity:
        """Returns a Export class instance.

        Returns:
            An Export class instance.

        """
        info = self._info()
        if info["status"] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalWorkspaceExport(
                f"Workspace export failed! Cause: {info['error'].get('message')}"
            )
        return self._create_entity(self, download_uri=info["data"]["downloadUri"])

    @property
    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            workspace.download().status

        """
        return AsyncOperationStatus(self._info()["status"])
