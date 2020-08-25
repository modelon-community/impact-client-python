import time
import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping
from enum import Enum
import modelon.impact.client.exceptions as exceptions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _assert_successful_operation(is_successful, operation_name="Operation"):
    """
    Asserts if a operation(compilation or simulation) has successfully completed.
    """
    if not is_successful:
        raise exceptions.OperationFailureError(
            f"{operation_name} failed! See the log for more info!"
        )


def _assert_is_running(status, operation_name="Operation"):
    """
    Asserts if a operation(compilation or simulation) is running.
    """
    if status not in (Status.RUNNING, Status.PENDING):
        raise exceptions.OperationCompleteError(
            f"{operation_name} has completed and cannot be cancelled!"
        )


def _assert_is_complete(status, operation_name="Operation"):
    """
    Asserts if a operation(compilation or simulation) has completed.
    """
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
    """
    Asserts if the variable exists in the result variables.
    """
    if variable not in result_variables:
        raise ValueError(f"{variable} is not present in the result variables!")


def _create_result_dict(variables, workspace_id, exp_id, case_id, exp_sal):
    """
    Creates a result dictionary from the variables and trajectories.
    """
    response = exp_sal.trajectories_get(workspace_id, exp_id, variables)
    case_index = int(case_id.split('_')[1])
    data = {
        variable: response[i][case_index - 1] for i, variable in enumerate(variables)
    }
    return data


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

    @abstractmethod
    def is_successful(self):
        """
        Returns True if the operation has completed successfully.
        """
        pass

    def is_complete(self):
        """
        Returns True if the operation has completed.
        """
        if self.status() in (Status.CANCELLED, Status.STOPPING):
            raise exceptions.OperationFailureError(
                "Operation was cancelled before completion! "
            )
        return self.status() == Status.DONE

    def wait(self, timeout=None, status=Status.DONE):
        """Waits until the operation achieves the set status.
        Returns the operation class instance if the set status is achieved.

        Parameters::

            timeout --
                Time to wait for achieving the status.

            status --
                Operation status to be achieved.
                Default: Status.DONE

        Returns::

            Operation class instance if the set status is achieved.

        Raises::

            OperationTimeOutError if time exceeds set timeout.
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
        """
        Returns the FMU id.
        """
        return self._fmu_id

    @property
    def info(self):
        """
        Returns the compilation information.
        """
        return self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

    @property
    def metadata(self):
        """
        Returns the FMU metadata.

        Raises::

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.
        """
        _assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.ss_fmu_metadata_get(self._workspace_id, self._fmu_id)

    def data(self):
        """
        Returns a new ModelExecutable class instance.
        """
        return ModelExecutable(
            self._workspace_id, self._fmu_id, self._workspace_sal, self._model_exe_sal,
        )

    def status(self):
        """
        Returns the compilation status as an enumeration.
        """
        return Status(
            self._model_exe_sal.compile_status(self._workspace_id, self._fmu_id)[
                "status"
            ]
        )

    def cancel(self):
        """
        Terminates the compilation process.

        Raises::

            OperationCompleteError if compilation process has already completed.
        """
        _assert_is_running(self.status(), "Compilation")
        self._model_exe_sal.compile_cancel(self._workspace_id, self._fmu_id)

    def is_successful(self):
        """
        Returns True if the model has compiled successfully.

        Raises::

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.
        """
        _assert_is_complete(self.status(), "Compilation")
        return True if self.info["run_info"]["status"] == "successful" else False

    def log(self):
        """
        Returns compilation log if the model has compiled.

        Raises::

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.
        """
        _assert_is_complete(self.status(), "Compilation")
        log = self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id)
        if log:
            return log
        else:
            raise exceptions.EmptyLogError(
                "Empty log file! Try to increase the log level for more logging!"
            )

    def settable_parameters(self):
        """
        Returns a list of settable parameters for the FMU.

        Raises::

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.
        """
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
        """
        Returns the experiment id.
        """
        return self._exp_id

    @property
    def info(self):
        """
        Returns the experiment information.
        """
        return self._workspace_sal.experiment_get(self._workspace_id, self._exp_id)

    def data(self):
        """
        Returns a new Experiment class instance.
        """
        return Experiment(
            self._workspace_id, self._exp_id, self._workspace_sal, self._exp_sal
        )

    def status(self):
        """
        Returns the execution status as an enumeration.
        """
        return Status(
            self._exp_sal.execute_status(self._workspace_id, self._exp_id)["status"]
        )

    def cancel(self):
        """
        Terminates the execution process.

        Raises::

            OperationCompleteError if simulation process has already completed.
        """
        _assert_is_running(self.status(), "Simulation")
        self._exp_sal.execute_cancel(self._workspace_id, self._exp_id)

    def is_successful(self):
        """
        Returns True if the FMU has executed successfully.

        Raises::

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.
        """
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
        """
        Returns a list of variables available in the result.

        Raises::

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.
        """
        _assert_successful_operation(self.is_successful(), "Simulation")
        return self._exp_sal.result_variables_get(self._workspace_id, self._exp_id)

    def cases(self):
        """
        Returns a list of case objects for an experiment.
        """
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
        """
        Returns a case object for a given case_id.

        Parameters::

            case_id --
                The case_id for the case.
        """
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
        """
        Returns the case id.
        """
        return self._case_id

    @property
    def info(self):
        """
        Returns the case information.
        """
        return self._exp_sal.case_get(self._workspace_id, self._exp_id, self._case_id)

    def is_successful(self):
        """
        Returns True if a case has completed successfully.
        """
        if self.info["run_info"]["status"] == "successful":
            return True
        else:
            return False

    def log(self):
        """
        Returns the log for a finished case.
        """
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
        """
        Returns the result stream for a finished case.
        """
        _assert_successful_operation(self.is_successful(), self._case_id)
        return self._exp_sal.case_result_get(
            self._workspace_id, self._exp_id, self._case_id
        )

    def trajectories(self):
        """
        Returns result object containing the result trajectories.
        """
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
        """
        Returns vector with result trajectory for a variable, parameter
        or constant that has the same length as the time vector.

        Parameters::

            key --
                Name of the variable/parameter/constant.
        """
        _assert_variable_in_result(key, self.variables)
        response = self._exp_sal.trajectories_get(
            self._workspace_id, self._exp_id, [key]
        )
        case_index = int(self._case_id.split('_')[1])
        return response[0][case_index - 1]

    def __iter__(self):
        data = _create_result_dict(
            self.variables,
            self._workspace_id,
            self._exp_id,
            self._case_id,
            self._exp_sal,
        )
        return data.__iter__()

    def __len__(self):
        return self.variables.__len__()
