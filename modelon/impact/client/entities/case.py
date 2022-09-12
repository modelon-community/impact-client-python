import logging
from datetime import datetime
from typing import Any, Dict, Tuple, Optional
from modelon.impact.client.sal.service import Service
from modelon.impact.client.sal.experiment import ResultFormat
from modelon.impact.client.operations.case import CaseOperation
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.log import Log
from modelon.impact.client.entities.result import Result
import modelon.impact.client.entities.model_executable
from modelon.impact.client.entities.status import CaseStatus
from modelon.impact.client.entities.asserts import assert_successful_operation
from modelon.impact.client import exceptions

logger = logging.getLogger(__name__)


def _assert_case_is_complete(status, operation_name="Operation"):
    if status == CaseStatus.NOT_STARTED:
        raise exceptions.OperationNotCompleteError.for_operation(operation_name, status)
    elif status == CaseStatus.CANCELLED:
        raise exceptions.OperationFailureError.for_operation(operation_name)


def _datetime_from_unix_time(unix_time: Optional[int]):
    if unix_time:
        return datetime.fromtimestamp(unix_time / 1e3)


class _CaseRunInfo:
    """
    Class containing Case run info.
    """

    def __init__(
        self,
        status: CaseStatus,
        consistent: bool,
        datetime_started: Optional[datetime],
        datetime_finished: Optional[datetime],
    ):
        self._status = status
        self._consistent = consistent
        self._datetime_started = datetime_started
        self._datetime_finished = datetime_finished

    @property
    def status(self) -> CaseStatus:
        """Status info for a Case, its type is CaseStatus."""
        return self._status

    @property
    def consistent(self) -> bool:
        """True if the case has not been synced since it was executed,
        false otherwise."""
        return self._consistent

    @property
    def started(self):
        """
        Case execution start time. Returns None if case execution hasn't started.
        """
        return self._datetime_started

    @property
    def finished(self):
        """
        Case execution finish time. Returns None if case execution hasn't finished.
        """
        return self._datetime_finished


class _CaseAnalysis:
    """
    Class containing Case analysis configuration.
    """

    def __init__(self, analysis: Dict[str, Any]):
        self._analysis = analysis

    @property
    def analysis_function(self) -> str:
        """The name of the custom function"""
        return self._analysis['analysis_function']

    @property
    def parameters(self) -> Dict[str, Any]:
        """Parameters to the custom function

        Example::
            {
                "start_time": 0,
                "final_time": 1
            }
        """
        return self._analysis['parameters']

    @parameters.setter
    def parameters(self, parameters: Dict[str, Any]):
        self._analysis['parameters'] = parameters

    @property
    def simulation_options(self) -> Dict[str, Any]:
        """Key-value pairs of simulation options"""
        return self._analysis['simulation_options']

    @simulation_options.setter
    def simulation_options(self, simulation_options: Dict[str, Any]):
        self._analysis['simulation_options'] = simulation_options

    @property
    def solver_options(self) -> Dict[str, Any]:
        """Key-value pairs of solver options"""
        return self._analysis['solver_options']

    @solver_options.setter
    def solver_options(self, solver_options: Dict[str, Any]):
        self._analysis['solver_options'] = solver_options

    @property
    def simulation_log_level(self) -> str:
        """The simulation log level"""
        return self._analysis['simulation_log_level']

    @simulation_log_level.setter
    def simulation_log_level(self, simulation_log_level: str):
        self._analysis['simulation_log_level'] = simulation_log_level


class _CaseMeta:
    """
    Class containing Case meta
    """

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def label(self) -> str:
        """Label for the case."""
        return self._data['label']

    @label.setter
    def label(self, label: str):
        self._data['label'] = label


class _CaseInput:
    """
    Class containing Case input
    """

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def analysis(self) -> _CaseAnalysis:
        return _CaseAnalysis(self._data['analysis'])

    @property
    def parametrization(self) -> Dict[str, Any]:
        """
        Parameterization of the case, a list of key value pairs where key
        is variable name and value is the value to use for that variable.
        """
        return self._data['parametrization']

    @parametrization.setter
    def parametrization(self, parameterization: Dict[str, Any]):
        self._data['parametrization'] = parameterization

    @property
    def fmu_id(self) -> str:
        """Reference ID to the compiled model used running the case."""
        return self._data['fmu_id']

    @property
    def structural_parametrization(self) -> Dict[str, Any]:
        """
        Structural parameterization of the case, a list of key value pairs where
        key is variable name and value is the value to use for that variable.
        These are values that cannot be applied to the FMU/Model after compilation.
        """
        return self._data['structural_parametrization']

    @property
    def fmu_base_parametrization(self) -> Dict[str, Any]:
        """
        This is some base parametrization that must be applied to the FMU for
        it to be valid running this case. It often comes as a result from of
        caching to reuse the FMU.
        """
        return self._data['fmu_base_parametrization']


