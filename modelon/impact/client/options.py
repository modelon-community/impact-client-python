from copy import deepcopy


def _set_options(
    workspace_id, custom_func_name, custom_func_sal, option_cat, options, **modified
):
    opts = deepcopy(options)
    for name, value in modified.items():
        opts[option_cat][name] = value
    return opts


class ExecutionOption:
    def __init__(
        self, workspace_id, options, custom_function_name, custom_function_service=None
    ):
        self._workspace_id = workspace_id
        self._options = options
        self._name = custom_function_name
        self._custom_func_sal = custom_function_service

    def __repr__(self):
        return f"Execution option for '{self._name}'"

    def to_dict(self):
        return self._options

    def with_simulation_options(self, **modified):
        options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "simulation",
            self._options,
            **modified,
        )
        return ExecutionOption(
            self._workspace_id, options, self._name, self._custom_func_sal
        )

    def with_compiler_options(self, **modified):
        options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "compiler",
            self._options,
            **modified,
        )
        return ExecutionOption(
            self._workspace_id, options, self._name, self._custom_func_sal
        )

    def with_solver_options(self, **modified):
        options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "solver",
            self._options,
            **modified,
        )
        return ExecutionOption(
            self._workspace_id, options, self._name, self._custom_func_sal
        )

    def with_runtime_options(self, **modified):
        options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "runtime",
            self._options,
            **modified,
        )
        return ExecutionOption(
            self._workspace_id, options, self._name, self._custom_func_sal
        )
