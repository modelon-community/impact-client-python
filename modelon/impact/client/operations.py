import time
from abc import ABC, abstractmethod
from enum import Enum
import modelon.impact.client.entities as entities
import modelon.impact.client.exceptions as exceptions


class Status(Enum):
    CANCELLED = 'cancelled'
    RUNNING = 'running'
    PENDING = 'pending'
    STOPPING = 'stopping'
    DONE = 'done'


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

    def wait(self, timeout=None, status=Status.DONE):
        start_t = time.time()
        while True:
            time.sleep(0.5)
            if self.status() == status.value:
                return self.data()
            current_t = time.time()
            if timeout and current_t - start_t > timeout:
                raise exceptions.OperationTimeOutError(
                    f"Time exceeded the set timeout - {timeout}s!"
                )

    def is_complete(self):
        return True if self.status() == "done" else False


class ModelExecutbleOperation(Operation):
    def __init__(
        self, workspace_id, fmu_id, workspace_service=None, model_exe_service=None,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def data(self):
        return entities.ModelExecutable(
            self._workspace_id, self._fmu_id, self._workspace_sal, self._model_exe_sal,
        )

    def status(self):
        return self._model_exe_sal.compile_status(self._workspace_id, self._fmu_id)[
            "status"
        ]

    def cancel(self):
        self._exp_sal.compile_cancel(self._workspace_id, self._fmu_id)


class ExperimentOperation(Operation):
    def __init__(
        self, workspace_id, exp_id=None, workspace_service=None, exp_service=None,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service

    def data(self):
        return entities.Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        )

    def status(self):
        return self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]

    def cancel(self):
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)
