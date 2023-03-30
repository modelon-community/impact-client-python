from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING, Type

from modelon.impact.client.operations.base import AsyncOperation, AsyncOperationStatus
from modelon.impact.client import exceptions

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service
    from modelon.impact.client.entities.content import ProjectContent


class ContentImportOperation(AsyncOperation):
    """An operation class for the
    modelon.impact.client.entities.project.ProjectContent class."""

    def __init__(self, location: str, service: Service, entity: Type[ProjectContent]):
        super().__init__()
        self._location = location
        self._sal = service
        self._entity = entity

    def __repr__(self) -> str:
        return f"Content import operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, ContentImportOperation) and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Content import id."""
        return self._location.split('/')[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Content import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> ProjectContent:
        """Returns a new Workspace class instance.

        Returns:

            workspace:
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
        return self._entity(resp, project_id, self._sal)

    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:

            upload_status:
                The AsyncOperationStatus enum. The status can have the enum values
                AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
                AsyncOperationStatus.ERROR

        Example::

            project.upload_content('path/to/model.mo').status()

        """
        return AsyncOperationStatus(self._info()["status"])
