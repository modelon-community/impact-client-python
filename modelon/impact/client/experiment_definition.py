from modelon.impact.client import entities
from abc import ABC, abstractmethod
from modelon.impact.client.options import ExecutionOptions
from modelon.impact.client import exceptions


def _assert_valid_args(fmu, custom_function, solver_options, simulation_options):
    if not isinstance(fmu, entities.ModelExecutable):
        raise TypeError("Fmu must be an instance of ModelExecutable class!")
    if not isinstance(custom_function, entities.CustomFunction):
        raise TypeError("Custom_function must be an instance of CustomFunction class!")
    if solver_options is not None and not isinstance(
        solver_options, (ExecutionOptions, dict)
    ):
        raise TypeError(
            "Solver options must be an instance of ExecutionOptions class or a "
            "dictionary class object!"
        )
    if simulation_options is not None and not isinstance(
        simulation_options, (ExecutionOptions, dict)
    ):
        raise TypeError(
            "Simulation options must be an instance of ExecutionOptions class or"
            " a dictionary class object!"
        )


def _assert_successful_compilation(fmu):
    if not fmu.is_successful():
        raise exceptions.OperationFailureError(
            "Compilation process has failed! See the log for more info!"
        )


def _assert_valid_case_modifiers(cases_modifiers):
    if not isinstance(cases_modifiers, list):
        raise TypeError("The case modifiers argument must be a list!")
    for case_modifier in cases_modifiers:
        if not isinstance(case_modifier, dict):
            raise TypeError(
                "The variable modifiers in the case_modifier list must be a "
                "dictionary!"
            )


def _assert_valid_extensions(experiment_extensions):
    if not isinstance(experiment_extensions, list):
        raise TypeError("The experiment extensions argument must be a list!")
    for extension in experiment_extensions:
        if not isinstance(extension, SimpleExperimentExtension):
            raise TypeError(
                "The extension object in the experiment extension list "
                "must be an instance of modelon.impact.client.experiment_definition."
                "SimpleExperimentExtension class!"
            )


class Operator:
    """
    Base class for an Operator.
    """

    @abstractmethod
    def __str__(self):
        "Returns a string representation of the operator"
        pass


class Range(Operator):
    """
    Range operator class for parameterizing batch runs.

    Parameters:

        start_value --
            The start value for the sweep parameter.

        end_value --
            The end value for the sweep parameter.

        no_of_steps --
            The number of steps to intermediate steps to take between start_value
            and end_value.

    Examples::

        from modelon.impact.client import Range

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Range(0.1, 0.5, 3)})
    """

    def __init__(self, start_value, end_value, no_of_steps):
        self.start_value = start_value
        self.end_value = end_value
        self.no_of_steps = no_of_steps

    def __str__(self):
        return f"range({self.start_value},{self.end_value},{self.no_of_steps})"


class Choices(Operator):
    """
    Choices operator class for parameterizing batch runs.

    Parameters:

        values --
            Variable number of numerical arguments to sweep.

    Examples::

        from modelon.impact.client import Choices

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Choices(0.1, 0.5)})
    """

    def __init__(self, *values):
        self.values = values

    def __str__(self):
        return f"choices{self.values}"


class BaseExperimentDefinition(ABC):
    """
    Base class for an Experiment definition class.
    """

    @abstractmethod
    def validate(self):
        """
        Validates the modifiers appended to the experiment definition.
        """
        pass


