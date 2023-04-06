from __future__ import annotations
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, Tuple, Optional, List, Union, Text, TYPE_CHECKING

from modelon.impact.client.sal.experiment import ResultFormat
from modelon.impact.client.operations.base import BaseOperation
from modelon.impact.client.operations.case import CaseOperation
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.log import Log
from modelon.impact.client.entities.result import Result
import modelon.impact.client.entities.model_executable
from modelon.impact.client.entities.status import CaseStatus
from modelon.impact.client.entities.asserts import assert_successful_operation
from modelon.impact.client import exceptions

if TYPE_CHECKING:
    from modelon.impact.client.sal.experiment import ExperimentService
    from modelon.impact.client.sal.service import Service
logger = logging.getLogger(__name__)


def _assert_case_is_complete(
    status: CaseStatus, operation_name: str = "Operation"
) -> None:
    if status == CaseStatus.NOT_STARTED:
        raise exceptions.OperationNotCompleteError.for_operation(operation_name, status)
    elif status == CaseStatus.CANCELLED:
        raise exceptions.OperationFailureError.for_operation(operation_name)


def _datetime_from_unix_time(unix_time: Optional[int]) -> Optional[datetime]:
    return datetime.fromtimestamp(unix_time / 1e3) if unix_time else None


class _CaseRunInfo:
    """Class containing Case run info."""

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
        """True if the case has not been synced since it was executed, false
        otherwise."""
        return self._consistent

    @property
    def started(self) -> Optional[datetime]:
        """Case execution start time.

        Returns None if case execution hasn't started.

        """
        return self._datetime_started

    @property
    def finished(self) -> Optional[datetime]:
        """Case execution finish time.

        Returns None if case execution hasn't finished.

        """
        return self._datetime_finished


class _CaseAnalysis:
    """Class containing Case analysis configuration."""

    __slots__ = ['_analysis']

    def __init__(self, analysis: Dict[str, Any]):
        self._analysis = analysis

    @property
    def analysis_function(self) -> str:
        """The name of the custom function."""
        return self._analysis['analysis_function']

    @property
    def parameters(self) -> Dict[str, Any]:
        """Parameters to the custom function.

        Example::
            {
                "start_time": 0,
                "final_time": 1
            }

        """
        return self._analysis['parameters']

    @parameters.setter
    def parameters(self, parameters: Dict[str, Any]) -> None:
        self._analysis['parameters'] = parameters

    @property
    def simulation_options(self) -> Dict[str, Any]:
        """Key-value pairs of simulation options."""
        return self._analysis['simulation_options']

    @simulation_options.setter
    def simulation_options(self, simulation_options: Dict[str, Any]) -> None:
        self._analysis['simulation_options'] = simulation_options

    @property
    def solver_options(self) -> Dict[str, Any]:
        """Key-value pairs of solver options."""
        return self._analysis['solver_options']

    @solver_options.setter
    def solver_options(self, solver_options: Dict[str, Any]) -> None:
        self._analysis['solver_options'] = solver_options

    @property
    def simulation_log_level(self) -> str:
        """The simulation log level."""
        return self._analysis['simulation_log_level']

    @simulation_log_level.setter
    def simulation_log_level(self, simulation_log_level: str) -> None:
        self._analysis['simulation_log_level'] = simulation_log_level


class CustomArtifact:
    """CustomArtifact class."""

    def __init__(
        self,
        workspace_id: str,
        experiment_id: str,
        case_id: str,
        artifact_id: str,
        download_as: str,
        exp_sal: ExperimentService,
    ):
        self._workspace_id = workspace_id
        self._exp_id = experiment_id
        self._case_id = case_id
        self._artifact_id = artifact_id
        self._download_as = download_as
        self._exp_sal = exp_sal

    @property
    def id(self) -> str:
        """Id of the custom artifact."""
        return self._artifact_id

    @property
    def download_as(self) -> str:
        """File name for the downloaded artifact."""
        return self._download_as

    def download(self, path: Optional[str] = None) -> str:
        """Downloads a custom artifact. Returns the local path to the
        downloaded artifact.

        Args:
            path: The local path to the directory to store the downloaded custom
                artifact. Default: None. If no path is given, custom artifact
                will be downloaded in a temporary directory.

        Returns:
            path: Local path to the downloaded custom artifact.

        Example::

            artifact_path = artifact.download()
            artifact_path = artifact.download('/home/Downloads')

        """
        artifact, _ = self._exp_sal.case_artifact_get(
            self._workspace_id, self._exp_id, self._case_id, self.id
        )
        if path is None:
            path = os.path.join(tempfile.gettempdir(), "impact-downloads")
        os.makedirs(path, exist_ok=True)
        artifact_path = os.path.join(path, self.download_as)
        with open(artifact_path, mode="wb") as f:
            f.write(artifact)
        return artifact_path

    def get_data(self) -> Union[Text, bytes]:
        """Returns the custom artifact stream.

        Returns:
            artifact: The artifact byte stream.

        Example::

            artifact = case.get_artifact("ABCD")
            data = artifact.get_data() # may raise exception on communication error
            with open(artifact.download_as, "wb") as f:
                f.write(data)

        """
        result_stream, _ = self._exp_sal.case_artifact_get(
            self._workspace_id, self._exp_id, self._case_id, self.id
        )

        return result_stream


