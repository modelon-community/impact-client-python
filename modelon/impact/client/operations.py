import time
import logging
import modelon.impact.client.entities as entities

from abc import ABC, abstractmethod
from modelon.impact.client import exceptions
from enum import Enum

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Status(Enum):
    """
    Class representing an enumeration for the possible
    operation states.
    """

    PENDING = "pending"
    RUNNING = "running"
    STOPPING = "stopping"
    CANCELLED = "cancelled"
    DONE = "done"


class Operation(ABC):
    """
    Abstract operation class containing base functionality.
    """

    @abstractmethod
    def data(self):
        """
        Returns the operation class.
        """
        pass

    @abstractmethod
    def status(self):
        """
        Returns the operation status as an enumeration.
        """
        pass

    @abstractmethod
    def cancel(self):
        """
        Terminates the operation.
        """
        pass

    def is_complete(self):
        """
        Returns True if the operation has completed.

        Returns::

            True -> If operation has completed.
            False -> If operation has not completed.

        Example::

           model.compile(options).is_complete()
           workspace.execute(specification).is_complete()
        """
        return self.status() == Status.DONE

    def wait(self, timeout=None, status=Status.DONE):
        """Waits until the operation achieves the set status.
        Returns the operation class instance if the set status is achieved.

        Parameters::

            timeout --
                Time to wait in seconds for achieving the status. By default 
                the timeout is set to 'None', which signifies an infinity time 
                to wait until the status is achieved.

            status --
                Operation status to be achieved.
                Default: Status.DONE

        Returns::

            Operation class instance if the set status is achieved.

        Raises::

            OperationTimeOutError if time exceeds set timeout.

        Example::

           model.compile(compile_options).wait(timeout = 120, status = Status.CANCELLED)
           workspace.execute(experiment_definition).wait(timeout = 120)
        """
        start_t = time.time()
        while True:
            logger.info(f"Operation in progress! Status : {self.status().name}")
            time.sleep(0.5)
            if self.status() == status:
                return self.data()
            current_t = time.time()
            if timeout and current_t - start_t > timeout:
                raise exceptions.OperationTimeOutError(
                    f"Time exceeded the set timeout - {timeout}s! "
                    f"Present status of operation is {self.status().name}!"
                )


class ModelExecutableOperation(Operation):
    """
    An operation class for the modelon.impact.client.entities.ModelExecutable class.
    """

    def __init__(
        self, workspace_id, fmu_id, workspace_service=None, model_exe_service=None,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def __repr__(self):
        return f"Model executable operations for id '{self._fmu_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ModelExecutableOperation) and obj._fmu_id == self._fmu_id

    @property
    def id(self):
        """FMU id"""
        return self._fmu_id

    def data(self):
        """
        Returns a new ModelExecutable class instance.

        Returns::

            model_executable --
                A model_executable class instance.
        """
        return entities.ModelExecutable(
            self._workspace_id, self._fmu_id, self._workspace_sal, self._model_exe_sal,
        )

    def status(self):
        """
        Returns the compilation status as an enumeration.

        Returns::

            status --
                The compilation status enum. The status can have the enum values
                Status.PENDING, Status.RUNNING, Status.STOPPING, Status.CANCELLED
                or Status.DONE

        Example::

            model.compile(options).status()
        """
        return Status(
            self._model_exe_sal.compile_status(self._workspace_id, self._fmu_id)[
                "status"
            ]
        )

    def cancel(self):
        """
        Terminates the compilation process.

        Example::

            model.compile(options).cancel()
        """
        self._model_exe_sal.compile_cancel(self._workspace_id, self._fmu_id)


class ExperimentOperation(Operation):
    """
    An operation class for the modelon.impact.client.entities.Experiment class.
    """

    def __init__(
        self, workspace_id, exp_id, workspace_service=None, exp_service=None,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service

    def __repr__(self):
        return f"Experiment operation for id '{self._exp_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ExperimentOperation) and obj._exp_id == self._exp_id

    @property
    def id(self):
        """Experiment id"""
        return self._exp_id

    def data(self):
        """
        Returns a new Experiment class instance.

        Returns::

            experiment --
                An experiment class instance.
        """
        return entities.Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        )

    def status(self):
        """
        Returns the execution status as an enumeration.

        Returns::

            status --
                The execution status enum. The status can have the enum values
                Status.PENDING, Status.RUNNING, Status.STOPPING, Status.CANCELLED
                or Status.DONE

        Example::

            workspace.execute(specification).status()
        """
        return Status(
            self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]
        )

    def cancel(self):
        """
        Terminates the execution process.

        Example::

            workspace.execute(specification).cancel()
        """
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)
