from modelon.impact.client.entities import case
from modelon.impact.client.operations.base import ExecutionOperation, Status
from modelon.impact.client.sal.service import Service


class CaseOperation(ExecutionOperation):
    """
    An operation class for the modelon.impact.client.entities.Case class.
    """

    def __init__(self, workspace_id, exp_id, case_id, service: Service):
        super().__init__()
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._case_id = case_id
        self._sal = service

    def __repr__(self):
        return f"Case operation for id '{self._case_id}'"

    def __eq__(self, obj):
        return isinstance(obj, CaseOperation) and obj._case_id == self._case_id

    @property
    def id(self):
        """Case id"""
        return self._case_id

    @property
    def name(self):
        """Return the name of operation"""
        return "Execution"

    def data(self):
        """
        Returns a new Case class instance.

        Returns:

            experiment --
                An Case class instance.
        """
        case_data = self._sal.experiment.case_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        return case.Case(
            self._case_id, self._workspace_id, self._exp_id, self._sal, case_data,
        )

    def status(self):
        """
        Returns the execution status as an enumeration.

        Returns:

            status --
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

    def cancel(self):
        """
        Terminates the execution process.

        Example::

            case.execute().cancel()
        """
        self._sal.experiment.execute_cancel(self._workspace_id, self._exp_id)
