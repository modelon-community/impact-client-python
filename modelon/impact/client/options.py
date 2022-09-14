from copy import deepcopy
from collections.abc import Mapping
from typing import Union, List, Dict, Any
from abc import ABC


def _set_options(options, **modified):
    opts = deepcopy(options)
    for name, value in modified.items():
        opts[name] = value
    return opts


class BaseExecutionOptions(Mapping, ABC):
    """
    Base class for the simulation, compiler, solver and runtime options settings.
    """

    def __init__(
        self, values: Dict[str, Any], custom_function_name: str,
    ):
        self._values = values
        self._custom_function_name = custom_function_name

    def __repr__(self):
        return f"{type(self).__name__} for '{self._custom_function_name}'"

    def __getitem__(self, key):
        return self._values[key]

    def __iter__(self):
        return self._values.__iter__()

    def __len__(self):
        return self._values.__len__()

    def with_values(self, **modified):
        """Sets/updates the options.

        Parameters:

            parameters --
                A keyworded, variable-length argument list of options.

        Example::

            cmp_opts = custom_function.get_compiler_options().with_values(
                c_compiler='gcc')
            runtime_opts = custom_function.get_runtime_options().with_values(
                cs_solver=0)
            sol_opts = custom_function.get_solver_options().with_values(rtol=1e-7)
            sim_opts = custom_function.get_simulation_options().with_values(ncp=500)
        """
        values = _set_options(self._values, **modified)
        return self.__class__(values, self._custom_function_name)


class CompilerOptions(BaseExecutionOptions):
    pass


class RuntimeOptions(BaseExecutionOptions):
    pass


class SolverOptions(BaseExecutionOptions):
    pass


class SimulationOptions(BaseExecutionOptions):
    def with_result_filter(self, pattern: Union[str, List[str]]):
        """Sets the variable filter for results.

        Parameters:

            pattern --
                A filter pattern for choosing which variables to actually store
            result for. The syntax can be found in
            http://en.wikipedia.org/wiki/Glob_%28programming%29 . An
            example is filter = "*der" , stores all variables ending with
            'der'. Can also be a list.

        Example::

            sim_opts = custom_function.get_simulation_options().with_result_filter(
                pattern = ["*.phi"])
        """
        if not isinstance(pattern, str):
            pattern = str(pattern)
        return self.with_values(filter=pattern)


class ProjectExecutionOptions:
    def __init__(self, data: Dict[str, Any], name: str):
        self._data = data
        self._name = name

    @property
    def custom_function(self):
        return self._name

    @property
    def compiler_options(self):
        return CompilerOptions(self._data.get("compiler", {}), self.custom_function)

    @property
    def runtime_options(self):
        return RuntimeOptions(self._data.get("runtime", {}), self.custom_function)

    @property
    def simulation_options(self):
        return SimulationOptions(self._data.get("simulation", {}), self.custom_function)

    @property
    def solver_options(self):
        return SolverOptions(self._data.get("solver", {}), self.custom_function)

    def to_dict(self):
        return {"customFunction": self._name, **self._data}
