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


class ModelExecutable(Operation):
    def __init__(
        self, workspace_id, fmu_id, workspace_service=None, model_exe_service=None,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service

    def __repr__(self):
        return f"FMU with id '{self._fmu_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ModelExecutable) and obj._fmu_id == self._fmu_id

    def data(self):
        return ModelExecutable(
            self._workspace_id, self._fmu_id, self._workspace_sal, self._model_exe_sal,
        )

    def status(self):
        return self._model_exe_sal.compile_status(self._workspace_id, self._fmu_id)[
            "status"
        ]

    def cancel(self):
        self._exp_sal.compile_cancel(self._workspace_id, self._fmu_id)

    @property
    def id(self):
        return self._fmu_id

    @property
    def settable_parameters(self):
        return self._model_exe_sal.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )

    @property
    def info(self):
        return self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

    @property
    def log(self):
        return self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id)

    @property
    def metadata(self):
        return self._workspace_sal.ss_fmu_metadata_get(self._workspace_id, self._fmu_id)

    def is_successful(self):
        return True if self.info["run_info"]['status'] == 'successful' else False


class Experiment(Operation):
    def __init__(
        self, workspace_id, exp_id=None, workspace_service=None, exp_service=None,
    ):
        super().__init__()
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service

    def __repr__(self):
        return f"Experiment with id '{self._exp_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Experiment) and obj._exp_id == self._exp_id

    def data(self):
        return entities.Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        )

    def status(self):
        return self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]

    def cancel(self):
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)

    @property
    def id(self):
        return self._exp_id

    @property
    def variables(self):
        return self._exp_sal.result_variables_get(self._workspace_id, self._exp_id)

    @property
    def info(self):
        return self._workspace_sal.experiment_get(self._workspace_id, self._exp_id)

    def execute(self):
        return Experiment(
            self._workspace_id,
            self._workspace_sal.experiment_execute(self._workspace_id, self._exp_id),
            self._workspace_sal,
            self._exp_sal,
        )

    def is_successful(self):
        if (
            self.info["run_info"]['status'] == 'done'
            and self.info["run_info"]["cancelled"] == 0
            and self.info["run_info"]["failed"] == 0
        ):
            return True
        else:
            return False

    def get_trajectories(self, variables):
        return self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, variables
        )