class _CaseMeta:
    """Class containing Case meta."""

    __slots__ = ['_data']

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def label(self) -> str:
        """Label for the case."""
        return self._data['label']

    @label.setter
    def label(self, label: str) -> None:
        self._data['label'] = label


class _CaseInput:
    """Class containing Case input."""

    __slots__ = ['_data']

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def analysis(self) -> _CaseAnalysis:
        return _CaseAnalysis(self._data['analysis'])

    @property
    def parametrization(self) -> Dict[str, Any]:
        """Parametrization of the case, a list of key value pairs where key is
        variable name and value is the value to use for that variable."""
        return self._data['parametrization']

    @parametrization.setter
    def parametrization(self, parametrization: Dict[str, Any]) -> None:
        self._data['parametrization'] = parametrization

    @property
    def fmu_id(self) -> str:
        """Reference ID to the compiled model used running the case."""
        return self._data['fmu_id']

    @property
    def structural_parametrization(self) -> Dict[str, Any]:
        """Structural parametrization of the case, a list of key value pairs
        where key is variable name and value is the value to use for that
        variable.

        These are values that cannot be applied to the FMU/Model after
        compilation.

        """
        return self._data['structural_parametrization']

    @property
    def fmu_base_parametrization(self) -> Dict[str, Any]:
        """This is some base parametrization that must be applied to the FMU
        for it to be valid running this case.

        It often comes as a result from of caching to reuse the FMU.

        """
        return self._data['fmu_base_parametrization']


