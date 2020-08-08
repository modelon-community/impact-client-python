import modelon.impact.client.compilation_definition as compilation_definition
import pytest
from tests.impact.client.fixtures import *


def test_compilation_definition(model, options):
    spec = compilation_definition.SimpleCompilationDefinition(
        model=model, options=options
    )
    config = spec.to_dict()
    assert config == {
        "input": {
            "class_name": "Test.PID",
            "compiler_options": {"c_compiler": "gcc"},
            "runtime_options": {"log_level": 3},
            "compiler_log_level": "info",
            "fmi_target": "me",
            "fmi_version": "2.0",
            "platform": "auto",
        }
    }


def test_invalid_option_input(model, options):
    pytest.raises(
        TypeError, compilation_definition.SimpleCompilationDefinition, options, model,
    )


def test_invalid_model_input(model, fmu):
    pytest.raises(
        TypeError, compilation_definition.SimpleCompilationDefinition, model, fmu
    )
