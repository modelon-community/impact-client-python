from copy import deepcopy


def _set_options(custom_func_name, custom_func_sal, option_cat, options, **modified):
    opts = deepcopy(options)
    for name, value in modified.items():
        opts[option_cat][name] = value
    return opts


class ExecutionOptions:
    """
    An class containing the simulation, compiler, solver and runtime options settings.
    """

    def __init__(self, options, custom_function_name, custom_function_service=None):
        self._options = options
        self._name = custom_function_name
        self._custom_func_sal = custom_function_service

    def __repr__(self):
        return f"Execution option for '{self._name}'"

    def to_dict(self):
        """
        Returns the options as a dictionary.

        Returns::

            options_dict --
                The options object as a dictionary.
        """
        return self._options

    def with_simulation_options(self, **modified):
        """ Sets/updates the simulation options.

        Parameters::

            parameters --
                A keyworded, variable-length argument list of simulation
                options.

        Example::

            custom_function.with_simulation_options(ncp=1000)
        """
        options = _set_options(
            self._name, self._custom_func_sal, "simulation", self._options, **modified,
        )
        return ExecutionOptions(options, self._name, self._custom_func_sal)

    def with_compiler_options(self, **modified):
        """ Sets/updates the compiler options.

        Parameters::

            parameters --
                A keyworded, variable-length argument list of compiler
                options.

        Example::

            custom_function.with_compiler_options(c_compiler='gcc')
        """
        options = _set_options(
            self._name, self._custom_func_sal, "compiler", self._options, **modified,
        )
        return ExecutionOptions(options, self._name, self._custom_func_sal)

    def with_solver_options(self, **modified):
        """ Sets/updates the solver options.

        Parameters::

            parameters --
                A keyworded, variable-length argument list of solver
                options.

        Example::

            custom_function.with_solver_options(rtol=1e-7)
        """
        options = _set_options(
            self._name, self._custom_func_sal, "solver", self._options, **modified,
        )
        return ExecutionOptions(options, self._name, self._custom_func_sal)

    def with_runtime_options(self, **modified):
        """ Sets/updates the runtime options.

        Parameters::

            parameters --
                A keyworded, variable-length argument list of runtime
                options.

        Example::

            custom_function.with_runtime_options(rtol=1e-7)
        """
        options = _set_options(
            self._name, self._custom_func_sal, "runtime", self._options, **modified,
        )
        return ExecutionOptions(options, self._name, self._custom_func_sal)
