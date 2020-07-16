from abc import ABC


class BaseExperimentDefinition(ABC):
    pass


class SimpleExperimentDefinition(BaseExperimentDefinition):
    def __init__(
        self,
        fmu,
        custom_function,
        options,
        simulation_log_level="WARNING",
        variables=None,
    ):
        self.fmu = fmu
        self.custom_function = custom_function
        self.options = options
        self.simulation_log_level = simulation_log_level
        self.variables = variables or {}

    @property
    def to_dict(self):
        return {
            "experiment": {
                "analysis": {
                    "analysis_function": self.custom_function.name,
                    "parameters": self.custom_function.parameter_values,
                    "simulation_options": self.options.simulation.values,
                    "solver_options": self.options.solver.values,
                    "simulation_log_level": self.simulation_log_level,
                },
                "fmu_id": self.fmu.id,
                "modifiers": {"variables": self.variables},
            }
        }
