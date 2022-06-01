import logging
import os
import tempfile
from enum import Enum
from typing import Any, List, Dict, Optional, Union
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.sal.model_executable import ModelExecutableService
from modelon.impact.client.entities.asserts import assert_successful_operation
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.entities.log import Log
from modelon.impact.client.options import ExecutionOptions
from modelon.impact.client.experiment_definition import base
from modelon.impact.client import exceptions


logger = logging.getLogger(__name__)

Options = Union[ExecutionOptions, Dict[str, Any]]


def _assert_compilation_is_complete(status, operation_name="Operation"):
    if status == ModelExecutableStatus.NOTSTARTED:
        raise exceptions.OperationNotCompleteError.for_operation(operation_name, status)
    elif status == ModelExecutableStatus.CANCELLED:
        raise exceptions.OperationFailureError.for_operation(operation_name)


class ModelExecutableStatus(Enum):
    """
    Class representing an enumeration for the possible
    model-executable run info states.
    """

    NOTSTARTED = "not_started"
    CANCELLED = "cancelled"
    SUCCESSFUL = "successful"
    FAILED = "failed"


class _ModelExecutableRunInfo:
    def __init__(self, status: ModelExecutableStatus, errors: List[str]):
        self._status = status
        self._errors = errors

    @property
    def status(self):
        """Status info for a Model-Executable"""
        return self._status

    @property
    def errors(self):
        """A list of errors. Is empty unless 'status' attribute is 'FAILED'"""
        return self._errors


class ModelExecutable:
    """
    Class containing ModelExecutable functionalities.
    """

    def __init__(
        self,
        workspace_id: str,
        fmu_id: str,
        workspace_service: WorkspaceService,
        model_exe_service: ModelExecutableService,
        info: Optional[Dict[str, Any]] = None,
        modifiers: Optional[Dict[str, Any]] = None,
    ):
        self._workspace_id = workspace_id
        self._fmu_id = fmu_id
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_exe_service
        self._info = info
        self._modifiers = modifiers

    def __repr__(self):
        return f"FMU with id '{self._fmu_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ModelExecutable) and obj._fmu_id == self._fmu_id

    def __hash__(self) -> int:
        return self._fmu_id.__hash__()

    @property
    def id(self) -> str:
        """FMU id"""
        return self._fmu_id

    def _variable_modifiers(self) -> Dict[str, Any]:
        return {} if self._modifiers is None else self._modifiers

    def _get_info(self) -> Dict[str, Any]:
        if self._info is None:
            self._info = self._workspace_sal.fmu_get(self._workspace_id, self._fmu_id)

        return self._info

    @property
    def info(self) -> Dict[str, Any]:
        """Deprecated, use 'run_info' attribute"""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._get_info()

    @property
    def run_info(self) -> _ModelExecutableRunInfo:
        """Compilation run information"""
        run_info = self._get_info()["run_info"]
        status = ModelExecutableStatus(run_info["status"])
        errors = run_info.get("errors", [])
        return _ModelExecutableRunInfo(status, errors)

    @property
    def metadata(self) -> Dict[str, Any]:
        """FMU metadata. Returns the 'iteration_variable_count' and 'residual_variable_count'
        only for steady state model compiled as an FMU"""
        assert_successful_operation(self.is_successful(), "Compilation")
        parameter_state = {"parameterState": self._variable_modifiers()}
        return self._model_exe_sal.ss_fmu_metadata_get(
            self._workspace_id, self._fmu_id, parameter_state
        )

    def is_successful(self) -> bool:
        """
        Returns True if the model has compiled successfully.
        Use the 'run_info' attribute to get more info.

        Returns:

            True -> If model has compiled successfully.
            False -> If compilation process has failed, is running or is cancelled.

        Example::

            fmu.is_successful()
        """
        return self.run_info.status == ModelExecutableStatus.SUCCESSFUL

    def get_log(self) -> Log:
        """
        Returns the compilation log object.

        Returns:

            log --
                The compilation log object.

        Raises:

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process was cancelled.

        Example::

            log = fmu.get_log()
            log.show()
        """
        _assert_compilation_is_complete(self.run_info.status, "Compilation")
        return Log(self._model_exe_sal.compile_log(self._workspace_id, self._fmu_id))

    def delete(self):
        """Deletes an FMU.

        Example::

            fmu.delete()
        """
        self._model_exe_sal.fmu_delete(self._workspace_id, self._fmu_id)

    def get_settable_parameters(self) -> List[str]:
        """
        Returns a list of settable parameters for the FMU.

        Returns:

            settable_parameters --
                A list of parameters than can be set on the FMU.

        Raises:

            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.

        Example::

            fmu.get_settable_parameters()
        """
        assert_successful_operation(self.is_successful(), "Compilation")
        return self._model_exe_sal.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )

    def new_experiment_definition(
        self,
        custom_function: CustomFunction,
        solver_options: Optional[Options] = None,
        simulation_options: Optional[Options] = None,
        simulation_log_level: str = "WARNING",
    ):
        """
        Returns a new experiment definition using this FMU.

        Parameters:

            custom_function --
                The custom function to use for this experiment.
            solver_options --
                The solver options to use for this experiment. By default the options
                is set to None, which means the default options for the
                custom_function input is used.
            simulation_options --
                The simulation_options to use for this experiment. By default the
                options is set to None, which means the default options for the
                custom_function input is used.
            simulation_log_level --
                Simulation log level for this experiment. Default is 'WARNING'.

        Example::

            fmu = model.compile().wait()
            dynamic = workspace.get_custom_function('dynamic')
            solver_options = {'atol':1e-8}
            simulation_options = dynamic.get_simulation_options().
            with_values(ncp=500)
            experiment_definition = fmu.new_experiment_definition(
                dynamic, solver_options, simulation_options)
            experiment = workspace.execute(experiment_definition).wait()
        """
        return base.SimpleFMUExperimentDefinition(
            self,
            custom_function,
            solver_options,
            simulation_options,
            simulation_log_level,
        )

    def download(self, path: Optional[str] = None):
        """Downloads an FMU binary that is compiled.
        Returns the local path to the downloaded FMU archive.

        Parameters:

            path --
                The local path to store the downloaded FMU. Default: None.
                If no path is given, FMU will be downloaded in a temporary directory.

        Returns:

            path --
                Local path to the downloaded FMU.

        Example::

            fmu_path = model.compile().wait().download()
            fmu_path = model.compile().wait().download('C:/Downloads')
        """
        data = self._workspace_sal.fmu_download(self._workspace_id, self._fmu_id)
        if path is None:
            path = os.path.join(tempfile.gettempdir(), "impact-downloads")
        os.makedirs(path, exist_ok=True)
        fmu_path = os.path.join(path, self._fmu_id + ".fmu")
        with open(fmu_path, "wb") as f:
            f.write(data)
        return fmu_path
