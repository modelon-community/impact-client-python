from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations.base import AsyncOperation, AsyncOperationStatus
from modelon.impact.client import exceptions
from modelon.impact.client.entities.content import ProjectContent


class ContentImportOperation(AsyncOperation):
    """
    An operation class for the modelon.impact.client.entities.project.ProjectContent
    class.
    """

    def __init__(self, location: str, service: Service):
        super().__init__()
        self._location = location
        self._sal = service

    def __repr__(self):
        return f"Content import operations for id '{self.id}'"

    def __eq__(self, obj):
        return (
            isinstance(obj, ContentImportOperation) and obj._location == self._location
        )

    @property
    def id(self):
        """Content import id"""
        return self._location.split('/')[-1]

    @property
    def name(self):
        """Return the name of operation"""
        return "Content import"

    def cancel(self):
        raise NotImplementedError('Cancel is not supported for this operation')

    def _info(self):
        return self._sal.project.project_content_upload_status(self._location)["data"]

    def data(self):
        """
        Returns a new Workspace class instance.

        Returns:

            workspace --
                A Workspace class instance.
        """
        info = self._info()
        if info['status'] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalContentImport(
                f"Content import failed! Cause: {info['error'].get('message')}"
            )
        project_id = info["data"]["projectId"]
        content_id = info["data"]["contentId"]
        resp = self._sal.project.project_content_get(project_id, content_id)
        return ProjectContent(resp, project_id, self._sal)

    def status(self):
        """
        Returns the upload status as an enumeration.

        Returns:

            upload_status --
                The AsyncOperationStatus enum. The status can have the enum values
                AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
                AsyncOperationStatus.ERROR

        Example::

            project.upload_content('path/to/model.mo').status()
        """
        return AsyncOperationStatus(self._info()["status"])