class SimpleExperimentDefinition(BaseExperimentDefinition):
    """
    A simple experiment definition class for defining experiements.

    Parameters:

        fmu --
            The FMU to be excecuted for this experiment.

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

    Examples::

        fmu = model.compile().wait()
        simulation_options = custom_function.get_simulation_options()
        .with_values(ncp=500)
        solver_options = {'atol':1e-8}
        simulate_def = fmu.new_experiment_definition(custom_function,
        solver_options, simulation_options)
        simulate_def.to_dict()
    """

    def __init__(
        self,
        fmu,
        custom_function,
        solver_options=None,
        simulation_options=None,
        simulation_log_level="WARNING",
    ):
        _assert_valid_args(fmu, custom_function, solver_options, simulation_options)
        _assert_successful_compilation(fmu)
        self.fmu = fmu
        self.custom_function = custom_function
        self._solver_options = (
            dict(custom_function.get_solver_options())
            if solver_options is None
            else dict(solver_options)
            if isinstance(solver_options, ExecutionOptions)
            else solver_options
        )
        self._simulation_options = (
            dict(custom_function.get_simulation_options())
            if simulation_options is None
            else dict(simulation_options)
            if isinstance(simulation_options, ExecutionOptions)
            else simulation_options
        )
        self._simulation_log_level = simulation_log_level
        self.variable_modifiers = {}
        self.extensions = []

    def validate(self):
        add = set(self.variable_modifiers.keys()) - set(
            self.fmu.get_settable_parameters()
        )
        if add:
            raise KeyError(
                f"Paramter(s) '{', '.join(add)}' {'are' if len(add)>1 else 'is'} "
                "not a valid parameter modifier! Call the get_settable_parameters() "
                "method on the fmu to view the list of settable parameters."
            )

    def with_modifiers(self, modifiers=None, **modifiers_kwargs):
        """Sets the modifiers parameters for an experiment.

        Parameters:

            modifiers --
                A dictionary of variable modifiers. Could be used if
                modifiers keys conflict with python identifiers or keywords.
                Default: None.

            modifiers_kwargs --
                A keyworded, variable-length argument list of variable
                modifiers.

        Example::

            from modelon.impact.client import Range, Choices

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(
                custom_function).with_modifiers({'inertia1.J': Choices(0.1, 0.9),
                'inertia2.J': Range(0.1, 0.5, 3)})
        """
        modifiers = {} if modifiers is None else modifiers
        modifiers_aggregate = {**modifiers, **modifiers_kwargs}
        new = SimpleExperimentDefinition(
            self.fmu,
            self.custom_function,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
        )

        for variable, value in modifiers_aggregate.items():
            new.variable_modifiers[variable] = (
                str(value) if isinstance(value, Operator) else value
            )
        return new

    def with_extensions(self, experiment_extensions):
        """Sets up an experiment with multiple experiment extensions.

        Parameters:

            experiment_extensions --
                "A list of experiment extension objects."
                "Extension object must an instance of "
                "modelon.impact.client.experiment_definition."
                "SimpleExperimentExtension class."

        Example::

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(custom_function).
            with_extensions(
                [
                    SimpleExperimentExtension().with_modifiers({'PI.k': 20}),
                    SimpleExperimentExtension().with_modifiers({'PI.k': 30}),
                ]
            )

            experiment_definition = fmu.new_experiment_definition(custom_function).
            with_extensions(
                [
                    SimpleExperimentExtension(
                        parameter_modifiers={'start_time': 0.0, 'final_time': 2.0}
                    ).with_modifiers({'PI.k': 20})
                ]
            )
        """

        _assert_valid_extensions(experiment_extensions)
        exp_ext = []
        for extension in experiment_extensions:
            exp_ext.append(extension)

        new = SimpleExperimentDefinition(
            self.fmu,
            self.custom_function,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
        )
        new.variable_modifiers = self.variable_modifiers
        new.extensions = self.extensions + exp_ext
        return new

    def with_cases(self, cases_modifiers):
        """Sets up an experiment with multiple cases with different
        variable modifiers.

        Parameters:

            cases_modifiers --
                A list of variable modifier dictionaries.
                Multiple dictionaries with variable modifiers could to added to create
                multiple cases.

        Example::

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(
                custom_function).with_cases([{'PI.k': 20}, {'PI.k': 30}])
        """
        _assert_valid_case_modifiers(cases_modifiers)

        extensions = [
            SimpleExperimentExtension().with_modifiers(modifiers)
            for modifiers in cases_modifiers
        ]
        return self.with_extensions(extensions)

    def to_dict(self):
        """Returns the experiment definition as a dictionary.

        Returns:

            definition_dict --
                A dictionary containing the experiment definition.

        Example::

            fmu = model.compile().wait()
            simulation_options = custom_function.get_simulation_options()
                .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_def = fmu.new_experiment_definition(custom_function,
            solver_options, simulation_options)
            simulate_def.to_dict()
        """
        return {
            "experiment": {
                "version": 2,
                "base": {
                    "model": {"fmu": {"id": self.fmu.id}},
                    "modifiers": {"variables": self.variable_modifiers},
                    "analysis": {
                        "type": self.custom_function.name,
                        "parameters": self.custom_function.parameter_values,
                        "simulationOptions": self._simulation_options,
                        "solverOptions": self._solver_options,
                        "simulationLogLevel": self._simulation_log_level,
                    },
                },
                "extensions": [ext.to_dict() for ext in self.extensions],
            }
        }