class Case:
    """
    Class containing Case functionalities.
    """

    def __init__(
        self,
        case_id: str,
        workspace_id: str,
        exp_id: str,
        service: Service,
        info: Dict[str, Any],
    ):
        self._case_id = case_id
        self._workspace_id = workspace_id
        self._exp_id = exp_id
        self._sal = service
        self._info = info

    def __repr__(self):
        return f"Case with id '{self._case_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Case) and obj._case_id == self._case_id

    @property
    def id(self) -> str:
        """Case id"""
        return self._case_id

    @property
    def experiment_id(self) -> str:
        """Experiment id"""
        return self._exp_id

    @property
    def info(self) -> Dict[str, Any]:
        """Deprecated, use 'run_info' attribute"""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._info

    @property
    def run_info(self) -> _CaseRunInfo:
        """Case run information"""
        run_info = self._info["run_info"]
        started = _datetime_from_unix_time(run_info.get("datetime_started"))
        finished = _datetime_from_unix_time(run_info.get("datetime_finished"))
        return _CaseRunInfo(
            CaseStatus(run_info["status"]), run_info["consistent"], started, finished,
        )

    @property
    def input(self) -> _CaseInput:
        """Case input attributes

        Example::

         case.input.analysis.parameters = {'start_time': 0, 'final_time': 90}
         case.input.analysis.simulation_options = {'ncp': 600}
         case.input.analysis.solver_options = {'atol': 1e-8}
         case.input.parametrization = {'PI.k': 120}
         case.sync()

         help(case.input.analysis) # See help for attribute
         dir(case.input) # See nested attributes
        """
        return _CaseInput(self._info['input'])

    @property
    def meta(self) -> _CaseMeta:
        """Case meta attributes

        Example::

         case.meta.label = 'Cruise condition'
         case.sync()

         help(case.meta) # See help for attribute
         dir(case.input) # See nested attributes
        """
        return _CaseMeta(self._info['meta'])

    @property
    def initialize_from_case(self) -> Optional['Case']:
        init_from_dict = self._info['input'].get('initialize_from_case')
        if init_from_dict is None:
            return None

        experiment_id = init_from_dict.get('experimentId')
        case_id = init_from_dict.get('caseId')

        case_data = self._sal.experiment.case_get(
            self._workspace_id, experiment_id, case_id
        )
        return Case(
            case_data["id"], self._workspace_id, experiment_id, self._sal, case_data,
        )

    @initialize_from_case.setter
    def initialize_from_case(self, case: 'Case'):
        if not isinstance(case, Case):
            raise TypeError(
                "The value must be an instance of modelon.impact.client.entities."
                "case.Case"
            )
        self._assert_unique_case_initialization('initialize_from_external_result')
        self._info['input']['initialize_from_case'] = {
            'experimentId': case.experiment_id,
            'caseId': case.id,
        }

    @property
    def initialize_from_external_result(self) -> Optional[ExternalResult]:
        init_from_dict = self._info['input'].get('initialize_from_external_result')

        if init_from_dict is None:
            return None

        result_id = init_from_dict.get('uploadId')

        return ExternalResult(result_id, self._sal)

    @initialize_from_external_result.setter
    def initialize_from_external_result(self, result: ExternalResult):
        if not isinstance(result, ExternalResult):
            raise TypeError(
                "The value must be an instance of "
                "modelon.impact.client.entities.external_result.ExternalResult"
            )
        self._assert_unique_case_initialization('initialize_from_case')
        self._info['input']['initialize_from_external_result'] = {"uploadId": result.id}

    def is_successful(self) -> bool:
        """
        Returns True if a case has completed successfully.

        Returns:

            True -> If the case has executed successfully.
            False -> If the case has failed execution.

        Example::

            case.is_successful()
        """
        return self.run_info.status == CaseStatus.SUCCESSFUL

    def get_log(self) -> Log:
        """
        Returns the log class object for a finished case.

        Returns:

            log --
                The case execution log class object.

        Example::

            log = case.get_log()
            log.show()
        """
        return Log(
            self._sal.experiment.case_get_log(
                self._workspace_id, self._exp_id, self._case_id
            )
        )

    def get_result(self, format: str = 'mat') -> Tuple[bytes, str]:
        """
        Returns the result stream and the file name for a finished case.

        Parameters:

            format --
                The file format to download the result in. The only possible values
                are 'mat' and 'csv'.
                Default: 'mat'

        Returns:

            result --
                The result byte stream.

            filename --
                The filename for the result. This name could be used to write the
                result stream.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.
            TypeError if the variable is not a list object.
            ValueError if trajectory variable is not present in the result.

        Example::

            result, file_name = case.get_result(format = 'csv')
            with open(file_name, "w") as f:
                f.write(result)
        """
        assert_successful_operation(self.is_successful(), self._case_id)
        result_format = ResultFormat(format)
        result, file_name = self._sal.experiment.case_result_get(
            self._workspace_id, self._exp_id, self._case_id, result_format
        )
        return result, file_name

    def get_trajectories(self) -> Result:
        """
        Returns result(Mapping) object containing the result trajectories.

        Returns:

            trajectories --
                A result trajectory dictionary object.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process was cancelled.

        Example::

            result = case.get_trajectories()
            result_variables = result.keys()
            height = result['h']
            time = res['time']
        """
        _assert_case_is_complete(self.run_info.status, "Simulation")
        return Result(
            self._sal.experiment.result_variables_get(self._workspace_id, self._exp_id),
            self._case_id,
            self._workspace_id,
            self._exp_id,
            self._sal,
        )

    def get_artifact(self, artifact_id: str) -> Tuple[bytes, str]:
        """
        Returns the artifact stream and the file name for a finished case.

        Parameters:

            artifact_id --
                The ID of the artifact.

        Returns:

            artifact --
                The artifact byte stream.

            filename --
                The filename for the artifact. This name could be used to write the
                artifact stream.

        Raises:

            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            result, file_name = case.get_artifact("ABCD")
            with open(file_name, "wb") as f:
                f.write(result)
        """
        assert_successful_operation(self.is_successful(), self._case_id)
        result, file_name = self._sal.experiment.case_artifact_get(
            self._workspace_id, self._exp_id, self._case_id, artifact_id
        )

        return result, file_name

    def get_fmu(self):
        """
        Returns the ModelExecutable class object simulated for the case.

        Returns:

            FMU --
                ModelExecutable class object.

        Example::

            case = experiment.get_case('case_1')
            fmu = case.get_fmu()
            fmus = set(case.get_fmu() for case in exp.get_cases())
        """
        fmu_id = self.input.fmu_id

        return modelon.impact.client.entities.model_executable.ModelExecutable(
            self._workspace_id, fmu_id, self._sal
        )

    def sync(self):
        """Sync case state against server, pushing any changes that has been
        done to the object client side.

        Example::
            case.input.parametrization = {'PI.k': 120}
            case.sync()
        """
        self._info = self._sal.experiment.case_put(
            self._workspace_id, self._exp_id, self._case_id, self._info
        )

    def execute(self, sync_case_changes: bool = True) -> CaseOperation:
        """Exceutes a case.
        Returns an modelon.impact.client.operations.case.CaseOperation class object.

        Parameters:

            sync_case_changes --
                Boolean specifying if to sync case changes against the server
                before executing the case. Default is True.


        Returns:

            case_ops --
                An modelon.impact.client.operations.case.CaseOperation class object.

        Example::
            case = experiment.get_case('case_1')
            case.input.parametrization = {'PI.k': 120}
            case.sync()
            case_ops = case.execute()
            case_ops.cancel()
            case_ops.status()
            case_ops.wait()
        """
        if sync_case_changes:
            self.sync()

        return CaseOperation(
            self._workspace_id,
            self._sal.experiment.experiment_execute(
                self._workspace_id, self._exp_id, [self._case_id]
            ),
            self._case_id,
            self._sal,
        )

    def _assert_unique_case_initialization(self, unsupported_init):
        if self._info['input'][unsupported_init]:
            raise ValueError(
                "A case cannot use both 'initialize_from_case' and "
                "'initialize_from_external_result' to specify what to initialize from! "
                f"To resolve this, set the '{unsupported_init}' attribute "
                "to None and re-try."
            )
