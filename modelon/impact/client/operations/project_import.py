from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations.base import (
    AsyncOperation,
    AsyncOperationStatus,
    Entity,
)
from modelon.impact.client import exceptions

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import EntityFromOperation


class ProjectImportOperation(AsyncOperation[Entity]):
    """An import operation class for the
    modelon.impact.client.entities.project.Project class."""

    def __init__(
        self, location: str, service: Service, create_entity: EntityFromOperation
    ):
        super().__init__(create_entity)
        self._location = location
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Project import operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, ProjectImportOperation) and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Project import id."""
        return self._location.split('/')[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Project import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> Entity:
        """Returns a new Project class instance.

        Returns:

            project:
                A Project class instance.

        """
        info = self._info()
        if info['status'] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalProjectImport(
                f"Project import failed! Cause: {info['error'].get('message')}"
            )
        project_id = info["data"]["projectId"]
        resp = self._sal.project.project_get(project_id, False)
        return self._create_entity(
            self,
            project_id=resp["id"],
            project_definition=resp["definition"],
            project_type=resp["projectType"],
        )

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
