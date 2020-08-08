from abc import ABC
import collections as col
from modelon.impact.client.operations import (
    ModelExecutable,
    _assert_successful_operation,
)
import modelon.impact.client.entities as entities
from modelon.impact.client.options import ExecutionOption

BatchSim = col.namedtuple(
    "Variable", ["variable_name", "start_value", "end_value", "no_of_steps"]
)


def _assert_valid_args(fmu, custom_function, options):
    if not isinstance(fmu, ModelExecutable):
        raise TypeError("Fmu must be an instance of ModelExecutable class")
    if not isinstance(custom_function, entities.CustomFunction):
        raise TypeError("Custom_function must be an instance of CustomFunction class")
    if not isinstance(options, ExecutionOption):
        raise TypeError("Options must be an instance of ExecutionOption class")


class BaseExperimentDefinition(ABC):
    pass


class SimpleExperimentDefinition(BaseExperimentDefinition):
    def __init__(
        self, fmu, custom_function, options, *batch, simulation_log_level="WARNING",
    ):
        _assert_valid_args(fmu, custom_function, options)
        _assert_successful_operation(fmu, "Compilation")
        self.fmu = fmu
        self.custom_function = custom_function
        self.options = options
        self.batch = batch
        self.simulation_log_level = simulation_log_level

    def to_dict(self):
        return {
            "experiment": {
                "analysis": {
                    "analysis_function": self.custom_function.name,
                    "parameters": self.custom_function.parameter_values,
                    "simulation_options": self.options.simulation().values,
                    "solver_options": self.options.solver().values,
                    "simulation_log_level": self.simulation_log_level,
                },
                "fmu_id": self.fmu.id,
                "modifiers": {
                    "variables": {
                        f"{value.variable_name}": f"range({value.start_value},"
                        f"{value.end_value},{value.no_of_steps})"
                        for value in self.batch
                    }
                    if self.batch
                    else {}
                },
            }
        }
