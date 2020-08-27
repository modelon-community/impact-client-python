import time
import logging
import modelon.impact.client.entities as entities

from abc import ABC, abstractmethod
from modelon.impact.client import exceptions
from enum import Enum

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _assert_is_running(status, operation_name="Operation"):
    if status not in (Status.RUNNING, Status.PENDING):
        raise exceptions.OperationNotCompleteError(
            f"{operation_name} has completed and cannot be cancelled!"
        )


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    STOPPING = "stopping"
    CANCELLED = "cancelled"
    DONE = "done"


class Operation(ABC):
    @abstractmethod
    def data(self):
        pass

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

    def is_complete(self):
        if self.status() in (Status.CANCELLED, Status.STOPPING):
            raise exceptions.OperationFailureError(
                "Operation was cancelled before completion! "
            )
        return self.status() == Status.DONE

    def wait(self, timeout=None, status=Status.DONE):
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
        return self._fmu_id

    def data(self):
        return entities.ModelExecutable(
            self._workspace_id, self._fmu_id, self._workspace_sal, self._model_exe_sal,
        )

    def status(self):
        return Status(
            self._model_exe_sal.compile_status(self._workspace_id, self._fmu_id)[
                "status"
            ]
        )

    def cancel(self):
        _assert_is_running(self.status(), "Compilation")
        self._model_exe_sal.compile_cancel(self._workspace_id, self._fmu_id)


class ExperimentOperation(Operation):
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
        return self._exp_id

    def data(self):
        return entities.Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        )

    def status(self):
        return Status(
            self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]
        )

    def cancel(self):
        _assert_is_running(self.status(), "Simulation")
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)
