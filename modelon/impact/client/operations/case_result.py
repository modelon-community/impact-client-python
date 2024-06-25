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


class CaseResultImportOperation(AsyncOperation[Entity]):
    """An operation class for the Result class."""

    def __init__(
        self,
        location: str,
        workspace_id: str,
        exp_id: str,
        case_id: str,
        service: Service,
        create_entity: EntityFromOperation,
    ):
        super().__init__(create_entity)
        self._location = location
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._case_id = case_id
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Case result import operations for id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, CaseResultImportOperation)
            and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Case result import id."""
        return self._location.split("/")[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Case result import"

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> Entity:
        """Returns a new Result class instance.

        Returns:
            A Result class instance.

        """
        info = self._info()
        if info["status"] == AsyncOperationStatus.ERROR.value:
            raise exceptions.IllegalCaseResultImport(
                f"Result import failed! Cause: {info['error'].get('message')}"
            )
        variables = self._sal.experiment.case_result_variables_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        return self._create_entity(
            self,
            variables=variables,
            workspace_id=self._workspace_id,
            exp_id=self._exp_id,
            case_id=self._case_id,
        )

    @property
    def status(self) -> AsyncOperationStatus:
        """Returns the upload status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            case.import_result('path/to/result.csv').status

        """
        return AsyncOperationStatus(self._info()["status"])
