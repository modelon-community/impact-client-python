from copy import deepcopy
from collections.abc import Mapping


def _set_options(options, **modified):
    opts = deepcopy(options)
    for name, value in modified.items():
        opts[name] = value
    return opts


class ExecutionOptions(Mapping):
    """
    An class containing the simulation, compiler, solver and runtime options settings.
    """

    def __init__(
        self, values, custom_function_name, custom_function_service=None,
    ):
        self._values = values
        self._name = custom_function_name
        self._custom_func_sal = custom_function_service

    def __repr__(self):
        return f"Execution option for '{self._name}'"

    def __getitem__(self, key):
        return self._values[key]

    def __iter__(self):
        return self._values.__iter__()

    def __len__(self):
        return self._values.__len__()

    def with_values(self, **modified):
        """Sets/updates the compiler options.

        Parameters:

            parameters --
                A keyworded, variable-length argument list of compiler
                options.

        Example::

            cmp_opts = custom_function.get_compiler_options().with_values(
                c_compiler='gcc')
            runtime_opts = custom_function.get_runtime_options().with_values(
                cs_solver=0)
            sol_opts = custom_function.get_solver_options().with_values(rtol=1e-7)
            sim_opts = custom_function.get_simulation_options().with_values(ncp=500)
        """
        values = _set_options(self._values, **modified,)
        return ExecutionOptions(values, self._name, self._custom_func_sal)
