from modelon.impact.client.options import ExecutionOptions
from modelon.impact.client.entities.model import Model
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.entities.model_executable import ModelExecutable


def assert_valid_args(
    model=None,
    fmu=None,
    custom_function=None,
    solver_options=None,
    simulation_options=None,
    compiler_options=None,
    runtime_options=None,
):
    if fmu and not isinstance(fmu, ModelExecutable):
        raise TypeError("FMU must be an instance of ModelExecutable class!")
    if model and not isinstance(model, Model):
        raise TypeError("Model must be an instance of Model class!")
    if custom_function and not isinstance(custom_function, CustomFunction):
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
    if compiler_options is not None and not isinstance(
        compiler_options, (ExecutionOptions, dict)
    ):
        raise TypeError(
            "Compiler options object must either be a dictionary or an "
            "instance of modelon.impact.client.options.ExecutionOptions class!"
        )
    if runtime_options is not None and not isinstance(
        runtime_options, (ExecutionOptions, dict)
    ):
        raise TypeError(
            "Runtime options object must either be a dictionary or an "
            "instance of modelon.impact.client.options.ExecutionOptions class!"
        )
