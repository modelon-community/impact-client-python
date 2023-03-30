from __future__ import annotations
from typing import TYPE_CHECKING, Type
from modelon.impact.client.operations import base

if TYPE_CHECKING:
    from modelon.impact.client.entities.experiment import Experiment
    from modelon.impact.client.sal.service import Service


class ExperimentOperation(base.ExecutionOperation):
    """An operation class for the
    modelon.impact.client.entities.experiment.Experiment class."""

    def __init__(
        self, workspace_id: str, exp_id: str, service: Service, entity: Type[Experiment]
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._sal = service
        self._entity = entity

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

    def data(self) -> Experiment:
        """Returns a new Experiment class instance.

        Returns:

            experiment:
                An experiment class instance.

        """
        return self._entity(self._workspace_id, self._exp_id, self._sal)

    def status(self) -> base.Status:
        """Returns the execution status as an enumeration.

        Returns:

            status:
                The execution status enum. The status can have the enum values
                Status.PENDING, Status.RUNNING, Status.STOPPING, Status.CANCELLED
                or Status.DONE

        Example::

            workspace.execute(definition).status()

        """
        return base.Status(
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
