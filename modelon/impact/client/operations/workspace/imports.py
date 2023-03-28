from typing import Dict, Any
from modelon.impact.client.entities.workspace import Workspace, WorkspaceDefinition
from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations.base import AsyncOperation, AsyncOperationStatus
from modelon.impact.client import exceptions


class WorkspaceImportOperation(AsyncOperation):
    """An import operation class for the
    modelon.impact.client.entities.workspace.

    Workspace class.

    """

    def __init__(
        self,
        location: str,
        service: Service,
    ):
        super().__init__()
        self._location = location
        self._sal = service

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
        return self._location.split('/')[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Workspace import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> Workspace:
        """Returns a new Workspace class instance.

        Returns:

            workspace:
                A Workspace class instance.

        """
        info = self._info()
        if info['status'] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalWorkspaceImport(
                f"Workspace import failed! Cause: {info['error'].get('message')}"
            )
        workspace_id = info["data"]["workspaceId"]
        resp = self._sal.workspace.workspace_get(workspace_id)
        return Workspace(resp["id"], WorkspaceDefinition(resp["definition"]), self._sal)

    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:

            upload_status:
                The AsyncOperationStatus enum. The status can have the enum values
                AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
                AsyncOperationStatus.ERROR

        Example::

            client.import_from_shared_definition(definition, False).status()

        """
        return AsyncOperationStatus(self._info()["status"])
