from __future__ import annotations
from typing import TYPE_CHECKING

from modelon.impact.client.operations.base import ExecutionOperation, Status, Entity

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service
    from modelon.impact.client.operations.base import EntityFromOperation


class CaseOperation(ExecutionOperation[Entity]):
    """An operation class for the modelon.impact.client.entities.Case class."""

    def __init__(
        self,
        workspace_id: str,
        exp_id: str,
        case_id: str,
        service: Service,
        create_entity: EntityFromOperation,
    ):
        super().__init__(create_entity)
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._case_id = case_id
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Case operation for id '{self._case_id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, CaseOperation) and obj._case_id == self._case_id

    @property
    def id(self) -> str:
        """Case id."""
        return self._case_id

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Execution"

    def data(self) -> Entity:
        """Returns a new Case class instance.

        Returns:

            experiment:
                An Case class instance.

        """
        case_data = self._sal.experiment.case_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        return self._create_entity(
            self,
            case_id=self._case_id,
            workspace_id=self._workspace_id,
            exp_id=self._exp_id,
            info=case_data,
        )

    def status(self) -> Status:
        """Returns the execution status as an enumeration.

        Returns:

            status:
                The execution status enum. The status can have the enum values
                Status.PENDING, Status.RUNNING, Status.STOPPING, Status.CANCELLED
                or Status.DONE

        Example::

            case.execute().status()

        """
        return Status(
            self._sal.experiment.execute_status(self._workspace_id, self._exp_id)[
                "status"
            ]
        )

    def cancel(self) -> None:
        """Terminates the execution process.

        Example::

            case.execute().cancel()

        """
        self._sal.experiment.execute_cancel(self._workspace_id, self._exp_id)
