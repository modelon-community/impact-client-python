from __future__ import annotations

from typing import TYPE_CHECKING

from modelon.impact.client.operations.base import Entity, ExecutionOperation, Status

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import EntityFromOperation
    from modelon.impact.client.sal.service import Service


class ExperimentOperation(ExecutionOperation[Entity]):
    """An operation class for the Experiment class."""

    def __init__(
        self,
        workspace_id: str,
        exp_id: str,
        service: Service,
        create_entity: EntityFromOperation,
    ):
        super().__init__(create_entity)
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Experiment operation for id '{self._exp_id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, ExperimentOperation) and obj._exp_id == self._exp_id

    @property
    def id(self) -> str:
        """Experiment id."""
        return self._exp_id

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Execution"

    def data(self) -> Entity:
        """Returns a new Experiment class instance.

        Returns:
            An experiment class instance.

        """
        return self._create_entity(
            self, workspace_id=self._workspace_id, exp_id=self._exp_id
        )

    @property
    def status(self) -> Status:
        """Returns the execution status as an enumeration.

        Returns:
            The execution status enum. The status can have the enum values
            Status.PENDING, Status.RUNNING, Status.STOPPING, Status.CANCELLED
            or Status.DONE

        Example::

            workspace.execute(definition).status

        """
        return Status(
            self._sal.experiment.execute_status(self._workspace_id, self._exp_id)[
                "status"
            ]
        )

    def cancel(self) -> None:
        """Terminates the execution process.

        Example::

            workspace.execute(definition).cancel()

        """
        self._sal.experiment.execute_cancel(self._workspace_id, self._exp_id)
