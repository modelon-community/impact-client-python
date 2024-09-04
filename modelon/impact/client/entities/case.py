from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Text, Tuple, Union

from modelon.impact.client import exceptions
from modelon.impact.client.entities.asserts import assert_successful_operation
from modelon.impact.client.entities.custom_artifact import CustomArtifact
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.interfaces.case import CaseReference
from modelon.impact.client.entities.log import Log
from modelon.impact.client.entities.model import (
    Model,
    SimpleModelicaExperimentDefinition,
    to_domain_parameter_value,
)
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.entities.result import Result
from modelon.impact.client.entities.status import CaseStatus
from modelon.impact.client.experiment_definition.modifiers import Enumeration
from modelon.impact.client.operations.base import BaseOperation
from modelon.impact.client.operations.case import CaseOperation
from modelon.impact.client.operations.case_result import CaseResultImportOperation
from modelon.impact.client.operations.custom_artifact import (
    CustomArtifactImportOperation,
)
from modelon.impact.client.sal.experiment import ResultFormat

if TYPE_CHECKING:
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


class CaseRunInfo:
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
        """Status info for a Case.

        .. Note:: For tracing status changes of a running case execution,
            the CaseOperation status property must be used and not Case
            entities run info(CaseRunInfo) status property. See example
            for usage.

        Example::

            # To get the case entity run info status
            status = case.run_info.status

            # To get the status updates of a running case execution
            case_ops = case.execute()
            status = case_ops.status

        """
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


