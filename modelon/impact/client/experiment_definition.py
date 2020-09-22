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
    """

    def __init__(
        self,
        fmu,
        custom_function,
        solver_options=None,
        simulation_options=None,
        simulation_log_level="WARNING",
    ):
        """
        Parameters::

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
        """
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
        self.simulation_log_level = simulation_log_level
        self.variable_modifiers = {}

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
        """ Sets the modifiers parameters for an experiment.

        Parameters::

            modifiers --
                A dictionary of variable modifiers. Could be used if
                modifiers keys conflict with python identifiers or keywords.
                Default: None.

            modifiers_kwargs --
                A keyworded, variable-length argument list of variable
                modifiers.

        Example::

            from modelon.impact.client import Range

            fmu = model.compile().wait()
            experiment_definition = fmu.new_experiment_definition(
                custom_function).with_modifiers({'inertia1.J': 2,
                'inertia2.J': Range(0.1, 0.5, 3)}, k=2, w=7)
        """
        modifiers = {} if modifiers is None else modifiers
        modifiers_aggregate = {**modifiers, **modifiers_kwargs}
        new = SimpleExperimentDefinition(
            self.fmu,
            self.custom_function,
            self._solver_options,
            self._simulation_options,
            self.simulation_log_level,
        )

        for variable, value in modifiers_aggregate.items():
            new.variable_modifiers[variable] = (
                str(value) if isinstance(value, Operator) else value
            )
        return new

    def to_dict(self):
        """ Returns the experiment definition as a dictionary.

        Returns::

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
                "analysis": {
                    "analysis_function": self.custom_function.name,
                    "parameters": self.custom_function.parameter_values,
                    "simulation_options": self._simulation_options,
                    "solver_options": self._solver_options,
                    "simulation_log_level": self.simulation_log_level,
                },
                "fmu_id": self.fmu.id,
                "modifiers": {"variables": self.variable_modifiers},
            }
        }
