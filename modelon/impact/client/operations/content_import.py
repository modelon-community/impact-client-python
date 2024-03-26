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


class ContentImportOperation(AsyncOperation[Entity]):
    """An operation class for the ProjectContent class."""

    def __init__(
        self, location: str, service: Service, create_entity: EntityFromOperation
    ):
        super().__init__(create_entity)
        self._location = location
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Content import operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, ContentImportOperation) and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Content import id."""
        return self._location.split("/")[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Project content import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> Entity:
        """Returns a new ProjectContent class instance.

        Returns:
            A ProjectContent class instance.

        """
        info = self._info()
        if info["status"] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalContentImport(
                f"Content import failed! Cause: {info['error'].get('message')}"
            )
        project_id = self._location.split("/")[-3]
        content_id = info["data"]["contentId"]
        resp = self._sal.project.project_content_get(project_id, content_id)
        return self._create_entity(self, content=resp, project_id=project_id)

    @property
    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            project.import_content('path/to/model.mo').status

        """
        return AsyncOperationStatus(self._info()["status"])