class CaseAnalysis:
    """Class containing Case analysis configuration."""

    __slots__ = ["_analysis"]

    def __init__(self, analysis: Dict[str, Any]):
        self._analysis = analysis

    @property
    def analysis_function(self) -> str:
        """Custom function name.

        Returns:
            The name of the custom function.

        Example::

            analysis_function = case.input.analysis.analysis_function

        """
        return self._analysis["type"]

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get or set parameters for the custom function. Parameters are a dictionary
        containing the custom function parameters.

        Example::

            # Set the custom function parameters
            case.input.analysis.parameters = {'start_time': 0, 'final_time': 90}


            # Get the custom function parameters
            parameters = case.input.analysis.parameters

        """
        parameters = self._analysis["parameters"]
        return {param["name"]: param["value"] for param in parameters}

    @parameters.setter
    def parameters(self, parameters: Dict[str, Any]) -> None:
        self._analysis["parameters"] = [
            {"name": param, "value": parameters[param]} for param in parameters
        ]

    @property
    def simulation_options(self) -> Dict[str, Any]:
        """Get or set the simulation options. Options are key-value pairs of simulation
        options.

        Example::

            # Set the custom function parameters
            case.input.analysis.simulation_options = {'ncp': 600}

            # Get the custom function parameters
            simulation_options = case.input.analysis.simulation_options

        """
        return self._analysis["simulationOptions"]

    @simulation_options.setter
    def simulation_options(self, simulation_options: Dict[str, Any]) -> None:
        self._analysis["simulationOptions"] = simulation_options

    @property
    def solver_options(self) -> Dict[str, Any]:
        """Get or set the simulation options. Options are key-value pairs of solver
        options.

        Example::

            # Set the solver options
            case.input.analysis.solver_options = {'atol': 1e-9}


            # Get the solver options
            solver_options = case.input.analysis.solver_options

        """
        return self._analysis["solverOptions"]

    @solver_options.setter
    def solver_options(self, solver_options: Dict[str, Any]) -> None:
        self._analysis["solverOptions"] = solver_options

    @property
    def simulation_log_level(self) -> str:
        """Get or set the simulation log level. Supported options are- 'WARNING',
        'ERROR', 'DEBUG', 'INFO' and 'VERBOSE'.

        Example::

            # Set the solver options
            case.input.analysis.simulation_log_level = "WARNING"

            # Get the solver options
            simulation_log_level = case.input.analysis.simulation_log_level

        """
        return self._analysis["simulationLogLevel"]

    @simulation_log_level.setter
    def simulation_log_level(self, simulation_log_level: str) -> None:
        self._analysis["simulationLogLevel"] = simulation_log_level


class CaseMeta:
    """Class containing Case meta."""

    __slots__ = ["_data"]

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def label(self) -> str:
        """Get or set the label for the case.

        Example::

            # Set the case label
            case.meta.label = 'Cruise condition'

            # Get the case label
            label = case.meta.label

        """
        return self._data["label"]

    @label.setter
    def label(self, label: str) -> None:
        self._data["label"] = label

    @property
    def orchestrator(self) -> bool:
        """Returns True, if this is an Orchestrator case which creates and runs other
        cases in this experiment..

        Example::

            orchestrator = case.meta.orchestrator

        """
        return self._data.get("orchestrator", False)


class CaseInput:
    """Class containing Case input."""

    __slots__ = ["_data"]

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def analysis(self) -> CaseAnalysis:
        return CaseAnalysis(self._data["analysis"])

    @property
    def parametrization(self) -> Dict[str, Any]:
        """Get or set the parametrization of the case. Parameterization is defined as a
        dict of key value pairs where key is variable name and value is the value to use
        for that variable.

        Example::

            # Set the case parametrization
            case.input.parametrization = {'PI.k': 120}


            # Get the case parametrization
            parametrization = case.input.parametrization

        """
        parametrization = self._data["parametrization"]
        return {
            param["name"]: to_domain_parameter_value(param) for param in parametrization
        }

    @parametrization.setter
    def parametrization(self, parametrization: Dict[str, Any]) -> None:
        converted_params = []
        for name, value in parametrization.items():
            if isinstance(value, Enumeration):
                converted_params.append(value.to_dict(name))
            else:
                converted_params.append({"name": name, "value": value})

        self._data["parametrization"] = converted_params

    @property
    def fmu_id(self) -> str:
        """Reference ID to the compiled model used running the case."""
        return self._data["fmuId"]

    @property
    def structural_parametrization(self) -> Dict[str, Any]:
        """Structural parametrization of the case, a list of key value pairs where key
        is variable name and value is the value to use for that variable.

        These are values that cannot be applied to the FMU/Model after compilation.

        """
        parametrization = self._data["structuralParametrization"]
        return {
            param["name"]: to_domain_parameter_value(param) for param in parametrization
        }

    @property
    def fmu_base_parametrization(self) -> Dict[str, Any]:
        """This is some base parametrization that must be applied to the FMU for it to
        be valid running this case.

        It often comes as a result from of caching to reuse the FMU.

        """
        parametrization = self._data["fmuBaseParametrization"]
        return {
            param["name"]: to_domain_parameter_value(param) for param in parametrization
        }


class Case(CaseReference):
    """Class containing Case functionalities."""

    __slots__ = ["_case_id", "_workspace_id", "_exp_id", "_sal", "_info"]

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
        super().__init__(case_id, workspace_id, exp_id, service, info)

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Case) and obj._case_id == self._case_id

    def __repr__(self) -> str:
        return f"Case with id '{self._case_id}'"

    def _get_info(self, cached: bool = True) -> Dict[str, Any]:
        if not cached or self._info is None:
            self._info = self._sal.experiment.case_get(
                self._workspace_id, self._exp_id, self.id
            )

        return self._info

    @property
    def info(self) -> Dict[str, Any]:
        """Deprecated, use 'run_info' attribute."""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._get_info(cached=False)

    @property
    def run_info(self) -> CaseRunInfo:
        """Case run information."""
        run_info = self._get_info(cached=False)["run_info"]
        started = _datetime_from_unix_time(run_info.get("datetime_started"))
        finished = _datetime_from_unix_time(run_info.get("datetime_finished"))
        return CaseRunInfo(
            CaseStatus(run_info["status"]), run_info["consistent"], started, finished
        )

    @property
    def input(self) -> CaseInput:
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
        return CaseInput(self._info["input"])

    @property
    def meta(self) -> CaseMeta:
        """Case meta attributes.

        Example::

            case.meta.label = 'Cruise condition'
            case.sync()

            help(case.meta) # See help for attribute
            dir(case.input) # See nested attributes

        """
        return CaseMeta(self._info["meta"])

    @property
    def initialize_from_case(self) -> Optional[Case]:
        """Get(if any) or set the case to initialize from.

        Example::

            # Set the case to  initialize from
            # Fetching the successful case
            case_1 = experiment.get_case('case_1')

            # Fetching the failed case
            case_2 = experiment.get_case('case_2')

            # Initializing from successful case
            case_2.initialize_from_case = case_1

            # Re-executing the case after initializing
            case_init_successful = case_2.execute().wait()


            # Get the case set to initialize from
            initialized_from_case = case.initialize_from_case

        """
        init_from_dict = self._info["input"].get("initializeFromCase")
        if init_from_dict is None:
            return None

        experiment_id = init_from_dict.get("experimentId")
        case_id = init_from_dict.get("caseId")

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
        self._assert_unique_case_initialization(
            "initializeFromExternalResult", "initialize_from_external_result"
        )
        self._info["input"]["initializeFromCase"] = {
            "experimentId": case.experiment_id,
            "caseId": case.id,
        }

    @property
    def initialize_from_external_result(self) -> Optional[ExternalResult]:
        """Get(if any) or set the external result file to initialize from.

        Example::

            # Set the external result file to  initialize from
            result = workspace.upload_result(path_to_result="<path_to_result>/
            result.mat", label = "result_to_init", description= "Converged
            result file").wait()

            # Initializing from external result
            case_2.initialize_from_external_result = result

            # Re-executing the case after initializing
            case_init_successful = case_2.execute().wait()


            # Get the external result file to initialize from
            initialize_from_external_result = case.initialize_from_external_result

        """
        init_from_dict = self._info["input"].get("initializeFromExternalResult")

        if init_from_dict is None:
            return None

        result_id = init_from_dict.get("uploadId")

        return ExternalResult(result_id, self._sal)

    @initialize_from_external_result.setter
    def initialize_from_external_result(self, result: ExternalResult) -> None:
        if not isinstance(result, ExternalResult):
            raise TypeError("The value must be an instance of ExternalResult")
        self._assert_unique_case_initialization(
            "initializeFromCase", "initialize_from_case"
        )
        self._info["input"]["initializeFromExternalResult"] = {"uploadId": result.id}

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

    def get_result(self, format: str = "mat") -> Tuple[Union[bytes, Text], str]:
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
            self._sal.experiment.case_result_variables_get(
                self._workspace_id, self._exp_id, self._case_id
            ),
            self._case_id,
            self._workspace_id,
            self._exp_id,
            self._sal,
        )

    def get_variables(self) -> List[str]:
        """Returns a list of variables available in the result.

        Returns:
            An list of result variables.

        Raises:
            OperationNotCompleteError if simulation process is in progress.
            OperationFailureError if simulation process has failed or was cancelled.

        Example::

            case.get_variables()

        """
        _assert_case_is_complete(self.run_info.status, "Simulation")
        return self._sal.experiment.case_result_variables_get(
            self._workspace_id, self._exp_id, self._case_id
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
                f"No custom artifact found with ID: {artifact_id}."
            )
        return meta["downloadAs"]

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
                meta["id"],
                meta["downloadAs"],
                self._sal.experiment,
            )
            for meta in resp["data"]["items"]
        ]

    def get_fmu(
        self,
    ) -> ModelExecutable:
        """Returns the ModelExecutable class object simulated for the case.

        Returns:
            ModelExecutable class object.

        Example::

            case = experiment.get_case('case_1')
            fmu = case.get_fmu()
            fmus = set(case.get_fmu() for case in exp.get_cases())

        """
        fmu_id = self.input.fmu_id
        if not fmu_id:
            custom_function = self._get_custom_function()
            for param in custom_function.parameter_values.values():
                if isinstance(param, CaseReference):
                    case = self.from_reference(param)
                    fmu_id = case.input.fmu_id
        return ModelExecutable(self._workspace_id, fmu_id, self._sal)

    def sync(self) -> None:
        """Sync case state against server, pushing any changes that has been done to the
        object client side.

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
            case_ops.status
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

    def _get_custom_function(self) -> CustomFunction:
        custom_function_meta = self._sal.custom_function.custom_function_get(
            self._workspace_id, self.input.analysis.analysis_function
        )
        custom_function_params = self.input.analysis.parameters
        return CustomFunction(
            self._workspace_id,
            custom_function_meta["name"],
            custom_function_meta["parameters"],
            self._sal,
        ).with_parameters(**custom_function_params)

    def get_definition(self) -> SimpleModelicaExperimentDefinition:
        """Get an experiment definition that can be used to reproduce this case result.

        Returns:
            An instance of SimpleModelicaExperimentDefinition class.

        Example::

            definition = case.get_definition()

        """
        custom_function = self._get_custom_function()
        fmu = self.get_fmu()
        model = Model(
            fmu.input.class_name,
            workspace_id=self._workspace_id,
            project_id="",
            service=self._sal,
        )
        definition = SimpleModelicaExperimentDefinition(
            model=model,
            custom_function=custom_function,
            compiler_options=fmu.input.compiler_options,
            fmi_target=fmu.input.fmi_target,
            fmi_version=fmu.input.fmi_version,
            platform=fmu.input.platform,
            compiler_log_level=fmu.input.compiler_log_level,
            runtime_options=fmu.input.runtime_options,
            solver_options=self.input.analysis.solver_options,
            simulation_options=self.input.analysis.simulation_options,
            simulation_log_level=self.input.analysis.simulation_log_level,
            initialize_from=self.initialize_from_case
            or self.initialize_from_external_result,
        )
        modifiers = {
            **self.input.structural_parametrization,
            **self.input.parametrization,
        }
        definition = definition.with_modifiers(modifiers=modifiers)
        return definition

    def _assert_unique_case_initialization(
        self, unsupported_init: str, unsupported_method_name: str
    ) -> None:
        if self._info["input"][unsupported_init]:
            raise ValueError(
                "A case cannot use both 'initialize_from_case' and "
                "'initialize_from_external_result' to specify what to initialize from! "
                f"To resolve this, set the '{unsupported_method_name}' attribute "
                "to None and re-try."
            )

    @classmethod
    def from_operation(cls, operation: BaseOperation[Case], **kwargs: Any) -> Case:
        assert isinstance(operation, CaseOperation)
        return cls(**kwargs, service=operation._sal)

    @classmethod
    def from_reference(cls, reference: CaseReference) -> Case:
        return cls(
            case_id=reference._case_id,
            workspace_id=reference._workspace_id,
            exp_id=reference._exp_id,
            service=reference._sal,
            info=reference._info,
        )

    def import_custom_artifact(
        self,
        path_to_artifact: str,
        artifact_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> CustomArtifactImportOperation:
        """Upload custom artifact to a case.

        Args:

            path_to_artifact: The path for the artifact to be imported.
            artifact_id: ID of the artifact to be imported.
            overwrite: Overwrite, if any already existing artifact exists
                        with the same ID. Default: False.


        Example::

            case.import_custom_artifact('/home/test.csv', artifact_id).wait()

        """
        resp = self._sal.experiment.custom_artifact_upload(
            path_to_artifact,
            self._workspace_id,
            self._exp_id,
            self._case_id,
            artifact_id,
            overwrite,
        )
        return CustomArtifactImportOperation[CustomArtifact](
            resp["data"]["location"],
            self._workspace_id,
            self._exp_id,
            self._case_id,
            self._sal,
            CustomArtifact.from_operation,
        )

    def import_result(
        self,
        path_to_result: str,
        overwrite: bool = False,
    ) -> CaseResultImportOperation:
        """Upload result to a case.

        Args:

            path_to_result: The path for the result to be imported. Only mat or csv
                result file format is supported for import.
            overwrite: Overwrite, if a result already exists
                for the case. Default: False.


        Example::

            case.import_result('/home/test.csv').wait()

        """
        resp = self._sal.experiment.case_result_upload(
            path_to_result,
            self._workspace_id,
            self._exp_id,
            self._case_id,
            overwrite,
        )
        return CaseResultImportOperation[Result](
            resp["data"]["location"],
            self._workspace_id,
            self._exp_id,
            self._case_id,
            self._sal,
            Result.from_operation,
        )
