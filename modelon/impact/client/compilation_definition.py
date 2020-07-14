from abc import ABC


class BaseCompilationDefinition(ABC):
    pass


class SimpleCompilationDefinition(BaseCompilationDefinition):
    def __init__(
        self,
        model,
        compiler_options=None,
        runtime_options=None,
        compiler_log_level="info",
        fmi_target="me",
        fmi_version="2.0",
        platform="win64",
    ):
        self.model = model
        self.compiler_options = compiler_options or {}
        self.runtime_options = runtime_options or {}
        self.compiler_log_level = compiler_log_level
        self.fmi_target = fmi_target
        self.fmi_version = fmi_version
        self.platform = platform

    @property
    def to_dict(self):
        {
            "input": {
                "class_name": self.model.class_name,
                "compiler_options": self.compiler_options,
                "runtime_options": self.runtime_options,
                "compiler_log_level": self.compiler_log_level,
                "fmi_target": self.fmi_target,
                "fmi_version": self.fmi_version,
                "platform": self.platform,
            }
        }
