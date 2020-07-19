import time
import logging
from abc import ABC, abstractmethod
from enum import Enum
import modelon.impact.client.exceptions as exceptions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _assert_successful_operation(ops, operation_name="Operation"):
    if ops.is_successful():
        return
    else:
        raise exceptions.OperationFailureError(
            f"{operation_name} failed! Cause :- '{ops.log()}'."
            "Try increasing the log_level for more logging!"
        )


def _assert_is_running(status, operation_name="Operation"):
    if status == "running" or status == 'pending' or status == 'not_started':
        return
    else:
        raise exceptions.OperationFailureError(
            f"{operation_name} has completed and cannot be cancelled!"
        )


def _wait_to_complete(ops, operation_name="Operation"):
    while (
        ops.info["run_info"]['status'] == "running"
        or ops.info["run_info"]['status'] == 'pending'
        or ops.info["run_info"]['status'] == 'not_started'
    ):
        time.sleep(0.5)
        logging.info(f"{operation_name} in progress! Status : {ops.status()}")
    if ops.status() == "cancelled" or ops.status() == "stopping":
        raise exceptions.OperationFailureError(
            f"{operation_name} was cancelled before completion! "
            f"Log file generated for cancelled {operation_name} is empty!"
        )


class Status(Enum):
    NOTSTARTED = 1
    PENDING = 2
    RUNNING = 3
    DONE = 4
    STOPPING = 5
    CANCELLED = 6


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

    @abstractmethod
    def is_successful(self):
        pass

    @abstractmethod
    def log(self):
        pass

    def is_complete(self):
        return True if self.status() == "done" else False

    def wait(self, timeout=None, status=Status.DONE):
        start_t = time.time()
        while True:
            time.sleep(0.5)
            if not self.is_successful() and self.is_complete():
                raise exceptions.OperationFailureError(
                    f"Operation failed! Cause :- '{self.log()}'."
                    "Try setting a higher log level for more info!"
                )
            if self.status() == status.name.lower():
                return self.data()
            if Status[self.status().upper()].value > status.value:
                raise exceptions.OperationFailureError(
                    "Set status could not be reached."
                    f"Present status of operation is {self.status()}!"
                )
            current_t = time.time()
            if timeout and current_t - start_t > timeout:
                raise exceptions.OperationTimeOutError(
                    f"Time exceeded the set timeout - {timeout}s!"
                )
            logging.info(f"Operation in progress! Status : {self.status()}")


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
        _assert_is_running(self.status(), "Compilation")
        self._model_exe_sal.compile_cancel(self._workspace_id, self._fmu_id)

    def is_successful(self):
        _wait_to_complete(
            ModelExecutable(
                self._workspace_id,
                self._fmu_id,
                self._workspace_sal,
                self._model_exe_sal,
            ),
            "Compilation",
        )
        return (
            True
            if self.info["run_info"]['status'] == 'successful' and self.is_complete()
            else False
        )

    def log(self):
        _wait_to_complete(
            ModelExecutable(
                self._workspace_id,
                self._fmu_id,
                self._workspace_sal,
                self._model_exe_sal,
            ),
            "Compilation",
        )
        log = self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id)
        if log:
            return log
        else:
            raise exceptions.EmptyLogError(
                "Empty log file! Try to increase the log level for more logging!"
            )

    @property
    def id(self):
        return self._fmu_id

    @property
    def settable_parameters(self):
        _assert_successful_operation(
            ModelExecutable(
                self._workspace_id,
                self._fmu_id,
                self._workspace_sal,
                self._model_exe_sal,
            ),
            "Compilation",
        )
        return self._model_exe_sal.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )

    @property
    def info(self):
        return self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

    @property
    def metadata(self):
        _assert_successful_operation(
            ModelExecutable(
                self._workspace_id,
                self._fmu_id,
                self._workspace_sal,
                self._model_exe_sal,
            ),
            "Compilation",
        )
        return self._workspace_sal.ss_fmu_metadata_get(self._workspace_id, self._fmu_id)


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
        return Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        )

    def status(self):
        return self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]

    def cancel(self):
        _assert_is_running(self.status(), "Simulation")
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)

    def is_successful(self):
        _wait_to_complete(
            Experiment(
                self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
            ),
            "Simulation",
        )
        if (
            self.info["run_info"]['status'] == 'done'
            and self.info["run_info"]["cancelled"] == 0
            and self.info["run_info"]["failed"] == 0
        ) and self.is_complete():
            return True
        else:
            return False

    def log(self, case_id="case_1"):
        _wait_to_complete(
            Experiment(
                self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
            ),
            "Simulation",
        )
        log = self._exp_sal.execute_log(self._workspace_id, self._exp_id, case_id)
        if log:
            return log
        else:
            raise exceptions.EmptyLogError(
                "Empty log file! Try to increase the log level for more logging!"
            )

    @property
    def id(self):
        return self._exp_id

    @property
    def variables(self):
        _assert_successful_operation(
            Experiment(
                self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal,
            ),
            "Simulation",
        )
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

    def get_trajectories(self, variables):
        _assert_successful_operation(
            Experiment(
                self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal,
            ),
            "Simulation",
        )
        return self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, variables
        )

    def result(self, case_id="case_1"):
        _assert_successful_operation(
            Experiment(
                self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal,
            ),
            "Simulation",
        )
        return self._exp_sal.result_get(self._workspace_id, self._exp_id, case_id)
