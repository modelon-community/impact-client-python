import enum
import time
import logging

from abc import ABC, abstractmethod
from typing import Optional
from modelon.impact.client import exceptions

logger = logging.getLogger(__name__)


@enum.unique
class Status(enum.Enum):
    """
    Class representing an enumeration for the possible
    operation states.
    """

    PENDING = "pending"
    RUNNING = "running"
    STOPPING = "stopping"
    CANCELLED = "cancelled"
    DONE = "done"


@enum.unique
class AsyncOperationStatus(enum.Enum):
    """
    Defines all states for import
    """

    RUNNING = 'running'
    READY = 'ready'
    ERROR = 'error'

    def done(self):
        return self in [AsyncOperationStatus.READY, AsyncOperationStatus.ERROR]


class BaseOperation(ABC):
    """
    Abstract base operation class.
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
    def name(self) -> str:
        """
        Name of the operation.
        """
        pass

    @abstractmethod
    def wait(self, timeout):
        """
        Waits for the operation to finish.
        """
        pass


class AsyncOperation(BaseOperation):
    """
    File operation class containing base functionality.
    """

    def wait(self, timeout: Optional[float] = None):
        """Waits until the operation completes.
        Returns the operation class instance if operation completes.

        Parameters:

            timeout --
                Time to wait in seconds for achieving the status. By default
                the timeout is set to 'None', which signifies an infinite time
                to wait until the status is achieved.

        Returns:

            Operation class instance if operation completes.

        Raises:

            OperationTimeOutError if time exceeds set timeout.

        Example::

            workspace.upload_result('C:/A.mat').wait(timeout = 120)
        """
        start_t = time.time()
        while True:
            logger.info(f"{self.name} in progress! Status : {self.status().name}")
            if self.status().done():
                logger.info(f"{self.name} completed! Status : {self.status().name}")
                return self.data()

            current_t = time.time()
            if timeout and current_t - start_t > timeout:
                raise exceptions.OperationTimeOutError(
                    f"Time exceeded the set timeout - {timeout}s! "
                    f"Present status of operation is {self.status().name}!"
                )

            time.sleep(0.5)


class ExecutionOperation(BaseOperation):
    """
    Execution operation class containing base functionality.
    """

    def is_complete(self) -> bool:
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

    def wait(self, timeout: Optional[float] = None, status: Status = Status.DONE):
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
            if self.status() == status:
                logger.info(f"{self.name} completed! Status : {self.status().name}")
                return self.data()

            current_t = time.time()
            if timeout and current_t - start_t > timeout:
                raise exceptions.OperationTimeOutError(
                    f"Time exceeded the set timeout - {timeout}s! "
                    f"Present status of operation is {self.status().name}!"
                )

            time.sleep(0.5)
