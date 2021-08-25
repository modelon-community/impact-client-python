from modelon.impact.client import (
    SimpleFMUExperimentDefinition,
    SimpleModelicaExperimentDefinition,
    Range,
    Choices,
    SimpleExperimentExtension,
)
import pytest
from modelon.impact.client import exceptions

from tests.impact.client.fixtures import *


class TestSimpleFMUExperimentDefinition:
    def test_experiment_definition_default_options(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
        )
        config = definition.to_dict()
        assert config == {
            "experiment": {
                "version": 2,
                "base": {
                    "model": {"fmu": {"id": "Test"}},
                    "modifiers": {'variables': {}},
                    "analysis": {
                        "type": "dynamic",
                        "parameters": {},
                        "simulationOptions": {"ncp": 500},
                        "solverOptions": {},
                        "simulationLogLevel": "WARNING",
                    },
                },
                "extensions": [],
            }
        }

    def test_experiment_definition_with_options(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu,
            custom_function=custom_function_no_param,
            simulation_options=custom_function_no_param.get_simulation_options().with_values(
                ncp=2000, rtol=0.0001
            ),
            solver_options={'a': 1},
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["analysis"]["simulationOptions"] == {
            "ncp": 2000,
            "rtol": 0.0001,
        }
        assert config["experiment"]["base"]["analysis"]["solverOptions"] == {"a": 1}

    def test_experiment_definition_with_modifier(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        ).with_modifiers({'h0': Range(0.1, 0.5, 3)}, v=Choices(0.1, 0.5, 3))
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {
            'h0': 'range(0.1,0.5,3)',
            'v': 'choices(0.1, 0.5, 3)',
        }

    def test_experiment_definition_with_choices_1_input_modifier(
        self, fmu, custom_function_no_param
    ):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        ).with_modifiers(v=Choices(0.1))
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {
            'v': 'choices(0.1)',
        }

    def test_experiment_definition_with_fmu_modifiers(
        self, fmu_with_modifiers, custom_function_no_param
    ):
        definition = SimpleFMUExperimentDefinition(
            fmu_with_modifiers, custom_function=custom_function_no_param,
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {'PI.K': 20}

    def test_experiment_definition_with_extensions(self, fmu, custom_function_no_param):
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = SimpleExperimentExtension({'final_time': 10}).with_modifiers(p=3)
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {
                "modifiers": {"variables": {"p": 3}},
                "analysis": {"parameters": {'final_time': 10}},
            },
        ]

    def test_experiment_definition_with_cases(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        ).with_cases([{'p': 2}, {'p': 3}])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {"modifiers": {"variables": {"p": 3}}},
        ]

    def test_failed_compile_exp_def(
        self,
        fmu_compile_failed,
        custom_function_no_param,
        solver_options,
        simulation_options,
    ):
        pytest.raises(
            exceptions.OperationFailureError,
            SimpleFMUExperimentDefinition,
            fmu_compile_failed,
            custom_function_no_param,
            solver_options,
            simulation_options,
        )

    def test_cancelled_compile_exp_def(
        self,
        fmu_compile_cancelled,
        custom_function_no_param,
        solver_options,
        simulation_options,
    ):
        pytest.raises(
            exceptions.OperationFailureError,
            SimpleFMUExperimentDefinition,
            fmu_compile_cancelled,
            custom_function_no_param,
            solver_options,
            simulation_options,
        )

    def test_invalid_option_input(self, custom_function, custom_function_no_param):
        pytest.raises(
            TypeError,
            SimpleFMUExperimentDefinition,
            custom_function,
            custom_function_no_param,
            {},
        )

    def test_invalid_fmu_input(self, fmu, custom_function_no_param):
        pytest.raises(
            TypeError,
            SimpleFMUExperimentDefinition,
            fmu,
            custom_function_no_param,
            "",
            "",
        )


class TestSimpleExperimentExtension:
    def test_experiment_extension_default_options(self):
        ext = SimpleExperimentExtension()
        config = ext.to_dict()
        assert config == {}

    def test_experiment_extension_with_options(self, custom_function_no_param):
        ext = SimpleExperimentExtension(
            {'stop_time': 5},
            {'a': 1},
            custom_function_no_param.get_simulation_options().with_values(
                ncp=2000, rtol=0.0001
            ),
        )
        config = ext.to_dict()
        assert config == {
            "analysis": {
                "parameters": {'stop_time': 5},
                "simulationOptions": {'ncp': 2000, 'rtol': 0.0001},
                "solverOptions": {'a': 1},
            },
        }

    def test_experiment_extension_with_modifiers(self):
        ext = SimpleExperimentExtension().with_modifiers({'PI.k': 10}, P=5, d=15)
        config = ext.to_dict()
        assert config == {
            "modifiers": {"variables": {'PI.k': 10, 'P': 5, 'd': 15}},
        }

    def test_experiment_extension_with_range_modifier(self):
        ext = SimpleExperimentExtension()
        pytest.raises(ValueError, ext.with_modifiers, {'h0': Range(0.1, 0.5, 3)})

    def test_experiment_extension_with_choices_modifier(self):
        ext = SimpleExperimentExtension()
        pytest.raises(ValueError, ext.with_modifiers, {'h0': Choices(0.1, 0.5, 3)})

    def test_invalid_with_extensions_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        )
        pytest.raises(TypeError, definition.with_extensions, {})

    def test_invalid_with_extensions_list_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        )
        pytest.raises(TypeError, definition.with_extensions, [{}])

    def test_invalid_with_cases_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        )
        pytest.raises(TypeError, definition.with_cases, {})

    def test_invalid_with_cases_list_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param,
        )
        pytest.raises(TypeError, definition.with_cases, [[]])


