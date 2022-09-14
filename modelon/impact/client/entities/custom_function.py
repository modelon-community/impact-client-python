import logging
from typing import Any, List, Dict, Optional
from modelon.impact.client.sal.service import Service
from modelon.impact.client.options import ProjectExecutionOptions

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
        service: Service,
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
        self._sal = service

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
            self._workspace_id, self._name, self._parameter_data, self._sal
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

    def get_options(self, use_defaults: Optional[bool] = False):
        """Get project execution option.

        Parameters:

            use_defaults --
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

    def get_compiler_options(self, use_defaults: bool = False):
        """
        Return a modelon.impact.client.options.CompilerOptions object.

        Returns:

            compiler_options --
                A modelon.impact.client.options.CompilerOptions object.

            use_defaults --
                If true, default compiler options are used.
        Example::

            opts = custom_function.get_compiler_options()
            compiler_options = opts.with_values(c_compiler='gcc')
        """
        return self.get_options(use_defaults=use_defaults).compiler_options

    def get_runtime_options(self, use_defaults: bool = False):
        """
        Return a modelon.impact.client.options.RuntimeOptions object.

        Returns:

            runtime_options --
                A modelon.impact.client.options.RuntimeOptions object.

            use_defaults --
                If true, default runtime options are used.
        Example::

            opts = custom_function.get_runtime_options()
            opts_2 = opts.with_values(cs_solver=0)
        """
        return self.get_options(use_defaults=use_defaults).runtime_options

    def get_solver_options(self, use_defaults: bool = False):
        """
        Return a modelon.impact.client.options.SolverOptions object.

        Returns:

            solver_options --
                A modelon.impact.client.options.SolverOptions object.

            use_defaults --
                If true, default solver options are used.

        Example::

            opts = custom_function.get_solver_options()
            opts_2 = opts.with_values(rtol=1e-7)
        """
        return self.get_options(use_defaults=use_defaults).solver_options

    def get_simulation_options(self, use_defaults: bool = False):
        """
        Return a modelon.impact.client.options.SimulationOptions object.

        Returns:

            simulation_options --
                A modelon.impact.client.options.SimulationOptions object.

            use_defaults --
                If true, default simulation options are used.
        Example::

            opts = custom_function.get_simulation_options()
            opts_2 = opts.with_values(ncp=500)
        """
        return self.get_options(use_defaults=use_defaults).simulation_options
