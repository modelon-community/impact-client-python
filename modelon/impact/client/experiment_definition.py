from modelon.impact.client import entities
from abc import ABC, abstractmethod
from modelon.impact.client.options import ExecutionOption
from modelon.impact.client import exceptions


def _assert_valid_args(fmu, custom_function, options):
    if not isinstance(fmu, entities.ModelExecutable):
        raise TypeError("Fmu must be an instance of ModelExecutable class")
    if not isinstance(custom_function, entities.CustomFunction):
        raise TypeError("Custom_function must be an instance of CustomFunction class")
    if not isinstance(options, ExecutionOption):
        raise TypeError("Options must be an instance of ExecutionOption class")


def _assert_settable_parameters(fmu, **variables):
    add = set(variables.keys()) - set(fmu.settable_parameters())
    if add:
        raise KeyError(
            f"Paramter(s) '{', '.join(add)}' {'are' if len(add)>1 else 'is'} "
            "not a valid parameter modifier! Settable parameters"
            f" are {fmu.settable_parameters()}"
        )


def _assert_successful_compilation(fmu):
    if not fmu.is_successful():
        raise exceptions.OperationFailureError(
            "Compilation process has failed! See the log for more info!"
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
    """

    def __init__(self, start_value, end_value, no_of_steps):
        self.start_value = start_value
        self.end_value = end_value
        self.no_of_steps = no_of_steps

    def __str__(self):
        return f"range({self.start_value},{self.end_value},{self.no_of_steps})"


class BaseExperimentDefinition(ABC):
    """
    Base class for an ExperimentDefinition class.
    """

    pass


class SimpleExperimentDefinition(BaseExperimentDefinition):
    """
    A Simple ExperimentDefinition class for creating experiement definitions.
    """

    def __init__(
        self, fmu, custom_function, options, simulation_log_level="WARNING",
    ):
        _assert_valid_args(fmu, custom_function, options)
        _assert_successful_compilation(fmu)
        self.fmu = fmu
        self.custom_function = custom_function
        self.options = options
        self.simulation_log_level = simulation_log_level
        self.variable_modifiers = {}

    def with_modifiers(self, **modifiers):
        """ Sets the modifiers parameters for an experiment.

        Parameters::

            modifiers --
                A keyworded, variable-length argument list of variable
                modifiers.

        Example::
            from modelon.impact.client.experiment_definition import
            SimpleExperimentDefinition, Range

            options = custom_function.options()
            simulate_def = SimpleExperimentDefinition(fmu, custom_function, options)
            .with_modifiers(h0 = 1, e = Range(0.1, 0.5, 3))
        """
        _assert_settable_parameters(self.fmu, **modifiers)
        new = SimpleExperimentDefinition(
            self.fmu, self.custom_function, self.options, self.simulation_log_level
        )

        for variable, value in modifiers.items():
            new.variable_modifiers[variable] = (
                str(value) if isinstance(value, Operator) else value
            )
        return new

    def to_dict(self):
        """ Returns the experiment specification as a dictionary.

        Returns::

            specification_dict --
                A dictionary containing the experiment definition.

        Example::
            from modelon.impact.client.experiment_definition import
            SimpleExperimentDefinition

            options = custom_function.options()
            simulate_def = SimpleExperimentDefinition(fmu, custom_function, options)
            simulate_def.to_dict()
        """
        return {
            "experiment": {
                "analysis": {
                    "analysis_function": self.custom_function.name,
                    "parameters": self.custom_function.parameter_values,
                    "simulation_options": self.options.to_dict()["simulation"],
                    "solver_options": self.options.to_dict()["solver"],
                    "simulation_log_level": self.simulation_log_level,
                },
                "fmu_id": self.fmu.id,
                "modifiers": {"variables": self.variable_modifiers},
            }
        }