class TestSimpleModelicaExperimentDefinition:
    def test_experiment_definition_default_options(
        self, model, custom_function_no_param
    ):
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param
        )
        config = definition.to_dict()
        assert config == {
            "experiment": {
                "version": 2,
                "base": {
                    "model": {
                        "modelica": {
                            "className": "Test.PID",
                            "compilerOptions": {"c_compiler": "gcc"},
                            "runtimeOptions": {},
                            "compilerLogLevel": 'warning',
                            "fmiTarget": 'me',
                            "fmiVersion": '2.0',
                            "platform": 'auto',
                        }
                    },
                    "modifiers": {'variables': {}},
                    "analysis": {
                        "type": "dynamic",
                        "parameters": {},
                        "simulationOptions": {"ncp": 500},
                        "solverOptions": {},
                        "simulationLogLevel": "WARNING",
                    },
                },
                "extensions": [],
            }
        }

    def test_experiment_definition_with_options(self, model, custom_function_no_param):
        definition = SimpleModelicaExperimentDefinition(
            model,
            custom_function=custom_function_no_param,
            compiler_options=custom_function_no_param.get_compiler_options().with_values(
                a=2, b=1
            ),
            runtime_options={'d': 1},
            simulation_options=custom_function_no_param.get_simulation_options().with_values(
                ncp=2000, rtol=0.0001
            ),
            solver_options={'a': 1},
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["model"]["modelica"]["compilerOptions"] == {
            "a": 2,
            "b": 1,
            'c_compiler': 'gcc',
        }
        assert config["experiment"]["base"]["model"]["modelica"]["runtimeOptions"] == {
            "d": 1,
        }
        assert config["experiment"]["base"]["analysis"]["simulationOptions"] == {
            "ncp": 2000,
            "rtol": 0.0001,
        }
        assert config["experiment"]["base"]["analysis"]["solverOptions"] == {"a": 1}

    def test_experiment_definition_with_modifier(self, model, custom_function_no_param):
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param,
        ).with_modifiers({'h0': Range(0.1, 0.5, 3), 'v': Choices(0.1, 0.5, 3)})
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {
            'h0': 'range(0.1,0.5,3)',
            'v': 'choices(0.1, 0.5, 3)',
        }

    def test_experiment_definition_initialize_from_experiment(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param,
        ).initialize_from(experiment)
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["initializeFrom"] == 'Test'

    def test_experiment_definition_initialize_from_case(
        self, model, custom_function_no_param, experiment
    ):
        case_1 = experiment.entity.get_case('case_1')
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param,
        ).initialize_from(case_1)
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["initializeFromCase"] == {
            'experimentId': 'Test',
            'caseId': 'case_1',
        }

    def test_experiment_definition_with_extensions(
        self, model, custom_function_no_param
    ):
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = SimpleExperimentExtension({'final_time': 10}).with_modifiers(p=3)
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param,
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {
                "modifiers": {"variables": {"p": 3}},
                "analysis": {"parameters": {'final_time': 10}},
            },
        ]

    def test_experiment_definition_with_extensions_initialize_from_experiment(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = (
            SimpleExperimentExtension({'final_time': 10})
            .with_modifiers(p=3)
            .initialize_from(experiment)
        )
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param,
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {
                "modifiers": {'initializeFrom': 'Test', "variables": {"p": 3}},
                "analysis": {"parameters": {'final_time': 10}},
            },
        ]

    def test_experiment_definition_with_extensions_initialize_from_case(
        self, model, custom_function_no_param, experiment
    ):
        case_1 = experiment.entity.get_case('case_1')
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = (
            SimpleExperimentExtension({'final_time': 10})
            .with_modifiers(p=3)
            .initialize_from(case_1)
        )
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param,
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {
                "modifiers": {
                    'initializeFromCase': {'experimentId': 'Test', 'caseId': 'case_1'},
                    "variables": {"p": 3},
                },
                "analysis": {"parameters": {'final_time': 10}},
            },
        ]

    def test_experiment_definition_with_cases(self, model, custom_function_no_param):
        definition = SimpleModelicaExperimentDefinition(
            model, custom_function=custom_function_no_param,
        ).with_cases([{'p': 2}, {'p': 3}])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {"modifiers": {"variables": {"p": 3}}},
        ]

    def test_invalid_option_input(self, custom_function, custom_function_no_param):
        pytest.raises(
            TypeError,
            SimpleModelicaExperimentDefinition,
            custom_function,
            custom_function_no_param,
            {},
        )

    def test_invalid_model_input(self, fmu, model, custom_function_no_param):
        pytest.raises(
            TypeError,
            SimpleModelicaExperimentDefinition,
            fmu,
            custom_function_no_param,
        )
