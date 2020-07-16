from abc import ABC


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
        self.model = model
        self.options = options
        self.compiler_log_level = compiler_log_level
        self.fmi_target = fmi_target
        self.fmi_version = fmi_version
        self.platform = platform

    @property
    def to_dict(self):
        return {
            "input": {
                "class_name": self.model.class_name,
                "compiler_options": self.options.compiler.values,
                "runtime_options": self.options.runtime.values,
                "compiler_log_level": self.compiler_log_level,
                "fmi_target": self.fmi_target,
                "fmi_version": self.fmi_version,
                "platform": self.platform,
            }
        }
