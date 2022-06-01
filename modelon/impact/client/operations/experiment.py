from modelon.impact.client.operations import base
import modelon.impact.client.entities.experiment
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.sal.model_executable import ModelExecutableService
from modelon.impact.client.sal.experiment import ExperimentService


class ExperimentOperation(base.ExecutionOperation):
    """
    An operation class for the modelon.impact.client.entities.Experiment class.
    """

    def __init__(
        self,
        workspace_id: str,
        exp_id: str,
        workspace_service: WorkspaceService,
        model_exe_service: ModelExecutableService,
        exp_service: ExperimentService,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service
        self._exp_sal = exp_service

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
            self._workspace_id,
            self._exp_id,
            self._workspace_sal,
            self._model_exe_sal,
            self._exp_sal,
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
            self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]
        )

    def cancel(self):
        """
        Terminates the execution process.

        Example::

            workspace.execute(definition).cancel()
        """
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)