class BaseExperimentExtension(ABC):
    """
    Base class for an experiment extension class.
    """


class SimpleExperimentExtension(BaseExperimentExtension):
    """
    A simple experiment extension class for defining experiement extensions.

    Parameters:

        parameter_modifiers --
            The custom function parameters passes as a dictionary. By default, the
            parameter_modifier is set to None, which means the options set in
            the experiment definition will be used.

        solver_options --
            The solver options to use for this experiment. By default, the solver
            options is set to None, which means the options set in the experiment
            definition will be used.

        simulation_options --
            The simulation_options to use for this experiment. By default the simulation
            options is set to None, which means the options set in the experiment
            definition will be used.

        simulation_log_level --
            Simulation log level for this experiment. Default is 'WARNING'.

    Examples::

        fmu = model.compile().wait()
        simulation_options = custom_function.get_simulation_options()
        .with_values(ncp=500)
        solver_options = {'atol':1e-8}
        simulate_def = fmu.new_experiment_definition(custom_function,
        solver_options, simulation_options).with_modifiers({'inertia1.J': 2})
        simulate_ext = SimpleExperimentExtension(
        {'start_time': 0.0, 'final_time': 4.0},
        solver_options,
        simulation_options.with_values(ncp=600)
        ).with_modifiers({'PI.k': 40})
        simulate_def = simulate_def.with_extensions(simulate_ext)
        simulate_def.to_dict()
    """

    def __init__(
        self,
        parameter_modifiers=None,
        solver_options=None,
        simulation_options=None,
        simulation_log_level=None,
    ):
        self._parameter_modifiers = (
            {} if parameter_modifiers is None else parameter_modifiers
        )
        self._solver_options = (
            {}
            if solver_options is None
            else dict(solver_options)
            if isinstance(solver_options, ExecutionOptions)
            else solver_options
        )
        self._simulation_options = (
            {}
            if simulation_options is None
            else dict(simulation_options)
            if isinstance(simulation_options, ExecutionOptions)
            else simulation_options
        )
        self._simulation_log_level = simulation_log_level
        self.variable_modifiers = {}

    def with_modifiers(self, modifiers=None, **modifiers_kwargs):
        """Sets the modifiers variables for an experiment extension.

        Parameters:

            modifiers --
                A dictionary of variable modifiers. Could be used if
                modifiers keys conflict with python identifiers or keywords.
                Default: None.

            modifiers_kwargs --
                A keyworded, variable-length argument list of variable
                modifiers.

        Example::

            fmu = model.compile().wait()
            simulation_options = custom_function.get_simulation_options()
            .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_ext = SimpleExperimentExtension().with_modifiers({'PI.k': 40})
            simulate_ext = SimpleExperimentExtension(
            {'start_time': 0.0, 'final_time': 4.0},
            solver_options,
            simulation_options
            ).with_modifiers({'PI.k': 40})

        """
        modifiers = {} if modifiers is None else modifiers
        modifiers_aggregate = {**modifiers, **modifiers_kwargs}
        new = SimpleExperimentExtension(
            self._parameter_modifiers,
            self._solver_options,
            self._simulation_options,
            self._simulation_log_level,
        )

        for variable, value in modifiers_aggregate.items():
            if isinstance(value, Operator):
                raise ValueError(
                    "Range operator is not supported when using extentions"
                    " in the experiment"
                )
            new.variable_modifiers[variable] = value
        return new

    def to_dict(self):
        """Returns the experiment extensions as a dictionary.

        Returns:

            extensions_dict --
                A dictionary containing the experiment extensions.

        Example::

            fmu = model.compile().wait()
            simulation_options = custom_function.get_simulation_options()
                .with_values(ncp=500)
            solver_options = {'atol':1e-8}
            simulate_ext = SimpleExperimentExtension(
            {'start_time': 0.0, 'final_time': 4.0},
            solver_options,
            simulation_options,
            ).with_modifiers({'PI.k': 40})
            simulate_ext.to_dict()
        """
        ext_dict = {}
        if self.variable_modifiers:
            ext_dict["modifiers"] = {"variables": self.variable_modifiers}

        if self._parameter_modifiers:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["parameters"] = self._parameter_modifiers

        if self._solver_options:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["solverOptions"] = self._solver_options

        if self._simulation_options:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["simulationOptions"] = self._simulation_options

        if self._simulation_log_level:
            ext_dict.setdefault("analysis", {})
            ext_dict["analysis"]["simulationLogLevel"] = self._simulation_log_level

        return ext_dict
