def _set_options(
    workspace_id, custom_func_name, custom_func_sal, option_cat, options, **modified
):
    for name, value in modified.items():
        options[option_cat][name] = value
    custom_func_sal.custom_function_options_set(
        workspace_id, custom_func_name, {"options": options}
    )
    options = custom_func_sal.custom_function_options_get(
        workspace_id, custom_func_name
    )
    return options


def _assert_option_exists(valid_opts, option_cat, *options):
    for option in options:
        if option not in list(valid_opts[option_cat]):
            raise KeyError(
                f'"{option}" is not a valid option. Valid options '
                f'are {(", ").join(valid_opts[option_cat])}.'
            )


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

    @property
    def to_dict(self):
        return self._options

    def simulation(self, **modified):
        self._options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "simulation",
            self._options,
            **modified,
        )
        return OptionAttributes(
            self._workspace_id,
            self._options,
            "simulation",
            self._name,
            self._custom_func_sal,
        )

    def compiler(self, **modified):
        self._options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "compiler",
            self._options,
            **modified,
        )
        return OptionAttributes(
            self._workspace_id,
            self._options,
            "compiler",
            self._name,
            self._custom_func_sal,
        )

    def solver(self, **modified):
        self._options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "solver",
            self._options,
            **modified,
        )
        return OptionAttributes(
            self._workspace_id,
            self._options,
            "solver",
            self._name,
            self._custom_func_sal,
        )

    def runtime(self, **modified):
        self._options = _set_options(
            self._workspace_id,
            self._name,
            self._custom_func_sal,
            "runtime",
            self._options,
            **modified,
        )
        return OptionAttributes(
            self._workspace_id,
            self._options,
            "runtime",
            self._name,
            self._custom_func_sal,
        )

    def delete(self, option_cat, *options):
        _assert_option_exists(self._options, option_cat, *options)
        opts_del = {"options": {option_cat: [option for option in options]}}
        self._custom_func_sal.custom_function_options_delete(
            self._workspace_id, self._name, opts_del
        )
        self._options = self._custom_func_sal.custom_function_options_get(
            self._workspace_id, self._name
        )


class OptionAttributes:
    def __init__(
        self,
        workspace_id,
        options,
        option_cat,
        custom_function_name,
        custom_function_service,
    ):
        self._workspace_id = workspace_id
        self._options = options
        self._option_cat = option_cat
        self._name = custom_function_name
        self._custom_func_sal = custom_function_service

    @property
    def values(self):
        return self._options[self._option_cat]

    @property
    def defaults(self):
        options = self._custom_func_sal.custom_function_default_options_get(
            self._workspace_id, self._name
        )
        return options[self._option_cat]
