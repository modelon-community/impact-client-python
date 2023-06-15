from __future__ import annotations
import logging
import enum
from typing import Any, List, Dict, Optional, Union, TYPE_CHECKING

from modelon.impact.client.entities.interfaces.experiment import ExperimentInterface
from modelon.impact.client.operations import experiment
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.asserts import assert_variable_in_result
from modelon.impact.client.entities.status import ExperimentStatus
from modelon.impact.client.options import (
    CompilerOptions,
    SimulationOptions,
    RuntimeOptions,
    SolverOptions,
)
from modelon.impact.client import exceptions

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service
    from modelon.impact.client.operations.base import BaseOperation

logger = logging.getLogger(__name__)

ScalarValue = Union[float, int, str]


@enum.unique
class _TrajectoryResponseFormat(enum.Enum):
    V1 = "application/vnd.impact.trajectories.v1+json"
    V2 = "application/vnd.impact.trajectories.v2+json"


class ExperimentResultPoint:
    """Value class with the single time instance data in a experiment."""

    def __init__(self, trajectories: List[Dict[str, Any]], variables: List[str]):
        self._trajectories = trajectories
        self._variables = variables

    @property
    def variables(self) -> List[str]:
        """List of variables."""
        return self._variables

    @property
    def cases(self) -> List[str]:
        """List of case ids."""
        return [case["caseId"] for case in self._trajectories]

    def as_lists(self) -> List[Optional[List[Optional[ScalarValue]]]]:
        """Return a list of results per case.

        None indicates that the case was not run or failed. None value
        for a variable indicated that the variable is not present in the
        specific case output.

        Example::

            result_data = result.as_lists()

        """
        return [
            [item["trajectory"][0] if item else None for item in case_data["items"]]
            for case_data in self._trajectories
        ]


@enum.unique
class _Workflow(enum.Enum):
    """Workflow type."""

    FMU_BASED = 'FMU_BASED'
    CLASS_BASED = 'CLASS_BASED'


def _assert_experiment_is_complete(
    status: ExperimentStatus, operation_name: str = "Operation"
) -> None:
    if status == ExperimentStatus.NOTSTARTED:
        raise exceptions.OperationNotCompleteError.for_operation(operation_name, status)
    elif status == ExperimentStatus.CANCELLED:
        raise exceptions.OperationFailureError.for_operation(operation_name)


class ExperimentRunInfo:
    """Class containing experiment run information."""

    def __init__(
        self,
        status: ExperimentStatus,
        errors: List[str],
        failed: int,
        successful: int,
        cancelled: int,
        not_started: int,
    ):
        self._status = status
        self._errors = errors
        self._failed = failed
        self._successful = successful
        self._cancelled = cancelled
        self._not_started = not_started

    @property
    def status(self) -> ExperimentStatus:
        """Status info for an Experiment.

        .. Note:: For tracing status changes of a running experiment execution,
            the ExperimentOperation status property must be used and not
            Experiment entities run info(ExperimentRunInfo) status property. See
            example for usage.

        Example::

            # To get the case entity run info status
            status = experiment.run_info.status

            # To get the status updates of a running experiment execution
            experiment_ops = experiment.execute()
            status = experiment_ops.status

        """
        return self._status

    @property
    def errors(self) -> List[str]:
        """A list of errors.

        Is empty unless 'status' attribute is 'FAILED'

        """
        return self._errors

    @property
    def successful(self) -> int:
        """Number of cases in experiment that are successful."""
        return self._successful

    @property
    def failed(self) -> int:
        """Number of cases in experiment thar have failed."""
        return self._failed

    @property
    def cancelled(self) -> int:
        """Number of cases in experiment that are cancelled."""
        return self._cancelled

    @property
    def not_started(self) -> int:
        """Number of cases in experiment that have not yet started."""
        return self._not_started


class ExperimentMetaData:
    """Class containing experiment metadata."""

    def __init__(self, meta_data: Dict[str, Any]):
        self._meta_data = meta_data

    @property
    def user_data(self) -> Dict[str, Any]:
        """User data dictionary object attached to experiment, if any."""
        return self._meta_data.get("user_data", {})

    @property
    def label(self) -> Optional[str]:
        """Experiment label."""
        return self._meta_data.get("label")


