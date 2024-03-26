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


class WorkspaceImportOperation(AsyncOperation[Entity]):
    """An import operation class for the Workspace class."""

    def __init__(
        self, location: str, service: Service, create_entity: EntityFromOperation
    ):
        super().__init__(create_entity)
        self._location = location
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Workspace import operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, WorkspaceImportOperation)
            and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Workspace import id."""
        return self._location.split("/")[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Workspace import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> Entity:
        """Returns a new Workspace class instance.

        Returns:
            A Workspace class instance.

        """
        info = self._info()
        if info["status"] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalWorkspaceImport(
                f"Workspace import failed! Cause: {info['error'].get('message')}"
            )
        workspace_id = info["data"]["workspaceId"]
        resp = self._sal.workspace.workspace_get(workspace_id, False)
        return self._create_entity(self, workspace_id=resp["id"])

    @property
    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            client.import_workspace_from_shared_definition(definition, False).status

        """
        return AsyncOperationStatus(self._info()["status"])