class Case:
    """Class containing Case functionalities."""

    __slots__ = ['_case_id', '_workspace_id', '_exp_id', '_sal', '_info']

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

    def __repr__(self) -> str:
        return f"Case with id '{self._case_id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Case) and obj._case_id == self._case_id

    @property
    def id(self) -> str:
        """Case id."""
        return self._case_id

    @property
    def experiment_id(self) -> str:
        """Experiment id."""
        return self._exp_id

    @property
    def info(self) -> Dict[str, Any]:
        """Deprecated, use 'run_info' attribute."""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._info

    @property
    def run_info(self) -> _CaseRunInfo:
        """Case run information."""
        run_info = self._info["run_info"]
        started = _datetime_from_unix_time(run_info.get("datetime_started"))
        finished = _datetime_from_unix_time(run_info.get("datetime_finished"))
        return _CaseRunInfo(
            CaseStatus(run_info["status"]), run_info["consistent"], started, finished
        )

    @property
    def input(self) -> _CaseInput:
        """Case input attributes.

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
        """Case meta attributes.

        Example::

         case.meta.label = 'Cruise condition'
         case.sync()

         help(case.meta) # See help for attribute
         dir(case.input) # See nested attributes

        """
        return _CaseMeta(self._info['meta'])

    @property
    def initialize_from_case(self) -> Optional[Case]:
        init_from_dict = self._info['input'].get('initialize_from_case')
        if init_from_dict is None:
            return None

        experiment_id = init_from_dict.get('experimentId')
        case_id = init_from_dict.get('caseId')

        case_data = self._sal.experiment.case_get(
            self._workspace_id, experiment_id, case_id
        )
        return Case(
            case_data["id"], self._workspace_id, experiment_id, self._sal, case_data
        )

    @initialize_from_case.setter
    def initialize_from_case(self, case: Case) -> None:
        if not isinstance(case, Case):
            raise TypeError("The value must be an instance of Case")
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
    def initialize_from_external_result(self, result: ExternalResult) -> None:
        if not isinstance(result, ExternalResult):
            raise TypeError("The value must be an instance of ExternalResult")
        self._assert_unique_case_initialization('initialize_from_case')
        self._info['input']['initialize_from_external_result'] = {"uploadId": result.id}

    def is_successful(self) -> bool:
        """Returns True if a case has completed successfully.

        Returns:
            True, if the case has executed successfully, False,
            if the case has failed execution.

        Example::

            case.is_successful()

        """
        return self.run_info.status == CaseStatus.SUCCESSFUL

    def get_log(self) -> Log:
        """Returns the log class object for a finished case.

        Returns:
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

    def get_result(self, format: str = 'mat') -> Tuple[Union[bytes, Text], str]:
        """Returns the result stream and the file name for a finished case.

        Args:
            format: The file format to download the result in. The only possible values
                are 'mat' and 'csv'. Default: 'mat'

        Returns:
            A tuple containing, respectively, the result byte stream.
            and the filename for the result. This name could be used to
            write the result stream.

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
        """Returns result(Mapping) object containing the result trajectories.

        Returns:
            A Result object (mapping) that allows requesting trajectory data given
            a variable name.

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

    def get_artifact(
        self, artifact_id: str, download_as: Optional[str] = None
    ) -> CustomArtifact:
        """Returns a CustomArtifact class for a finished case.

        Returns:
            The CustomArtifact class object.

        Raises:
            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            custom_artifact = case.get_artifact(artifact_id)

        """
        assert_successful_operation(self.is_successful(), self._case_id)
        return CustomArtifact(
            self._workspace_id,
            self.experiment_id,
            self._case_id,
            artifact_id,
            download_as
            if download_as
            else self._get_artifact_download_name(artifact_id),
            self._sal.experiment,
        )

    def _get_artifact_download_name(self, artifact_id: str) -> str:
        resp = self._sal.experiment.case_artifacts_meta_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        meta = next(
            (meta for meta in resp["data"]["items"] if meta["id"] == artifact_id),
            None,
        )
        if not meta:
            raise exceptions.NoSuchCustomArtifactError(
                f'No custom artifact found with ID: {artifact_id}.'
            )
        return meta['downloadAs']

    def get_artifacts(self) -> List[CustomArtifact]:
        """Returns a list of CustomArtifact classes for a finished case.

        Returns:
            A list of CustomArtifact class objects.

        Raises:
            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            custom_artifacts = case.get_artifacts()

        """
        assert_successful_operation(self.is_successful(), self._case_id)
        resp = self._sal.experiment.case_artifacts_meta_get(
            self._workspace_id, self._exp_id, self._case_id
        )
        return [
            CustomArtifact(
                self._workspace_id,
                self.experiment_id,
                self._case_id,
                meta['id'],
                meta['downloadAs'],
                self._sal.experiment,
            )
            for meta in resp["data"]["items"]
        ]

    def get_fmu(
        self,
    ) -> modelon.impact.client.entities.model_executable.ModelExecutable:
        """Returns the ModelExecutable class object simulated for the case.

        Returns:
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

    def sync(self) -> None:
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
        """Executes a case. Returns an CaseOperation class object.

        Args:
            sync_case_changes: Boolean specifying if to sync case changes
            against the server before executing the case. Default is True.


        Returns:
            An CaseOperation class object.

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

        return CaseOperation[Case](
            self._workspace_id,
            self._sal.experiment.experiment_execute(
                self._workspace_id, self._exp_id, [self._case_id]
            ),
            self._case_id,
            self._sal,
            Case.from_operation,
        )

    def _assert_unique_case_initialization(self, unsupported_init: str) -> None:
        if self._info['input'][unsupported_init]:
            raise ValueError(
                "A case cannot use both 'initialize_from_case' and "
                "'initialize_from_external_result' to specify what to initialize from! "
                f"To resolve this, set the '{unsupported_init}' attribute "
                "to None and re-try."
            )

    @classmethod
    def from_operation(cls, operation: BaseOperation[Case], **kwargs: Any) -> Case:
        assert isinstance(operation, CaseOperation)
        return cls(**kwargs, service=operation._sal)
