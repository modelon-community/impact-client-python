from __future__ import annotations

import logging
import os
import tempfile
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from modelon.impact.client import exceptions
from modelon.impact.client.entities.asserts import assert_successful_operation
from modelon.impact.client.entities.interfaces.model_executable import (
    ModelExecutableInterface,
)
from modelon.impact.client.entities.log import Log
from modelon.impact.client.entities.status import ModelExecutableStatus
from modelon.impact.client.experiment_definition.fmu_based import (
    SimpleFMUExperimentDefinition,
)
from modelon.impact.client.experiment_definition.modifiers import Enumeration
from modelon.impact.client.operations.model_executable import (
    CachedModelExecutableOperation,
    ModelExecutableOperation,
)

if TYPE_CHECKING:
    from modelon.impact.client.entities.custom_function import CustomFunction
    from modelon.impact.client.operations.base import BaseOperation
    from modelon.impact.client.options import SimulationOptions, SolverOptions
    from modelon.impact.client.sal.service import Service

    SimulationOptionsOrDict = Union[SimulationOptions, Dict[str, Any]]
    SolverOptionsOrDict = Union[SolverOptions, Dict[str, Any]]

logger = logging.getLogger(__name__)


def _assert_compilation_is_complete(
    status: ModelExecutableStatus, operation_name: str = "Operation"
) -> None:
    if status == ModelExecutableStatus.NOTSTARTED:
        raise exceptions.OperationNotCompleteError.for_operation(operation_name, status)
    elif status == ModelExecutableStatus.CANCELLED:
        raise exceptions.OperationFailureError.for_operation(operation_name)


class ModelDescription(str):
    """ModelDescription class inheriting from string object."""

    def show(self) -> None:
        """Prints the formatted xml."""
        print(self)

    def download(self, path: Optional[str] = None) -> str:
        """Downloads the formatted xml.

        Args:
            path: The local path to store the downloaded model description.
                Default: None. If no path is given, model description will
                be downloaded in a temporary directory.

        Returns:
            Local path to the model description file.

        Example::

            model_description = fmu.get_model_description()
            model_description.show()
            model_description.download()

        """
        if path is None:
            path = os.path.join(tempfile.gettempdir(), "impact-downloads")
        os.makedirs(path, exist_ok=True)
        artifact_path = os.path.join(path, "modelDescription.xml")
        with open(artifact_path, mode="w", encoding="utf-8") as f:
            f.write(self)
        return artifact_path


class ModelExecutableRunInfo:
    def __init__(self, status: ModelExecutableStatus, errors: List[str]):
        self._status = status
        self._errors = errors

    @property
    def status(self) -> ModelExecutableStatus:
        """Status info for a Model-Executable.

        .. Note:: For tracing status changes of a running
            compilation, the ModelExecutableOperation status
            property must be used and not ModelExecutable
            entities run info(ModelExecutableRunInfo) status
            property. See example for usage.

        Example::

            # To get the case entity run info status
            status = fmu.run_info.status

            # To get the status updates of a running compilation
            compile_ops = = model.compile()
            status = compile_ops.status

        """
        return self._status

    @property
    def errors(self) -> List[str]:
        """A list of errors.

        Is empty unless 'status' attribute is 'FAILED'

        """
        return self._errors


class ModelExecutableInput:
    """Class containing ModelExecutable input."""

    __slots__ = ["_data"]

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def class_name(self) -> str:
        """Returns the model class name."""
        return self._data["class_name"]

    @property
    def compiler_log_level(self) -> str:
        """Returns the compiler log level."""
        return self._data["compiler_log_level"]

    @property
    def compiler_options(self) -> Dict[str, Any]:
        """Returns the compiler options dict."""
        return self._data["compiler_options"]

    @property
    def runtime_options(self) -> Dict[str, Any]:
        """Returns the runtime options dict."""
        return self._data["runtime_options"]

    @property
    def fmi_target(self) -> str:
        """Returns the FMI target."""
        return self._data["fmi_target"]

    @property
    def fmi_version(self) -> str:
        """Returns the FMI version."""
        return self._data["fmi_version"]

    @property
    def platform(self) -> str:
        """Returns the platform the FMU was compiled for."""
        return self._data["platform"]


