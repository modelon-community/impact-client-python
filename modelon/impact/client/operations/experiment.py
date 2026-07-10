from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List

from modelon.impact.client.operations.base import Entity, ExecutionOperation, Status

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import EntityFromOperation
    from modelon.impact.client.sal.service import Service


@dataclass
class CaseExecutionProgress:
    """Progress information for a single case of a running execution."""

    message: str
    percentage: float
    done: bool
    stage: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CaseExecutionProgress:
        return cls(
            message=data.get("message", ""),
            percentage=data.get("percentage", 0.0),
            done=data.get("done", False),
            stage=data.get("stage", ""),
        )


@dataclass
class ExecutionProgress:
    """Detailed progress information for an ongoing experiment execution."""

    status: Status
    finished_executions: int
    total_executions: int
    case_progresses: List[CaseExecutionProgress] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutionProgress:
        return cls(
            status=Status(data["status"]),
            finished_executions=data.get("finished_executions", 0),
            total_executions=data.get("total_executions", 0),
            case_progresses=[
                CaseExecutionProgress.from_dict(p) for p in data.get("progresses", [])
            ],
        )


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

    @property
    def execution_progress(self) -> ExecutionProgress:
        """Returns detailed progress information for the ongoing execution.

        In addition to the execution status, this includes the number of finished
        and total case executions, and per-case progress (message, percentage
        complete, done flag and current stage).

        Returns:
            An ExecutionProgress class object.

        Example::

            progress = workspace.execute(definition).execution_progress
            progress.finished_executions
            progress.total_executions
            progress.case_progresses[0].percentage

        """
        data = self._sal.experiment.execute_status(self._workspace_id, self._exp_id)
        return ExecutionProgress.from_dict(data)

    def cancel(self) -> None:
        """Terminates the execution process.

        Example::

            workspace.execute(definition).cancel()

        """
        self._sal.experiment.execute_cancel(self._workspace_id, self._exp_id)
