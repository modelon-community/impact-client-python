from __future__ import annotations
import logging
from typing import Dict, Optional, Any, TYPE_CHECKING

from modelon.impact.client.operations.base import ExecutionOperation, Status, Entity
from modelon.impact.client import exceptions

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service
    from modelon.impact.client.operations.base import EntityFromOperation

logger = logging.getLogger(__name__)


class CachedModelExecutableOperation(ExecutionOperation[Entity]):
    """An operation class for a cached ModelExecutable class."""

    def __init__(
        self,
        workspace_id: str,
        fmu_id: str,
        service: Service,
        create_entity: EntityFromOperation,
        info: Optional[Dict[str, Any]] = None,
        modifiers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(create_entity)
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._sal = service
        self._info = info
        self._modifiers = modifiers
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Cached model executable operations for id '{self._fmu_id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, CachedModelExecutableOperation)
            and obj._fmu_id == self._fmu_id
        )

    @property
    def id(self) -> str:
        """FMU id."""
        return self._fmu_id

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Looking for cached FMU"

    def data(self) -> Entity:
        """Returns a new ModelExecutable class instance.

        Returns:
            A model_executable class instance.

        """
        return self._create_entity(
            self,
            workspace_id=self._workspace_id,
            fmu_id=self._fmu_id,
            info=self._info,
            modifiers=self._modifiers,
        )

    def status(self) -> Status:
        """Returns the compilation status as an enumeration.

        Returns:
            The compilation status enum. The status has the enum value
            Status.DONE as a cached FMU is only possible for a
            successfully finished compilation.

        Example::

            model.compile(options).status()

        """
        return Status.DONE

    def cancel(self) -> None:
        raise NotImplementedError(
            "Cancel is not supported for CachedModelExecutableOperation class"
        )

    def wait(
        self, timeout: Optional[float] = None, status: Status = Status.DONE
    ) -> Entity:
        """Waits until the operation achieves the set status. Returns the
        operation class instance if the set status is achieved.

        Args:
            timeout: Time to wait in seconds for achieving the status.This argument is
                not accounted for the CachedModelExecutableOperation class as the
                model has a successfully compiled status(Status.DONE) in this class.

            status:
                Operation status to be achieved. The only possible status for the
                CachedModelExecutableOperation class is Status.DONE as cached FMU
                is only available for a successfully compiled model.

        Returns:

            Entity class instance if the set status is achieved.

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


class ModelExecutableOperation(ExecutionOperation[Entity]):
    """An operation class for the ModelExecutable class."""

    def __init__(
        self,
        workspace_id: str,
        fmu_id: str,
        service: Service,
        create_entity: EntityFromOperation,
    ):
        super().__init__(create_entity)
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._sal = service
        self._create_entity = create_entity

    def __repr__(self) -> str:
        return f"Model executable operations for id '{self._fmu_id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, ModelExecutableOperation) and obj._fmu_id == self._fmu_id

    @property
    def id(self) -> str:
        """FMU id."""
        return self._fmu_id

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return "Compilation"

    def data(self) -> Entity:
        """Returns a new ModelExecutable class instance.

        Returns:
            A ModelExecutable class instance.

        """
        return self._create_entity(
            self, workspace_id=self._workspace_id, fmu_id=self._fmu_id
        )

    def status(self) -> Status:
        """Returns the compilation status as an enumeration.

        Returns:
            The compilation status enum. The status can have the enum values
            Status.PENDING, Status.RUNNING, Status.STOPPING, Status.CANCELLED
            or Status.DONE

        Example::

            model.compile(options).status()

        """
        return Status(
            self._sal.model_executable.compile_status(self._workspace_id, self._fmu_id)[
                "status"
            ]
        )

    def cancel(self) -> None:
        """Terminates the compilation process.

        Example::

            model.compile(options).cancel()

        """
        self._sal.model_executable.compile_cancel(self._workspace_id, self._fmu_id)