class ModelExecutable(ModelExecutableInterface):
    """Class containing ModelExecutable functionalities."""

    def __init__(
        self,
        workspace_id: str,
        fmu_id: str,
        service: Service,
        info: Optional[Dict[str, Any]] = None,
        modifiers: Optional[Dict[str, Any]] = None,
    ):
        self._fmu_id = fmu_id
        self._workspace_id = workspace_id
        self._sal = service
        self._info = info
        self._modifiers = modifiers

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, ModelExecutable) and obj._fmu_id == self._fmu_id

    def __repr__(self) -> str:
        return f"FMU with id '{self._fmu_id}'"

    def __hash__(self) -> int:
        return self._fmu_id.__hash__()

    def _convert_enum_to_string(
        self, param: Union[str, int, float, bool, Enumeration]
    ) -> Union[str, int, float, bool]:
        return param.to_value() if isinstance(param, Enumeration) else param

    def _variable_modifiers(self) -> Dict[str, Any]:
        if self._modifiers is None:
            return {}
        # Enum is converted to string as POST workspaces
        # /{workspace_id}/model-executables/{fmu_id}/steady-state-metadata
        # doesn't supports Enum yet.
        return {
            key: self._convert_enum_to_string(value)
            for key, value in self._modifiers.items()
        }

    def _get_info(self, cached: bool = True) -> Dict[str, Any]:
        if not cached or self._info is None:
            self._info = self._sal.workspace.fmu_get(self._workspace_id, self._fmu_id)

        return self._info

    @property
    def id(self) -> str:
        """FMU id."""
        return self._fmu_id

    @property
    def info(self) -> Dict[str, Any]:
        """Deprecated, use 'run_info' attribute."""
        logger.warning("This attribute is deprectated, use 'run_info' instead")
        return self._get_info(cached=False)

    @property
    def run_info(self) -> ModelExecutableRunInfo:
        """Compilation run information."""
        run_info = self._get_info(cached=False)["run_info"]
        status = ModelExecutableStatus(run_info["status"])
        errors = run_info.get("errors", [])
        return ModelExecutableRunInfo(status, errors)

    @property
    def metadata(self) -> Dict[str, Any]:
        """FMU metadata.

        Returns the 'iteration_variable_count' and 'residual_variable_count' only for
        steady state model compiled as an FMU

        """
        assert_successful_operation(self.is_successful(), "Compilation")
        parameter_state = {"parameterState": self._variable_modifiers()}
        return self._sal.model_executable.ss_fmu_metadata_get(
            self._workspace_id, self._fmu_id, parameter_state
        )

    @property
    def input(self) -> ModelExecutableInput:
        """ModelExecutable input attributes.

        Example::

            compiled_platform = fmu.input.platform

            help(fmu.input.platform) # See help for attribute
            dir(fmu.input) # See nested attributes

        """
        return ModelExecutableInput(self._get_info()["input"])

    def get_class_name(self) -> str:
        """Return the model class name."""
        return self._get_info()["input"]["class_name"]

    def is_successful(self) -> bool:
        """Returns True if the model has compiled successfully. Use the 'run_info'
        attribute to get more info.

        Returns:
            True, if model has compiled successfully. False, if compilation
            process has failed, is running or is cancelled.

        Example::

            fmu.is_successful()

        """
        return self.run_info.status == ModelExecutableStatus.SUCCESSFUL

    def get_log(self) -> Log:
        """Returns the compilation log object.

        Returns:
            The compilation log object.

        Raises:
            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process was cancelled.

        Example::

            log = fmu.get_log()
            log.show()

        """
        _assert_compilation_is_complete(self.run_info.status, "Compilation")
        return Log(
            self._sal.model_executable.compile_log(self._workspace_id, self._fmu_id)
        )

    def get_model_description(self) -> ModelDescription:
        """Returns the model description object.

        Returns:
            The ModelDescription class object.

        Example::

            model_description = fmu.get_model_description()

            # Print the formatted xml
            model_description.show()

            # Download the formatted xml
            model_description.download()

            # Parse the xml
            from xml.etree import ElementTree

            tree = ElementTree.fromstring(model_description)
            model_variables =tree.find('ModelVariables')
            variable_names = [child.attrib.get('name') for child in model_variables]

        """
        return ModelDescription(
            self._sal.model_executable.model_description_get(
                self._workspace_id, self._fmu_id
            )
        )

    def delete(self) -> None:
        """Deletes an FMU.

        Example::

            fmu.delete()

        """
        self._sal.model_executable.fmu_delete(self._workspace_id, self._fmu_id)

    def get_settable_parameters(self) -> List[str]:
        """Returns a list of settable parameters for the FMU.

        Returns:
            A list of parameters that can be set on the FMU.

        Raises:
            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.

        Example::

            fmu.get_settable_parameters()

        """
        assert_successful_operation(self.is_successful(), "Compilation")
        return self._sal.model_executable.settable_parameters_get(
            self._workspace_id, self._fmu_id
        )

    def new_experiment_definition(
        self,
        custom_function: CustomFunction,
        solver_options: Optional[SolverOptionsOrDict] = None,
        simulation_options: Optional[SimulationOptionsOrDict] = None,
        simulation_log_level: str = "WARNING",
    ) -> SimpleFMUExperimentDefinition:
        """Returns a new experiment definition using this FMU.

        Args:
            custom_function: The custom function to use for this experiment.
            solver_options: The solver options to use for this experiment. By default
                the options is set to None, which means the default options for the
                custom_function input is used.
            simulation_options: The simulation_options to use for this experiment.
                By default the options is set to None, which means the default options
                for the custom_function input is used.
            simulation_log_level: Simulation log level for this experiment. Default
                is 'WARNING'.

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
        return SimpleFMUExperimentDefinition(
            self,
            custom_function,
            solver_options,
            simulation_options,
            simulation_log_level,
        )

    def download(self, path: Optional[str] = None) -> str:
        """Downloads an FMU binary that is compiled. Returns the local path to the
        downloaded FMU archive.

        Args:
            path: The local path to store the downloaded FMU. Default: None.
                If no path is given, FMU will be downloaded in a temporary directory.

        Returns:
            Local path to the downloaded FMU.

        Raises:
            OperationNotCompleteError if compilation process is in progress.
            OperationFailureError if compilation process has failed or was cancelled.

        Example::

            fmu =  model.compile().wait()
            if fmu.is_successful():
                fmu_path = fmu.download()
                fmu_path = fmu.download('~/Downloads')

        """
        assert_successful_operation(self.is_successful(), "Compilation")
        data = self._sal.workspace.fmu_download(self._workspace_id, self._fmu_id)
        if path is None:
            path = os.path.join(tempfile.gettempdir(), "impact-downloads")
        os.makedirs(path, exist_ok=True)
        fmu_path = os.path.join(path, self._fmu_id + ".fmu")
        with open(fmu_path, "wb") as f:
            f.write(data)
        return fmu_path

    @classmethod
    def from_operation(
        cls, operation: BaseOperation[ModelExecutable], **kwargs: Any
    ) -> ModelExecutable:
        assert isinstance(
            operation, (ModelExecutableOperation, CachedModelExecutableOperation)
        )
        return cls(**kwargs, service=operation._sal)
