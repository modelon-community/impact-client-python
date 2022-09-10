from modelon.impact.client.entities.workspace import Workspace, WorkspaceDefinition
from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations.base import AsyncOperation, AsyncOperationStatus
from modelon.impact.client import exceptions


class WorkspaceImportOperation(AsyncOperation):
    """
    An operation class for the modelon.impact.client.entities.workspace.Workspace class.
    """

    def __init__(
        self,
        location: str,
        workspace_definition: WorkspaceDefinition,
        service: Service,
    ):
        super().__init__()
        self._location = location
        self._workspace_definition = workspace_definition
        self._sal = service

    def __repr__(self):
        return f"Workspace import operations for id '{self.id}'"

    def __eq__(self, obj):
        return (
            isinstance(obj, WorkspaceImportOperation)
            and obj._location == self._location
        )

    @property
    def id(self):
        """Workspace import id"""
        return self._location.split('/')[-1]

    @property
    def name(self):
        """Return the name of operation"""
        return "Workspace import"

    def cancel(self):
        raise NotImplementedError('Cancel is not supported for this operation')

    def _info(self):
        return self._sal.workspace.get_workspace_upload_status(self._location)["data"]

    def data(self):
        """
        Returns a new Workspace class instance.

        Returns:

            workspace --
                A Workspace class instance.
        """
        info = self._info()
        if info['status'] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalWorkspaceImport(
                f"Workspace import failed! Cause: {info['error'].get('message')}"
            )
        workspace_id = info["data"]["workspaceId"]
        return Workspace(workspace_id, self._workspace_definition, self._sal)

    def status(self):
        """
        Returns the upload status as an enumeration.

        Returns:

            upload_status --
                The AsyncOperationStatus enum. The status can have the enum values
                AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
                AsyncOperationStatus.ERROR

        Example::

            client.import_from_shared_definition(definition, False).status()
        """
        return AsyncOperationStatus(self._info()["status"])
