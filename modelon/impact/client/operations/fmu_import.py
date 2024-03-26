from __future__ import annotations

import logging
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

logger = logging.getLogger(__name__)


class FMUImportOperation(AsyncOperation[Entity]):
    """An operation class for the Model class."""

    def __init__(
        self,
        location: str,
        workspace_id: str,
        project_id: str,
        service: Service,
        create_entity: EntityFromOperation,
    ):
        super().__init__(create_entity)
        self._location = location
        self._workspace_id = workspace_id
        self._project_id = project_id
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"FMU import operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, FMUImportOperation) and obj._location == self._location

    @property
    def id(self) -> str:
        """FMU import id."""
        return self._location.split("/")[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Model import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> Entity:
        """Returns a new Model class instance.

        Returns:
            A Model class instance.

        """
        info = self._info()
        if info["status"] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalFMUImport(
                f"FMU import failed! Cause: {info['error'].get('message')}"
            )
        if info.get("importWarnings"):
            logger.warning(f"Import Warnings: {'. '.join(info['importWarnings'])}")

        class_name = info["data"]["fmuClassPath"]
        return self._create_entity(
            self,
            class_name=class_name,
            workspace_id=self._workspace_id,
            project_id=self._project_id,
        )

    @property
    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            model.import_fmu('test.fmu').status

        """
        return AsyncOperationStatus(self._info()["status"])
