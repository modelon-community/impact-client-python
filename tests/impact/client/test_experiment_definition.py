from unittest import mock
from modelon.impact.client.entities.result import Result
from modelon.impact.client import (
    SimpleFMUExperimentDefinition,
    SimpleModelicaExperimentDefinition,
    Range,
    Choices,
    Uniform,
    Beta,
    Normal,
    SimpleExperimentExtension,
    Sobol,
    LatinHypercube,
)
import pytest
import copy
from modelon.impact.client import exceptions
from tests.impact.client.helpers import (
    create_external_result_entity,
    create_case_entity,
    IDs,
)


_EXPECTED_FMU_EXP = {
    "experiment": {
        "version": 2,
        "base": {
            "model": {"fmu": {"id": IDs.FMU_PRIMARY}},
            "modifiers": {
                'variables': {'h0': 'range(0.1,0.5,3)'},
                'initializeFrom': IDs.EXPERIMENT_PRIMARY,
            },
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
_EXPECTED_MODELICA_EXP = {
    "experiment": {
        "version": 2,
        "base": {
            "model": {
                "modelica": {
                    "className": IDs.LOCAL_MODELICA_CLASS_PATH,
                    "compilerOptions": {"c_compiler": "gcc"},
                    "runtimeOptions": {},
                    "compilerLogLevel": 'warning',
                    "fmiTarget": 'me',
                    "fmiVersion": '2.0',
                    "platform": 'auto',
                }
            },
            "modifiers": {
                'variables': {'h0': 'range(0.1,0.5,3)'},
                "initializeFrom": IDs.EXPERIMENT_PRIMARY,
            },
            "analysis": {
                "type": "dynamic",
                "parameters": {},
                "simulationOptions": {"ncp": 500},
                "solverOptions": {},
                "simulationLogLevel": "WARNING",
            },
            "expansion": {"algorithm": "FULLFACTORIAL"},
        },
        "extensions": [],
    }
}


def get_experiment_extension_with_case_label_init_modifier():
    return {
        "analysis": {
            "parameters": {'stop_time': 5},
            "simulationOptions": {'ncp': 2000, 'rtol': 0.0001},
            "solverOptions": {'a': 1},
            'simulationLogLevel': 'Warning',
        },
        "modifiers": {
            'initializeFrom': IDs.EXPERIMENT_PRIMARY,
            "variables": {'PI.k': 10, 'P': 5, 'd': 15},
        },
        'caseData': [{'label': 'Cruise condition'}],
    }


def get_base_ext(custom_function_no_param):
    return SimpleExperimentExtension(
        {'stop_time': 5},
        {'a': 1},
        custom_function_no_param.get_simulation_options().with_values(
            ncp=2000, rtol=0.0001
        ),
        simulation_log_level="Warning",
    )


def get_expected_with_ext_first(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["extensions"] = [
        {"modifiers": {"variables": {"t": 2}}},
        {"modifiers": {"variables": {"p": 3}}},
    ]
    return expected


def get_expected_with_cases_first(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["extensions"] = [
        {"modifiers": {"variables": {"p": 3}}},
        {"modifiers": {"variables": {"t": 2}}},
    ]
    return expected


def get_expected_with_sobol_expansion(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["base"]["modifiers"] = {
        "variables": {'h0': 'uniform(0.1,0.5)'}
    }
    expected["experiment"]["base"]["expansion"] = {
        "algorithm": "SOBOL",
        "parameters": {'samples': 5},
    }
    return expected


def get_expected_with_lhs_expansion(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["base"]["modifiers"] = {
        "variables": {'h0': 'normal(0.1,0.5,-inf,inf)'}
    }
    expected["experiment"]["base"]["expansion"] = {
        "algorithm": "LATINHYPERCUBE",
        "parameters": {'samples': 5, 'seed': 1},
    }
    return expected


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
                    "model": {"fmu": {"id": IDs.FMU_PRIMARY}},
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

    def test_experiment_definition_order_1(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_2(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_cases([{'p': 3}])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_3(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_4(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_5(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_6(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_7(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_8(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_9(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_10(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_11(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_12(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_13(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_14(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_ext_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_cases([{'p': 3}])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_15(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_16(
        self, fmu, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        expected = get_expected_with_cases_first(_EXPECTED_FMU_EXP)
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        exp_def = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

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
            fmu, custom_function=custom_function_no_param
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
            fmu, custom_function=custom_function_no_param
        ).with_modifiers(v=Choices(0.1))
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {
            'v': 'choices(0.1)',
        }

    def test_experiment_definition_with_fmu_modifiers(
        self, fmu_with_modifiers, custom_function_no_param
    ):
        definition = SimpleFMUExperimentDefinition(
            fmu_with_modifiers, custom_function=custom_function_no_param
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {'PI.K': 20}

    def test_experiment_definition_with_extensions(self, fmu, custom_function_no_param):
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = SimpleExperimentExtension({'final_time': 10}).with_modifiers(p=3)
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
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
            fmu,
            custom_function=custom_function_no_param,
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

    def test_experiment_extension_with_case_label(self):
        ext = SimpleExperimentExtension().with_case_label('Cruise condition')
        config = ext.to_dict()
        assert config == {'caseData': [{'label': 'Cruise condition'}]}

    def test_experiment_extension_order_1(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_modifiers({'PI.k': 10}, P=5, d=15)
            .with_initialize_from(experiment)
            .with_case_label('Cruise condition')
            .to_dict()
        )
        assert ext == expected_output

    def test_experiment_extension_order_2(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_initialize_from(experiment)
            .with_modifiers({'PI.k': 10}, P=5, d=15)
            .with_case_label('Cruise condition')
            .to_dict()
        )
        assert ext == expected_output

    def test_experiment_extension_order_3(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_initialize_from(experiment)
            .with_case_label('Cruise condition')
            .with_modifiers({'PI.k': 10}, P=5, d=15)
            .to_dict()
        )
        assert ext == expected_output

    def test_experiment_extension_order_4(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_case_label('Cruise condition')
            .with_initialize_from(experiment)
            .with_modifiers({'PI.k': 10}, P=5, d=15)
        ).to_dict()
        assert ext == expected_output

    def test_experiment_extension_order_5(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_case_label('Cruise condition')
            .with_modifiers({'PI.k': 10}, P=5, d=15)
            .with_initialize_from(experiment)
        ).to_dict()
        assert ext == expected_output

    def test_experiment_extension_order_6(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_modifiers({'PI.k': 10}, P=5, d=15)
            .with_initialize_from(experiment)
            .with_case_label('Cruise condition')
        ).to_dict()
        assert ext == expected_output

    def test_experiment_extension_with_range_modifier(self):
        ext = SimpleExperimentExtension()
        pytest.raises(ValueError, ext.with_modifiers, {'h0': Range(0.1, 0.5, 3)})

    def test_experiment_extension_with_choices_modifier(self):
        ext = SimpleExperimentExtension()
        pytest.raises(ValueError, ext.with_modifiers, {'h0': Choices(0.1, 0.5, 3)})

    def test_invalid_with_extensions_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
        )
        pytest.raises(TypeError, definition.with_extensions, {})

    def test_invalid_with_extensions_list_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
        )
        pytest.raises(TypeError, definition.with_extensions, [{}])

    def test_invalid_with_cases_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
        )
        pytest.raises(TypeError, definition.with_cases, {})

    def test_invalid_with_cases_list_input(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
        )
        pytest.raises(TypeError, definition.with_cases, [[]])


class TestSimpleModelicaExperimentDefinition:
    def test_experiment_definition_default_options(
        self, model, custom_function_no_param
    ):
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        )
        config = definition.to_dict()
        assert config == {
            "experiment": {
                "version": 2,
                "base": {
                    "model": {
                        "modelica": {
                            "className": IDs.LOCAL_MODELICA_CLASS_PATH,
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
                    "expansion": {"algorithm": "FULLFACTORIAL"},
                },
                "extensions": [],
            },
        }

    def test_experiment_definition_with_sobol_expansion(
        self, model, custom_function_no_param
    ):
        expected = get_expected_with_sobol_expansion(_EXPECTED_MODELICA_EXP)
        definition = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_modifiers({'h0': Uniform(0.1, 0.5)})
            .with_expansion(expansion=Sobol(5))
            .to_dict()
        )

        assert definition == expected

    def test_experiment_definition_with_lhs_expansion(
        self, model, custom_function_no_param
    ):
        expected = get_expected_with_lhs_expansion(_EXPECTED_MODELICA_EXP)
        definition = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_modifiers({'h0': Normal(0.1, 0.5)})
            .with_expansion(expansion=LatinHypercube(5, 1))
            .to_dict()
        )

        assert definition == expected

    def test_experiment_definition_order_1(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .to_dict()
        )

        assert exp_def == expected

    def test_experiment_definition_order_2(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_cases([{'p': 3}])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_3(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_4(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_5(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_6(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_7(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_8(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_9(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_10(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_11(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_12(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_13(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_extensions([ext])
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_14(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_ext_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_cases([{'p': 3}])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_15(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_cases([{'p': 3}])
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_order_16(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext = SimpleExperimentExtension().with_modifiers(t=2)
        expected = get_expected_with_cases_first(_EXPECTED_MODELICA_EXP)
        exp_def = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_modifiers({'h0': Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{'p': 3}])
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_with_options(self, model, custom_function_no_param):
        definition = SimpleModelicaExperimentDefinition(
            model.entity,
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

    def test_experiment_definition_with_operator_modifier(
        self, model, custom_function_no_param
    ):
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_modifiers({'h0': Range(0.1, 0.5, 3), 'v': Choices(0.1, 0.5, 3)})
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {
            'h0': 'range(0.1,0.5,3)',
            'v': 'choices(0.1, 0.5, 3)',
        }

    def test_experiment_definition_with_distribution_modifier(
        self, model, custom_function_no_param
    ):
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_modifiers(
            {'h0': Uniform(0.1, 0.5), 'v': Beta(0.1, 0.5), 't': Normal(0.1, 0.5, -5)}
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == {
            'h0': 'uniform(0.1,0.5)',
            'v': 'beta(0.1,0.1)',
            't': 'normal(0.1,0.5,-5,inf)',
        }

    def test_experiment_definition_initialize_from_result(
        self,
        model,
        custom_function_no_param,
        workspace_ops,
        upload_result,
        upload_result_status_ready,
        upload_result_meta,
    ):
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            result = workspace_ops.upload_result(
                "test.mat", IDs.WORKSPACE_PRIMARY
            ).wait()
            mock_file.assert_called_with("test.mat", "rb")

        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_initialize_from(result)
        config = definition.to_dict()
        assert (
            config["experiment"]["base"]["modifiers"]["initializeFromExternalResult"]
            == result.id
        )

    def test_experiment_definition_initialize_from_experiment(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_initialize_from(experiment)
        config = definition.to_dict()
        assert (
            config["experiment"]["base"]["modifiers"]["initializeFrom"] == experiment.id
        )

    def test_experiment_definition_initialize_from_case(
        self, model, custom_function_no_param, experiment
    ):
        case_1 = experiment.entity.get_case(IDs.CASE_PRIMARY)
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_initialize_from(case_1)
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["initializeFromCase"] == {
            "experimentId": case_1.experiment_id,
            "caseId": case_1.id,
        }

    def test_experiment_definition_initialize_from_multiple_entities(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        definition = SimpleModelicaExperimentDefinition(
            model.entity,
            custom_function=custom_function_no_param,
            initialize_from=experiment,
        )

        # Reinitializing with case entity
        case_to_init = create_case_entity(
            'Case_2', IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        definition = definition.with_initialize_from(case_to_init)
        modifiers = definition.to_dict()["experiment"]["base"]["modifiers"]
        assert len(modifiers) == 2
        assert modifiers["initializeFromCase"] == {
            "experimentId": case_to_init.experiment_id,
            "caseId": case_to_init.id,
        }

        # Reinitializing with external result entity
        result_to_init = create_external_result_entity('result_id')
        definition = definition.with_initialize_from(result_to_init)
        modifiers = definition.to_dict()["experiment"]["base"]["modifiers"]
        assert len(modifiers) == 2
        assert modifiers["initializeFromExternalResult"] == result_to_init.id

    def test_experiment_definition_with_extensions(
        self, model, custom_function_no_param
    ):
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = SimpleExperimentExtension({'final_time': 10}).with_modifiers(p=3)
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {
                "modifiers": {"variables": {"p": 3}},
                "analysis": {"parameters": {'final_time': 10}},
            },
        ]

    def test_experiment_definition_with_extensions_initialize_from_result(self):
        ext = SimpleExperimentExtension()
        pytest.raises(TypeError, ext.with_initialize_from, Result)

    def test_experiment_definition_with_extensions_initialize_from_experiment(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = SimpleExperimentExtension({'final_time': 10}).with_modifiers(p=3)
        ext2 = ext2.with_initialize_from(experiment)
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {
                "modifiers": {'initializeFrom': experiment.id, "variables": {"p": 3}},
                "analysis": {"parameters": {'final_time': 10}},
            },
        ]

    def test_experiment_definition_with_extensions_initialize_from_case(
        self, model, custom_function_no_param, experiment
    ):
        case_1 = experiment.entity.get_case(IDs.CASE_PRIMARY)
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = (
            SimpleExperimentExtension({'final_time': 10})
            .with_modifiers(p=3)
            .with_initialize_from(case_1)
        )
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {"modifiers": {"variables": {"p": 2}}},
            {
                "modifiers": {
                    "initializeFromCase": {
                        "experimentId": case_1.experiment_id,
                        "caseId": case_1.id,
                    },
                    "variables": {"p": 3},
                },
                "analysis": {"parameters": {'final_time': 10}},
            },
        ]

    def test_experiment_definition_with_extensions_initialize_from_multiple_entities(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        case_1 = experiment.get_case(IDs.CASE_PRIMARY)
        ext1 = SimpleExperimentExtension({'final_time': 10}).with_modifiers(p=3)
        ext1 = ext1.with_initialize_from(case_1)
        modifiers = ext1.to_dict()['modifiers']
        assert len(modifiers) == 2
        assert modifiers['initializeFromCase'] == {
            "experimentId": case_1.experiment_id,
            "caseId": case_1.id,
        }

        # Reinitializing with experiment entity
        ext1 = ext1.with_initialize_from(experiment)
        modifiers = ext1.to_dict()['modifiers']
        assert len(modifiers) == 2
        assert modifiers['initializeFrom'] == case_1.experiment_id

    def test_experiment_definition_with_cases(self, model, custom_function_no_param):
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
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
