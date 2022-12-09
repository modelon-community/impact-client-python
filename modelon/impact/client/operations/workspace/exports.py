import os
from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations.base import AsyncOperation, AsyncOperationStatus
from modelon.impact.client import exceptions


class BinaryBlob:
    def __init__(self, binary_data):
        self._data = binary_data

    def download_as(self, path_to_download):
        """Writes the binary archive to a file.
        Returns the path to downloaded archive.

        Parameters:

            path_to_download --
                The path to store the downloaded workspace.

        Returns:

            path --
                Local path to the downloaded archive.

        Example::

            path = workspace.download(options).wait().download_as('/home/workspace.zip')
            path = workspace.download(options).wait().download_as('workspace.zip')
        """
        os.makedirs(os.path.dirname(path_to_download), exist_ok=True)
        with open(path_to_download, "wb") as f:
            f.write(self._data)
        return path_to_download


class WorkspaceExportOperation(AsyncOperation):
    """
    An export operation class for the modelon.impact.client.entities.workspace.
    Workspace class.
    """

    def __init__(
        self, location: str, service: Service,
    ):
        super().__init__()
        self._location = location
        self._sal = service

    def __repr__(self):
        return f"Workspace export operations for id '{self.id}'"

    def __eq__(self, obj):
        return (
            isinstance(obj, WorkspaceExportOperation)
            and obj._location == self._location
        )

    @property
    def id(self):
        """Workspace export id"""
        return self._location.split('/')[-1]

    @property
    def name(self):
        """Return the name of operation"""
        return "Workspace export"

    def cancel(self):
        raise NotImplementedError('Cancel is not supported for this operation')

    def _info(self):
        return self._sal.workspace.get_workspace_export_status(self._location)["data"]

    def data(self):
        """
        Returns a new Workspace class instance.

        Returns:

            A BinaryBlob class object.
        """
        info = self._info()
        if info['status'] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalWorkspaceExport(
                f"Workspace export failed! Cause: {info['error'].get('message')}"
            )
        return BinaryBlob(self._sal.export.export_download(info["data"]["downloadUri"]))

    def status(self):
        """
        Returns the upload status as an enumeration.

        Returns:

            upload_status --
                The AsyncOperationStatus enum. The status can have the enum values
                AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
                AsyncOperationStatus.ERROR

        Example::

            workspace.download(definition, False).status()
        """
        return AsyncOperationStatus(self._info()["status"])
