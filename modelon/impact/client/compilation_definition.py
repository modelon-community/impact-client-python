from abc import ABC
import modelon.impact.client.entities as entities
from modelon.impact.client.options import ExecutionOption


def _assert_valid_args(model, options):
    if not isinstance(model, entities.Model):
        raise TypeError("Model must be an instance of Model class")
    if not isinstance(options, ExecutionOption):
        raise TypeError("Options must be an instance of ExecutionOption class")


class BaseCompilationDefinition(ABC):
    pass


class SimpleCompilationDefinition(BaseCompilationDefinition):
    def __init__(
        self,
        model,
        options,
        compiler_log_level="info",
        fmi_target="me",
        fmi_version="2.0",
        platform="auto",
    ):
        _assert_valid_args(model, options)
        self.model = model
        self.options = options
        self.compiler_log_level = compiler_log_level
        self.fmi_target = fmi_target
        self.fmi_version = fmi_version
        self.platform = platform

    def to_dict(self):
        return {
            "input": {
                "class_name": self.model.class_name,
                "compiler_options": self.options.compiler().values,
                "runtime_options": self.options.runtime().values,
                "compiler_log_level": self.compiler_log_level,
                "fmi_target": self.fmi_target,
                "fmi_version": self.fmi_version,
                "platform": self.platform,
            }
        }
