import logging
from typing import Any, List, Dict
from modelon.impact.client.sal.custom_function import CustomFunctionService
from modelon.impact.client.options import ExecutionOptions

logger = logging.getLogger(__name__)


class _Parameter:
    _JSON_2_PY_TYPE = {
        "Number": (float, int,),
        "String": (str,),
        "Boolean": (bool,),
        "Enumeration": (str,),
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
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
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


class CustomFunction:
    """
    Class containing CustomFunction functionalities.
    """

    def __init__(
        self,
        workspace_id: str,
        name: str,
        parameter_data: List[Dict[str, Any]],
        custom_function_service: CustomFunctionService,
    ):
        self._name = name
        self._workspace_id = workspace_id
        self._parameter_data = parameter_data
        self._param_by_name = {
            p["name"]: _Parameter(
                p["name"], p["defaultValue"], p["type"], p.get("values", []),
            )
            for p in parameter_data
        }
        self._custom_func_sal = custom_function_service

    def __repr__(self):
        return f"Custom function '{self._name}'"

    def __eq__(self, obj):
        return isinstance(obj, CustomFunction) and obj._name == self._name

    @property
    def name(self) -> str:
        "Custom function name"
        return self._name

    def with_parameters(self, **modified) -> 'CustomFunction':
        """Sets/updates the custom_function parameters for an experiment.

        Parameters:

            parameters --
                A keyworded, variable-length argument list of custom_function
                parameters.

        Example::

            custom_function.with_parameters(start_time=0.0, final_time=2.0)
        """
        new = CustomFunction(
            self._workspace_id, self._name, self._parameter_data, self._custom_func_sal
        )
        for name, value in modified.items():
            if name not in new._param_by_name:
                raise ValueError(
                    f"The custom function '{self._name}' "
                    f"does not have a parameter '{name}'"
                )

            parameter = new._param_by_name[name]
            parameter.value = value

        return new

    @property
    def parameter_values(self) -> Dict[str, Any]:
        """Custom_function parameters and value as a dictionary"""
        return {p.name: p.value for p in self._param_by_name.values()}

    def get_compiler_options(self) -> ExecutionOptions:
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            compiler_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_compiler_options()
            opts_2 = opts.with_values(c_compiler='gcc')
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self._name
        )
        return ExecutionOptions(options["compiler"], self._name, self._custom_func_sal)

    def get_runtime_options(self) -> ExecutionOptions:
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            runtime_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_runtime_options()
            opts_2 = opts.with_values(cs_solver=0)
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self._name
        )
        return ExecutionOptions(options["runtime"], self._name, self._custom_func_sal)

    def get_solver_options(self) -> ExecutionOptions:
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            solver_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_solver_options()
            opts_2 = opts.with_values(rtol=1e-7)
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self._name
        )
        return ExecutionOptions(options["solver"], self._name, self._custom_func_sal)

    def get_simulation_options(self) -> ExecutionOptions:
        """
        Return a modelon.impact.client.options.ExecutionOptions object.

        Returns:

            simulation_options --
                A modelon.impact.client.options.ExecutionOptions object.

        Example::

            opts = custom_function.get_simulation_options()
            opts_2 = opts.with_values(ncp=500)
        """
        options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self._name
        )
        return ExecutionOptions(
            options["simulation"], self._name, self._custom_func_sal
        )