class Experiment(ExperimentInterface):
    """Class containing Experiment functionalities."""

    def __init__(
        self,
        workspace_id: str,
        exp_id: str,
        service: Service,
        info: Optional[Dict[str, Any]] = None,
    ):
        self._exp_id = exp_id
        self._workspace_id = workspace_id
        self._sal = service
        self._info = info
        self._fmu_info: Optional[Dict[str, Any]] = None

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Experiment) and obj._exp_id == self._exp_id

    def __repr__(self) -> str:
        return f"Experiment with id '{self._exp_id}'"

    @property
    def id(self) -> str:
        """Experiment id."""
        return self._exp_id

    def _get_info(self, cached: bool = True) -> Dict[str, Any]:
        if not cached or self._info is None:
            self._info = self._sal.workspace.experiment_get(
                self._workspace_id, self._exp_id
            )

        return self._info

    @property
    def run_info(self) -> ExperimentRunInfo:
        """Experiment run information.

        Returns:
            A ExperimentRunInfo class object.

        Example::

            status = experiment.run_info.status

        """
        run_info = self._get_info(cached=False)["run_info"]

        status = ExperimentStatus(run_info["status"])
        errors = run_info.get("errors", [])
        failed = run_info.get("failed", 0)
        successful = run_info.get("successful", 0)
        cancelled = run_info.get("cancelled", 0)
        not_started = run_info.get("not_started", 0)
        return ExperimentRunInfo(
            status, errors, failed, successful, cancelled, not_started
        )

    @property
    def metadata(self) -> ExperimentMetaData:
        """Experiment metadata.

        Returns:
            A ExperimentMetaData class object.

        Example::

            user_data = experiment.metadata.user_data

        """

        info = self._get_info(cached=False)
        meta_data = info.get("meta_data", {})
        return ExperimentMetaData(meta_data)

    @property
    def info(self) -> Dict[str, Any]:
        """Deprecated, use 'run_info' attribute."""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._get_info(cached=False)

    def execute(
        self, with_cases: Optional[List[Case]] = None, sync_case_changes: bool = True
    ) -> experiment.ExperimentOperation:
        """Executes an experiment. Returns an ExperimentOperation class object.

        Args:
            with_cases: A list of cases objects to execute.
            sync_case_changes: Boolean specifying if to sync the cases given with the
                'with_cases' argument against the server before executing the
                experiment. Default is True.

        Returns:
            An ExperimentOperation class object.

        Example::

            experiment = workspace.create_experiment(experiment_definition)
            experiment_ops = experiment.execute()
            experiment_ops.cancel()
            experiment_ops.status
            experiment_ops.wait()

            generate_cases = experiment.execute(with_cases=[]).wait()
            cases_to_execute =  generate_cases.get_case('case_2')
            experiment = experiment.execute(with_cases=[cases_to_execute]).wait()

        """
        if sync_case_changes and with_cases is not None:
            for case in with_cases:
                case.sync()

        case_ids = [case.id for case in with_cases] if with_cases is not None else None
        return experiment.ExperimentOperation[Experiment](
            self._workspace_id,
            self._sal.experiment.experiment_execute(
                self._workspace_id, self._exp_id, case_ids
            ),
            self._sal,
            Experiment.from_operation,
        )

    def is_successful(self) -> bool:
        """Returns True if the Experiment is done and no cases has failed. Use
        the 'run_info' attribute to get more info.

        Returns:
            True, if execution process has completed successfully. False, if
            execution process has failed, is cancelled or still running.

        Example::

            experiment.is_successful()

        """
        return (
            self.run_info.status == ExperimentStatus.DONE
            and self.run_info.failed == 0
            and self.run_info.cancelled == 0
        )

    def get_variables(self) -> List[str]:
        """Returns a list of variables available in the result.

        Returns:
            An list of result variables.

        Raises:
            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            experiment.get_variables()

        """
        _assert_experiment_is_complete(self.run_info.status, "Simulation")
        return self._sal.experiment.result_variables_get(
            self._workspace_id, self._exp_id
        )

    def get_cases(self) -> List[Case]:
        """Returns a list of case objects for an experiment.

        Returns:
            An list of case objects.

        Example::

            experiment.get_cases()

        """
        resp = self._sal.experiment.cases_get(self._workspace_id, self._exp_id)
        return [
            Case(case["id"], self._workspace_id, self._exp_id, self._sal, case)
            for case in resp["data"]["items"]
        ]

    def get_case(self, case_id: str) -> Case:
        """Returns a case object for a given case_id.

        Args:
            case_id: The case_id for the case.

        Returns:
            An case object.

        Example::

            experiment.get_case('case_1')

        """
        case_data = self._sal.experiment.case_get(
            self._workspace_id, self._exp_id, case_id
        )
        return Case(
            case_data["id"], self._workspace_id, self._exp_id, self._sal, case_data
        )

    def get_cases_with_label(self, case_label: str) -> List[Case]:
        """Returns a list of case objects for an experiment with the label.

        Args:
            case_label: The case_label for the case.

        Returns:
            An list of case objects.

        Example::

            experiment.get_cases_with_label('Cruise condition')

        """
        return [case for case in self.get_cases() if case.meta.label == case_label]

    def _validate_and_fetch_trajectories(
        self,
        variables: List[str],
        only_last_point: bool = False,
        format: _TrajectoryResponseFormat = _TrajectoryResponseFormat.V1,
    ) -> Any:
        if not isinstance(variables, list):
            raise TypeError(
                "Please specify the list of result keys for the trajectories of "
                "intrest!"
            )
        _assert_experiment_is_complete(self.run_info.status, "Simulation")
        assert_variable_in_result(variables, self.get_variables())

        return self._sal.experiment.trajectories_get(
            self._workspace_id, self._exp_id, variables, only_last_point, format.value
        )

    def get_trajectories(self, variables: List[str]) -> Dict[str, Any]:
        """Returns a dictionary containing the result trajectories for a list
        of result variables for all the cases.

        Args:
            variables: A list of result variables to fetch trajectories for.

        Returns:
            A dictionary object containing the result trajectories for all cases.

        Raises:
            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process was cancelled.
            TypeError if the variable is not a list object.
            ValueError if trajectory variable is not present in the result.

        Example::

            result = experiment.get_trajectories(['h', 'time'])
            height = result['case_1']['h']
            time = result['case_1']['time']

        """
        response = self._validate_and_fetch_trajectories(
            variables, only_last_point=False, format=_TrajectoryResponseFormat.V1
        )

        if response:
            case_nbrs = range(len(response[0]))
        else:
            case_nbrs = range(len(self.get_cases()))

        return {
            f"case_{j + 1}": {
                variable: response[i][j] for i, variable in enumerate(variables)
            }
            for j in case_nbrs
        }

    def get_last_point(
        self, variables: Optional[List[str]] = None
    ) -> ExperimentResultPoint:
        """Returns a ExperimentResultPoint class for a list of result variables
        for all the cases.

        Args:
            variables: An optional list of result variables to fetch
            trajectories for.

        Returns:
            An ExperimentResultPoint class object.

        Raises:
            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process was cancelled.
            TypeError if the variable is not a list object.
            ValueError if trajectory variable is not present in the result.

        Example::

            result = experiment.get_last_point(['h', 'time'])

            # Convert to Pandas data frame
            df = pd.DataFrame(data=result.as_lists(), columns=result.variables,
                index=result.cases)
            df.index.name = "Cases"

        """
        format = _TrajectoryResponseFormat.V2
        if variables is None:
            variables = self.get_variables()
            trajectories = self._sal.experiment.trajectories_get(
                self._workspace_id,
                self._exp_id,
                variables,
                last_point_only=True,
                format=format.value,
            )
        else:
            trajectories = self._validate_and_fetch_trajectories(
                variables, only_last_point=True, format=format
            )
        return ExperimentResultPoint(trajectories["data"]["items"], variables)

    def delete(self) -> None:
        """Deletes an experiment.

        Example::

            experiment.delete()

        """
        self._sal.experiment.experiment_delete(self._workspace_id, self._exp_id)

    def set_label(self, label: str) -> None:
        """Sets a label (string) for an experiment to distinguish it.

        Example::

            experiment.set_label("Engine run with Oil type B")

        """
        self._sal.experiment.experiment_set_label(
            self._workspace_id, self._exp_id, label
        )

    @classmethod
    def from_operation(
        cls, operation: BaseOperation[Experiment], **kwargs: Any
    ) -> Experiment:
        assert isinstance(operation, experiment.ExperimentOperation)
        return cls(**kwargs, service=operation._sal)

    @property
    def custom_function(self) -> str:
        """Returns the custom function name."""
        return self._get_info()["experiment"]["base"]["analysis"]["type"]

    def _get_fmu_info(self, fmu_id: str) -> Dict[str, Any]:
        if self._fmu_info is None:
            self._fmu_info = self._sal.workspace.fmu_get(self._workspace_id, fmu_id)

        return self._fmu_info

    def _get_workflow(self) -> _Workflow:
        model = self._get_info()["experiment"]["base"]["model"]
        return _Workflow.CLASS_BASED if model.get("modelica") else _Workflow.FMU_BASED

    def get_class_name(self) -> str:
        """Return the model class name."""
        model = self._get_info()["experiment"]["base"]["model"]
        if self._get_workflow() == _Workflow.CLASS_BASED:
            return model["modelica"]["className"]
        return self._get_fmu_info(model["fmu"]["id"])['input']["class_name"]

    def get_compiler_options(self) -> CompilerOptions:
        """Return a CompilerOptions object."""
        model = self._get_info()["experiment"]["base"]["model"]
        if self._get_workflow() == _Workflow.CLASS_BASED:
            return CompilerOptions(
                model["modelica"].get("compilerOptions", {}), self.custom_function
            )
        fmu_info = self._get_fmu_info(model["fmu"]["id"])['input']
        return CompilerOptions(
            fmu_info.get("compiler_options", {}), self.custom_function
        )

    def get_runtime_options(self) -> RuntimeOptions:
        """Return a RuntimeOptions object."""
        model = self._get_info()["experiment"]["base"]["model"]
        if self._get_workflow() == _Workflow.CLASS_BASED:
            return RuntimeOptions(
                model["modelica"].get("runtimeOptions", {}), self.custom_function
            )
        fmu_info = self._get_fmu_info(model["fmu"]["id"])['input']
        return RuntimeOptions(fmu_info.get("runtime_options", {}), self.custom_function)

    def get_simulation_options(self) -> SimulationOptions:
        """Return a SimulationOptions object."""
        analysis = self._get_info()["experiment"]["base"]["analysis"]
        return SimulationOptions(
            analysis.get("simulationOptions", {}), self.custom_function
        )

    def get_solver_options(self) -> SolverOptions:
        """Return a SolverOptions object."""
        analysis = self._get_info()["experiment"]["base"]["analysis"]
        return SolverOptions(analysis.get("solverOptions", {}), self.custom_function)
