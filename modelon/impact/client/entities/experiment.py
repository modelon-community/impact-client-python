import logging
from typing import Any, List, Dict, Optional
from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations import experiment
from modelon.impact.client.entities.case import Case
from modelon.impact.client.entities.asserts import assert_variable_in_result
from modelon.impact.client.entities.status import ExperimentStatus
from modelon.impact.client import exceptions

logger = logging.getLogger(__name__)


def _assert_experiment_is_complete(status, operation_name="Operation"):
    if status == ExperimentStatus.NOTSTARTED:
        raise exceptions.OperationNotCompleteError.for_operation(operation_name, status)
    elif status == ExperimentStatus.CANCELLED:
        raise exceptions.OperationFailureError.for_operation(operation_name)


class _ExperimentRunInfo:
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
    def status(self):
        """Status info for an Experiment"""
        return self._status

    @property
    def errors(self):
        """A list of errors. Is empty unless 'status' attribute is 'FAILED'"""
        return self._errors

    @property
    def successful(self):
        """Number of cases in experiment that are successful"""
        return self._successful

    @property
    def failed(self):
        """Number of cases in experiment thar have failed"""
        return self._failed

    @property
    def cancelled(self):
        """Number of cases in experiment that are cancelled"""
        return self._cancelled

    @property
    def not_started(self):
        """Number of cases in experiment that have not yet started"""
        return self._not_started


class _ExperimentMetaData:
    def __init__(self, user_data: Dict[str, Any]):
        self._user_data = user_data

    @property
    def user_data(self) -> Dict[str, Any]:
        """User data dictionary object attached to experiment, if any"""
        return self._user_data


class Experiment:
    """
    Class containing Experiment functionalities.
    """

    def __init__(
        self,
        workspace_id: str,
        exp_id: str,
        service: Service,
        info: Optional[Dict[str, Any]] = None,
    ):
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._sal = service
        self._info = info

    def __repr__(self):
        return f"Experiment with id '{self._exp_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Experiment) and obj._exp_id == self._exp_id

    @property
    def id(self) -> str:
        """Experiment id"""
        return self._exp_id

    def _get_info(self) -> Dict[str, Any]:
        if self._info is None:
            self._info = self._sal.workspace.experiment_get(
                self._workspace_id, self._exp_id
            )

        return self._info

    @property
    def run_info(self) -> _ExperimentRunInfo:
        """Experiment run information"""
        run_info = self._get_info()["run_info"]

        status = ExperimentStatus(run_info["status"])
        errors = run_info.get("errors", [])
        failed = run_info.get("failed", 0)
        successful = run_info.get("successful", 0)
        cancelled = run_info.get("cancelled", 0)
        not_started = run_info.get("not_started", 0)
        return _ExperimentRunInfo(
            status, errors, failed, successful, cancelled, not_started
        )

    @property
    def metadata(self) -> Optional[_ExperimentMetaData]:
        """Experiment metadata. Returns custom user_data dictionary object attached
        to the experiment, if any."""

        info = self._get_info()
        meta_data = info.get("meta_data")
        if meta_data is not None:
            user_data = meta_data.get("user_data")
            if user_data is not None:
                return _ExperimentMetaData(user_data)

        return None

    @property
    def info(self) -> Dict[str, Any]:
        """Deprecated, use 'run_info' attribute"""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._get_info()

    def execute(
        self, with_cases: Optional[List[Case]] = None, sync_case_changes: bool = True
    ):
        """Exceutes an experiment.
        Returns an modelon.impact.client.operations.experiment.ExperimentOperation class
        object.

        Parameters:

            with_cases --
                A list of cases objects to execute.
            sync_case_changes --
                Boolean specifying if to sync the cases given with the 'with_cases'
                argument against the server before executing the experiment.
                Default is True.

        Returns:

            experiment_ops --
                An modelon.impact.client.operations.experiment.ExperimentOperation
                class object.

        Example::
            experiment = workspace.create_experiment(experiment_definition)
            experiment_ops = experiment.execute()
            experiment_ops.cancel()
            experiment_ops.status()
            experiment_ops.wait()

            generate_cases = experiment.execute(with_cases=[]).wait()
            cases_to_execute =  generate_cases.get_case('case_2')
            experiment = experiment.execute(with_cases=[cases_to_execute]).wait()
        """
        if sync_case_changes and with_cases is not None:
            for case in with_cases:
                case.sync()

        case_ids = [case.id for case in with_cases] if with_cases is not None else None
        return experiment.ExperimentOperation(
            self._workspace_id,
            self._sal.experiment.experiment_execute(
                self._workspace_id, self._exp_id, case_ids
            ),
            self._sal,
        )

    def is_successful(self) -> bool:
        """
        Returns True if the Experiment is done and no cases has failed.
        Use the 'run_info' attribute to get more info.

        Returns:

            True -> If execution process has completed successfully.
            False -> If execution process has failed, is cancelled or still running.

        Example::

            experiment.is_successful()
        """
        return (
            self.run_info.status == ExperimentStatus.DONE
            and self.run_info.failed == 0
            and self.run_info.cancelled == 0
        )

    def get_variables(self) -> List[str]:
        """
        Returns a list of variables available in the result.

        Returns:

            variables --
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
        """
        Returns a list of case objects for an experiment.

        Returns:

            cases --
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
        """
        Returns a case object for a given case_id.

        Parameters:

            case_id --
                The case_id for the case.

        Returns:

            cases --
                An case object.

        Example::

            experiment.get_case('case_1')
        """
        case_data = self._sal.experiment.case_get(
            self._workspace_id, self._exp_id, case_id
        )
        return Case(
            case_data["id"], self._workspace_id, self._exp_id, self._sal, case_data,
        )

    def get_cases_with_label(self, case_label: str) -> List[Case]:
        """
        Returns a list of case objects for an experiment with the label.

        Parameters:

            case_label --
                The case_label for the case.

        Returns:

            cases --
                An list of case objects.

        Example::

            experiment.get_cases_with_label('Cruise condition')
        """
        return [case for case in self.get_cases() if case.meta.label == case_label]

    def get_trajectories(self, variables: List[str]) -> Dict[str, Any]:
        """
        Returns a dictionary containing the result trajectories
        for a list of result variables for all the cases.

        Parameters:

            variables --
                A list of result variables to fecth trajectories for.

        Returns:

            trajectory --
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
        if not isinstance(variables, list):
            raise TypeError(
                "Please specify the list of result keys for the trajectories of "
                "intrest!"
            )
        _assert_experiment_is_complete(self.run_info.status, "Simulation")
        assert_variable_in_result(variables, self.get_variables())

        response = self._sal.experiment.trajectories_get(
            self._workspace_id, self._exp_id, variables
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

    def delete(self):
        """Deletes an experiment.

        Example::

            experiment.delete()
        """
        self._sal.experiment.experiment_delete(self._workspace_id, self._exp_id)

    def set_label(self, label: str):
        """Sets a label (string) for an experiment to distinguish it.

        Example::

            experiment.set_label("Engine run with Oil type B")
        """
        self._sal.experiment.experiment_set_label(
            self._workspace_id, self._exp_id, label
        )
