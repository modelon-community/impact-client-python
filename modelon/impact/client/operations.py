import time
import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from enum import Enum
from modelon.impact.client import exceptions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _assert_successful_operation(is_successful, operation_name="Operation"):
    if not is_successful:
        raise exceptions.OperationFailureError(
            f"{operation_name} failed! See the log for more info!"
        )


def _assert_is_running(status, operation_name="Operation"):
    if status not in (Status.RUNNING, Status.PENDING):
        raise exceptions.OperationNotCompleteError(
            f"{operation_name} has completed and cannot be cancelled!"
        )


def _assert_is_complete(status, operation_name="Operation"):
    if status in (Status.RUNNING, Status.PENDING):
        raise exceptions.OperationNotCompleteError(
            f"{operation_name} is still in progress! Status : {status}."
            f" Please use the wait() method on the {operation_name} operation"
            " to wait until completion!"
        )
    if status in (Status.CANCELLED, Status.STOPPING):
        raise exceptions.OperationFailureError(
            f"{operation_name} was cancelled before completion! "
            f"Log file generated for cancelled {operation_name} is empty!"
        )


def _assert_variable_in_result(variable, result_variables):
    if variable not in result_variables:
        raise ValueError(f"{variable} is not present in the result variables!")


def create_result_dict(variables, workspace_id, exp_id, case_id, exp_sal):
    response = exp_sal.trajectories_get(workspace_id, exp_id, variables)
    case_index = int(case_id.split('_')[1])
    data = {
        variable: response[i][case_index - 1] for i, variable in enumerate(variables)
    }
    return data


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

    @abstractmethod
    def is_successful(self):
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

    @property
    def id(self):
        return self._fmu_id

    @property
    def info(self):
        return self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

    @property
    def metadata(self):
        _assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.ss_fmu_metadata_get(self._workspace_id, self._fmu_id)

    def data(self):
        return ModelExecutable(
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

    def is_successful(self):
        _assert_is_complete(self.status(), "Compilation")
        return True if self.info["run_info"]["status"] == "successful" else False

    def log(self):
        _assert_is_complete(self.status(), "Compilation")
        log = self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id)
        if log:
            return log
        else:
            raise exceptions.EmptyLogError(
                "Empty log file! Try to increase the log level for more logging!"
            )

    def settable_parameters(self):
        _assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )


class Experiment(Operation):
    def __init__(
        self, workspace_id, exp_id, workspace_service=None, exp_service=None,
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

    @property
    def id(self):
        return self._exp_id

    @property
    def info(self):
        return self._workspace_sal.experiment_get(self._workspace_id, self._exp_id)

    def data(self):
        return Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        )

    def status(self):
        return Status(
            self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]
        )

    def cancel(self):
        _assert_is_running(self.status(), "Simulation")
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)

    def is_successful(self):
        _assert_is_complete(self.status(), "Simulation")
        if (
            self.info["run_info"]["status"] == "done"
            and self.info["run_info"]["cancelled"] == 0
            and self.info["run_info"]["failed"] == 0
        ):
            return True
        else:
            return False

    def variables(self):
        _assert_successful_operation(self.is_successful(), "Simulation")
        return self._exp_sal.result_variables_get(self._workspace_id, self._exp_id)

    def cases(self):
        resp = self._exp_sal.cases_get(self._workspace_id, self._exp_id)
        return [
            Case(
                case["id"],
                self._workspace_id,
                self._exp_id,
                self._exp_sal,
                self._workspace_sal,
            )
            for case in resp["data"]["items"]
        ]

    def case(self, case_id):
        resp = self._exp_sal.case_get(self._workspace_id, self._exp_id, case_id)
        return Case(
            resp["id"],
            self._workspace_id,
            self._exp_id,
            self._exp_sal,
            self._workspace_sal,
        )


class Case:
    def __init__(
        self, case_id, workspace_id, exp_id, exp_service=None, workspace_service=None
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._exp_sal = exp_service
        self._workspace_sal = workspace_service

    def __repr__(self):
        return f"Case with id '{self._case_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Case) and obj._case_id == self._case_id

    @property
    def id(self):
        return self._case_id

    @property
    def info(self):
        return self._exp_sal.case_get(self._workspace_id, self._exp_id, self._case_id)

    def is_successful(self):
        if self.info["run_info"]["status"] == "successful":
            return True
        else:
            return False

    def log(self):
        log = self._exp_sal.case_get_log(
            self._workspace_id, self._exp_id, self._case_id
        )
        if log:
            return log
        else:
            raise exceptions.EmptyLogError(
                "Empty log file! Try to increase the log level for more logging!"
            )

    def result(self):
        _assert_successful_operation(self.is_successful(), self._case_id)
        return self._exp_sal.case_result_get(
            self._workspace_id, self._exp_id, self._case_id
        )

    def trajectories(self):
        _assert_successful_operation(self.is_successful(), self._case_id)
        return Result(
            self._case_id,
            self._workspace_id,
            self._exp_id,
            self._workspace_sal,
            self._exp_sal,
        )


class Result(Mapping):
    def __init__(
        self, case_id, workspace_id, exp_id, workspace_service=None, exp_service=None
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._workspace_sal = workspace_service
        self._exp_sal = exp_service
        self.variables = Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        ).variables()

    def __getitem__(self, key):
        _assert_variable_in_result(key, self.variables)
        response = self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, [key]
        )
        case_index = int(self._case_id.split('_')[1])
        return response[0][case_index - 1]

    def __iter__(self):
        data = create_result_dict(
            self.variables,
            self._workspace_id,
            self._exp_id,
            self._case_id,
            self._exp_sal,
        )
        return data.__iter__()

    def __len__(self):
        return self.variables.__len__()
