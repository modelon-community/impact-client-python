from modelon.impact.client.operations import base
import modelon.impact.client.entities.experiment
from modelon.impact.client.sal.service import Service


class ExperimentOperation(base.ExecutionOperation):
    """
    An operation class for the modelon.impact.client.entities.experiment.Experiment
    class.
    """

    def __init__(self, workspace_id: str, exp_id: str, service: Service):
        super().__init__()
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._sal = service

    def __repr__(self):
        return f"Experiment operation for id '{self._exp_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ExperimentOperation) and obj._exp_id == self._exp_id

    @property
    def id(self):
        """Experiment id"""
        return self._exp_id

    @property
    def name(self):
        """Return the name of operation"""
        return "Execution"

    def data(self):
        """
        Returns a new Experiment class instance.

        Returns:

            experiment --
                An experiment class instance.
        """
        return modelon.impact.client.entities.experiment.Experiment(
            self._workspace_id, self._exp_id, self._sal,
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

            workspace.execute(definition).status()
        """
        return base.Status(
            self._sal.experiment.execute_status(self._workspace_id, self._exp_id)[
                "status"
            ]
        )

    def cancel(self):
        """
        Terminates the execution process.

        Example::

            workspace.execute(definition).cancel()
        """
        self._sal.experiment.execute_cancel(self._workspace_id, self._exp_id)
