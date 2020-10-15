import time
import logging
from modelon.impact.client import entities

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

    @property
    @abstractmethod
    def name(self):
        """
        Name of the operation.
        """
        pass

    def is_complete(self):
        """
        Returns True if the operation has completed.

        Returns:

            True -> If operation has completed.
            False -> If operation has not completed.

        Example::

           model.compile(options).is_complete()
           workspace.execute(definition).is_complete()
        """
        return self.status() == Status.DONE

    def wait(self, timeout=None, status=Status.DONE):
        """Waits until the operation achieves the set status.
        Returns the operation class instance if the set status is achieved.

        Parameters:

            timeout --
                Time to wait in seconds for achieving the status. By default
                the timeout is set to 'None', which signifies an infinite time
                to wait until the status is achieved.

            status --
                Operation status to be achieved.
                Default: Status.DONE

        Returns:

            Operation class instance if the set status is achieved.

        Raises:

            OperationTimeOutError if time exceeds set timeout.

        Example::

           model.compile(compile_options).wait(
               timeout = 120,
               status = Status.CANCELLED
           )
           workspace.execute(experiment_definition).wait(timeout = 120)
        """
        start_t = time.time()
        while True:
            logger.info(f"{self.name} in progress! Status : {self.status().name}")
            time.sleep(0.5)
            if self.status() == status:
                logger.info(f"{self.name} completed! Status : {self.status().name}")
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

    @property
    def name(self):
        """Return the name of operation"""
        return "Compilation"

    def data(self):
        """
        Returns a new ModelExecutable class instance.

        Returns:

            model_executable --
                A model_executable class instance.
        """
        return entities.ModelExecutable(
            self._workspace_id, self._fmu_id, self._workspace_sal, self._model_exe_sal,
        )

    def status(self):
        """
        Returns the compilation status as an enumeration.

        Returns:

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


class CachedModelExecutableOperation(Operation):
    """
    An operation class for a cached modelon.impact.client.entities.ModelExecutable
    class.
    """

    def __init__(
        self,
        workspace_id,
        fmu_id,
        workspace_service=None,
        model_exe_service=None,
        info=None,
        modifiers=None,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_service = workspace_service
        self._model_exe_sal = model_exe_service
        self._info = info
        self._modifiers = modifiers

    def __repr__(self):
        return f"Cached model executable operations for id '{self._fmu_id}'"

    def __eq__(self, obj):
        return (
            isinstance(obj, CachedModelExecutableOperation)
            and obj._fmu_id == self._fmu_id
        )

    @property
    def id(self):
        """FMU id"""
        return self._fmu_id

    @property
    def name(self):
        """Return the name of operation"""
        return "Looking for cached FMU"

    def data(self):
        """
        Returns a new ModelExecutable class instance.

        Returns:

            model_executable --
                A model_executable class instance.
        """
        return entities.ModelExecutable(
            self._workspace_id,
            self._fmu_id,
            self._workspace_service,
            self._model_exe_sal,
            self._info,
            self._modifiers,
        )

    def status(self):
        """
        Returns the compilation status as an enumeration.

        Returns:

            status --
                The compilation status enum. The status has the enum value
                Status.DONE as a cached FMU is only possible for a
                successfully finished compilation.

        Example::

            model.compile(options).status()
        """
        return Status.DONE

    def cancel(self):
        raise NotImplementedError(
            "Cancel is not supported for CachedModelExecutableOperation class"
        )

    def wait(self, timeout=None, status=Status.DONE):
        """Waits until the operation achieves the set status.
        Returns the operation class instance if the set status is achieved.

        Parameters:

            timeout --
                Time to wait in seconds for achieving the status.This argument is
                not accounted for the CachedModelExecutableOperation class as the
                model has a successfully compiled status(Status.DONE) in this class.

            status --
                Operation status to be achieved. The only possible status for the
                CachedModelExecutableOperation class is Status.DONE as cached FMU
                is only avaiable for a successfully compiled model.

        Returns:

            Operation class instance if the set status is achieved.

        Raises:

            OperationTimeOutError if operation status is not set as Status.DONE.

        Example::

           model.compile(compile_options).wait()
        """

        if self.status() != status:
            raise exceptions.OperationTimeOutError(
                f"The operation '{self.name}' has the status '{self.status().name}'"
                f", it will never get the status '{status.name}'!"
            )

        logger.info("Cached FMU found! Using the cached FMU!")
        return self.data()


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
        return entities.Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
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
        return Status(
            self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]
        )

    def cancel(self):
        """
        Terminates the execution process.

        Example::

            workspace.execute(definition).cancel()
        """
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)
