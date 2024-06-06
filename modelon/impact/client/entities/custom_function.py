from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from modelon.impact.client.entities.file_uri import FileURI, get_resource_URI_from_str
from modelon.impact.client.entities.interfaces.case import CaseInterface, CaseReference
from modelon.impact.client.entities.interfaces.custom_function import (
    CustomFunctionInterface,
)
from modelon.impact.client.entities.interfaces.experiment import (
    ExperimentInterface,
    ExperimentReference,
)
from modelon.impact.client.options import ProjectExecutionOptions
from modelon.impact.client.sal.service import Service

if TYPE_CHECKING:
    from modelon.impact.client.options import (
        CompilerOptions,
        RuntimeOptions,
        SimulationOptions,
        SolverOptions,
    )

logger = logging.getLogger(__name__)


class _Parameter:
    __slots__ = ["_name", "_value", "_value_type", "_valid_values"]

    _JSON_2_PY_TYPE = {
        "Number": (
            float,
            int,
        ),
        "String": (str,),
        "Boolean": (bool,),
        "Enumeration": (str,),
        "CaseResult": (CaseInterface,),
        "ExperimentResult": (ExperimentInterface,),
        "FileURI": (FileURI,),
        "VariableNames": (list,),
    }

    def __init__(self, name: str, value: Any, value_type: str, valid_values: List[Any]):
        self._name = name
        self._value = value
        self._value_type = value_type
        self._valid_values = valid_values

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._value_type

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        if not isinstance(value, self._JSON_2_PY_TYPE[self._value_type]):
            raise ValueError(
                f"Cannot set {self._name} to {value}, its type is {self._value_type}"
            )

        if self._value_type == "Enumeration" and value not in self._valid_values:
            raise ValueError(
                f"Cannot set enumeration '{self._name}' to '{value}', "
                f"must be one of {self._valid_values}"
            )
        self._value = value


class ParameterDict(dict):
    def as_raw_dict(self) -> Dict[str, Any]:
        new_dict = {}
        for key, value in self.items():
            if isinstance(value, ExperimentInterface):
                new_dict[key] = value.id
            elif isinstance(value, CaseInterface):
                new_dict[key] = f"{value.experiment_id}/{value.id}"
            elif isinstance(value, FileURI):
                new_dict[key] = str(value)
            else:
                new_dict[key] = value
        return new_dict


class CustomFunction(CustomFunctionInterface):
    """Class containing CustomFunction functionalities."""

    def __init__(
        self,
        workspace_id: str,
        name: str,
        parameter_data: List[Dict[str, Any]],
        service: Service,
    ):
        self._name = name
        self._workspace_id = workspace_id
        self._parameter_data = parameter_data
        self._param_by_name = {
            p["name"]: _Parameter(
                p["name"],
                p.get("defaultValue", ""),
                p["type"],
                p.get("values", []),
            )
            for p in parameter_data
        }
        self._sal = service

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, CustomFunction) and obj._name == self._name

    def __repr__(self) -> str:
        return f"Custom function '{self._name}'"

    @property
    def name(self) -> str:
        "Custom function name"
        return self._name

    def with_parameters(self, **modified: Any) -> CustomFunction:
        """Sets/updates the custom_function parameters for an experiment.

        Args:
            parameters: A key-worded, variable-length argument list of custom_function
                parameters.

        Example::

            custom_function.with_parameters(start_time=0.0, final_time=2.0)

        """
        new = CustomFunction(
            self._workspace_id, self._name, self._parameter_data, self._sal
        )
        for name, value in modified.items():
            if name not in new._param_by_name:
                raise ValueError(
                    f"The custom function '{self._name}' "
                    f"does not have a parameter '{name}'"
                )

            parameter = new._param_by_name[name]
            if parameter.type == "ExperimentResult" and isinstance(value, str):
                exp_info = self._sal.workspace.experiment_get(self._workspace_id, value)
                parameter.value = ExperimentReference(
                    self._workspace_id, value, self._sal, exp_info
                )
            elif parameter.type == "CaseResult" and isinstance(value, str):
                experiment_id, case_id = value.split("/")
                case_info = self._sal.experiment.case_get(
                    self._workspace_id, experiment_id, case_id
                )
                parameter.value = CaseReference(
                    case_id, self._workspace_id, experiment_id, self._sal, case_info
                )
            elif parameter.type == "FileURI" and isinstance(value, str):
                parameter.value = get_resource_URI_from_str(value)
            else:
                parameter.value = value

        return new

    @property
    def parameter_values(self) -> ParameterDict:
        """Custom_function parameters and value as a dictionary."""
        return ParameterDict({p.name: p.value for p in self._param_by_name.values()})

    def get_options(
        self, use_defaults: Optional[bool] = False
    ) -> ProjectExecutionOptions:
        """Get project execution option.

        Args:
            use_defaults:
                If true, default compiler options are used.

        Example::

            opts = custom_function.get_compiler_options()
            opts_2 = opts.compiler_options.with_values(c_compiler='gcc')

        """
        if use_defaults:
            options = self._sal.custom_function.custom_function_default_options_get(
                self._workspace_id, self._name
            )
        else:
            options = self._sal.custom_function.custom_function_options_get(
                self._workspace_id, self._name
            )
        return ProjectExecutionOptions(options, self.name)

    def get_compiler_options(self, use_defaults: bool = False) -> CompilerOptions:
        """Return a modelon.impact.client.options.CompilerOptions object.

        Args:
            use_defaults:
                If True, default compiler options are used.

        Returns:
            A CompilerOptions object.

        Example::

            opts = custom_function.get_compiler_options()
            compiler_options = opts.with_values(c_compiler='gcc')

        """
        return self.get_options(use_defaults=use_defaults).compiler_options

    def get_runtime_options(self, use_defaults: bool = False) -> RuntimeOptions:
        """Return a RuntimeOptions object.

        Args:
            use_defaults:
                If True, default compiler options are used.

        Returns:
            A RuntimeOptions object.

        Example::

            opts = custom_function.get_runtime_options()
            opts_2 = opts.with_values(cs_solver=0)

        """
        return self.get_options(use_defaults=use_defaults).runtime_options

    def get_solver_options(self, use_defaults: bool = False) -> SolverOptions:
        """Return a modelon.impact.client.options.SolverOptions object.

        Args:
            use_defaults:
                If True, default compiler options are used.

        Returns:
            A SolverOptions object.

        Example::

            opts = custom_function.get_solver_options()
            opts_2 = opts.with_values(rtol=1e-7)

        """
        return self.get_options(use_defaults=use_defaults).solver_options

    def get_simulation_options(self, use_defaults: bool = False) -> SimulationOptions:
        """Return a SimulationOptions object.

        Args:
            use_defaults:
                If True, default compiler options are used.

        Returns:
            A SimulationOptions object.

        Example::

            opts = custom_function.get_simulation_options()
            opts_2 = opts.with_values(ncp=500)

        """
        return self.get_options(use_defaults=use_defaults).simulation_options
