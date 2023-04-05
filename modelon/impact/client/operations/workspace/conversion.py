from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from modelon.impact.client import exceptions

from modelon.impact.client.operations.base import (
    AsyncOperation,
    AsyncOperationStatus,
    Entity,
)
from modelon.impact.client.sal.service import Service

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import EntityFromOperation


class WorkspaceConversionOperation(AsyncOperation[Entity]):
    """An conversion operation class for the
    modelon.impact.client.entities.workspace.Workspace class."""

    def __init__(
        self, location: str, service: Service, create_entity: EntityFromOperation
    ):
        super().__init__(create_entity)
        self._location = location
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Workspace conversion operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, WorkspaceConversionOperation)
            and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Workspace conversion id."""
        return self._location.split('/')[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Workspace conversion"

    def _info(self) -> Dict[str, Any]:
        return self._sal.workspace.get_workspace_conversion_status(self._location)[
            "data"
        ]

    def data(self) -> Entity:
        """Returns a Workspace class instance of the converted workspace.

        Returns:

            An Workspace class instance.

        """
        info = self._info()
        if info['status'] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalWorkspaceConversion(
                f"Workspace conversion failed! Cause: {info['error'].get('message')}"
            )

        workspace_id = info["data"]["workspaceId"]
        resp = self._sal.workspace.workspace_get(workspace_id)
        return self._create_entity(
            self, workspace_id=resp["id"], workspace_definition=resp["definition"]
        )

    def status(self) -> AsyncOperationStatus:
        """Returns the conversion status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            client.convert_workspace(workspace_id).status()

        """
        return AsyncOperationStatus(self._info()["status"])
