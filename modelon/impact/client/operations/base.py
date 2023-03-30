from __future__ import annotations
import enum
import time
import logging

from abc import abstractmethod
from typing import Any, Optional, TypeVar, Protocol, Generic
from modelon.impact.client import exceptions

logger = logging.getLogger(__name__)
Entity = TypeVar("Entity")


class EntityFromOperation(Protocol[Entity]):
    def __call__(self, operation: BaseOperation[Entity], **kwargs: Any) -> Entity:
        ...


@enum.unique
class Status(enum.Enum):
    """Class representing an enumeration for the possible operation states."""

    PENDING = "pending"
    RUNNING = "running"
    STOPPING = "stopping"
    CANCELLED = "cancelled"
    DONE = "done"


@enum.unique
class AsyncOperationStatus(enum.Enum):
    """Defines all states for import."""

    RUNNING = 'running'
    READY = 'ready'
    ERROR = 'error'

    def done(self) -> bool:
        return self in [AsyncOperationStatus.READY, AsyncOperationStatus.ERROR]


class BaseOperation(Generic[Entity]):
    """Abstract base operation class."""

    def __init__(self, create_entity: EntityFromOperation):
        self._create_entity = create_entity

    @abstractmethod
    def data(self) -> Entity:
        """Returns the Entity class."""
        pass

    @abstractmethod
    def status(self) -> Any:
        """Returns the operation status as an enumeration."""
        pass

    @abstractmethod
    def cancel(self) -> Any:
        """Terminates the operation."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the operation."""
        pass

    @abstractmethod
    def wait(self, timeout: Optional[float]) -> Entity:
        """Waits for the operation to finish."""
        pass


class AsyncOperation(BaseOperation[Entity]):
    """File operation class containing base functionality."""

    def wait(self, timeout: Optional[float] = None) -> Entity:
        """Waits until the operation completes. Returns the operation class
        instance if operation completes.

        Args:
            timeout: Time to wait in seconds for achieving the status. By default
                the timeout is set to 'None', which signifies an infinite time
                to wait until the status is achieved.

        Returns:

            Entity class instance if operation completes.

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

    def cancel(self) -> None:
        raise NotImplementedError('Cancel is not supported for this operation')


class ExecutionOperation(BaseOperation[Entity]):
    """Execution operation class containing base functionality."""

    def is_complete(self) -> bool:
        """Returns True if the operation has completed.

        Returns:
            True, if operation has completed.False, if operation has
            not completed.

        Example::

           model.compile(options).is_complete()
           workspace.execute(definition).is_complete()

        """
        return self.status() == Status.DONE

    def wait(
        self, timeout: Optional[float] = None, status: Status = Status.DONE
    ) -> Entity:
        """Waits until the operation achieves the set status. Returns the
        operation class instance if the set status is achieved.

        Args:
            timeout: Time to wait in seconds for achieving the status. By default
                the timeout is set to 'None', which signifies an infinite time
                to wait until the status is achieved.

            status:
                Operation status to be achieved.
                Default: Status.DONE

        Returns:

            Entity class instance if the set status is achieved.

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
