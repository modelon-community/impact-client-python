from abc import ABC


class BaseExperimentDefinition(ABC):
    pass


class SimpleExperimentDefinition(BaseExperimentDefinition):
    def __init__(
        self,
        fmu,
        custom_function,
        simulation_options=None,
        solver_options=None,
        simulation_log_level="WARNING",
        variables=None,
    ):
        self.fmu = fmu
        self.custom_function = custom_function
        self.simulation_options = simulation_options or {}
        self.solver_options = solver_options or {}
        self.simulation_log_level = simulation_log_level
        self.variables = variables or {}

    @property
    def to_dict(self):
        return {
            "experiment": {
                "analysis": {
                    "analysis_function": self.custom_function.name,
                    "parameters": self.custom_function.parameter_values,
                    "simulation_options": self.simulation_options,
                    "solver_options": self.solver_options,
                    "simulation_log_level": self.simulation_log_level,
                },
                "fmu_id": self.fmu.id,
                "modifiers": {"variables": self.variables},
            }
        }
