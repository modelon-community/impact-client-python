import copy
from unittest import mock

import pytest

from modelon.impact.client import (
    Beta,
    Choices,
    Enumeration,
    LatinHypercube,
    Normal,
    Range,
    SimpleExperimentExtension,
    SimpleFMUExperimentDefinition,
    SimpleModelicaExperimentDefinition,
    Sobol,
    Uniform,
    exceptions,
)
from modelon.impact.client.entities.result import Result
from modelon.impact.client.experiment_definition.modifiers import DataType
from tests.impact.client.helpers import (
    IDs,
    create_case_entity,
    create_external_result_entity,
)

_EXPECTED_FMU_EXP = {
    "experiment": {
        "version": 3,
        "base": {
            "model": {"fmu": {"id": IDs.FMU_ID_PRIMARY}},
            "modifiers": {
                "variables": [
                    {
                        "kind": "range",
                        "name": "h0",
                        "start": 0.1,
                        "end": 0.5,
                        "steps": 3,
                    }
                ],
                "initializeFrom": IDs.EXPERIMENT_ID_PRIMARY,
            },
            "analysis": {
                "type": "dynamic",
                "parameters": [],
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
        "version": 3,
        "base": {
            "model": {
                "modelica": {
                    "className": IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
                    "compilerOptions": {"c_compiler": "gcc"},
                    "runtimeOptions": {},
                    "compilerLogLevel": "warning",
                    "fmiTarget": "me",
                    "fmiVersion": "2.0",
                    "platform": "auto",
                }
            },
            "modifiers": {
                "variables": [
                    {
                        "kind": "range",
                        "name": "h0",
                        "start": 0.1,
                        "end": 0.5,
                        "steps": 3,
                    },
                ],
                "initializeFrom": IDs.EXPERIMENT_ID_PRIMARY,
            },
            "analysis": {
                "type": "dynamic",
                "parameters": [],
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
            "parameters": [{"name": "stop_time", "value": 5}],
            "simulationOptions": {"ncp": 2000, "rtol": 0.0001},
            "solverOptions": {"a": 1},
            "simulationLogLevel": "Warning",
        },
        "modifiers": {
            "initializeFrom": IDs.EXPERIMENT_ID_PRIMARY,
            "variables": [
                {"kind": "value", "name": "PI.k", "value": 10, "dataType": "INTEGER"},
                {"kind": "value", "name": "P", "value": 5, "dataType": "INTEGER"},
                {"kind": "value", "name": "d", "value": 15, "dataType": "INTEGER"},
            ],
        },
        "caseData": [{"label": "Cruise condition"}],
    }


def get_base_ext(custom_function_no_param):
    return SimpleExperimentExtension(
        {"stop_time": 5},
        {"a": 1},
        custom_function_no_param.get_simulation_options().with_values(
            ncp=2000, rtol=0.0001
        ),
        simulation_log_level="Warning",
    )


def get_expected_with_ext_first(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["extensions"] = [
        {
            "modifiers": {
                "variables": [
                    {"kind": "value", "name": "t", "value": 2, "dataType": "INTEGER"}
                ]
            }
        },
        {
            "modifiers": {
                "variables": [
                    {"kind": "value", "name": "p", "value": 3, "dataType": "INTEGER"}
                ]
            }
        },
    ]
    return expected


def get_expected_with_cases_first(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["extensions"] = [
        {
            "modifiers": {
                "variables": [
                    {"kind": "value", "name": "p", "value": 3, "dataType": "INTEGER"}
                ]
            }
        },
        {
            "modifiers": {
                "variables": [
                    {"kind": "value", "name": "t", "value": 2, "dataType": "INTEGER"}
                ]
            }
        },
    ]
    return expected


def get_expected_with_sobol_expansion(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["base"]["modifiers"] = {
        "variables": [{"kind": "uniform", "name": "h0", "start": 0.1, "end": 0.5}]
    }
    expected["experiment"]["base"]["expansion"] = {
        "algorithm": "SOBOL",
        "parameters": {"samples": 5},
    }
    return expected


def get_expected_with_lhs_expansion(experiment_body):
    expected = copy.deepcopy(experiment_body)
    expected["experiment"]["base"]["modifiers"] = {
        "variables": [
            {
                "kind": "normal",
                "name": "h0",
                "mean": 0.1,
                "variable": 0.5,
                "start": None,
                "end": None,
            }
        ]
    }
    expected["experiment"]["base"]["expansion"] = {
        "algorithm": "LATINHYPERCUBE",
        "parameters": {"samples": 5, "seed": 1},
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
                "version": 3,
                "base": {
                    "model": {"fmu": {"id": IDs.FMU_ID_PRIMARY}},
                    "modifiers": {"variables": []},
                    "analysis": {
                        "type": "dynamic",
                        "parameters": [],
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{"p": 3}])
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .with_initialize_from(experiment)
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_initialize_from(experiment)
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_cases([{"p": 3}])
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_initialize_from(experiment)
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_with_options(self, fmu, custom_function_no_param):
        sim_opts = custom_function_no_param.get_simulation_options().with_values(
            ncp=2000, rtol=0.0001
        )
        definition = SimpleFMUExperimentDefinition(
            fmu,
            custom_function=custom_function_no_param,
            simulation_options=sim_opts,
            solver_options={"a": 1},
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
        ).with_modifiers({"h0": Range(0.1, 0.5, 3)}, v=Choices(0.1, 0.5, 3))
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == [
            {"kind": "range", "name": "h0", "start": 0.1, "end": 0.5, "steps": 3},
            {
                "kind": "choices",
                "name": "v",
                "values": [0.1, 0.5, 3],
                "dataType": "REAL",
            },
        ]

    def test_experiment_definition_with_choices_1_input_modifier(
        self, fmu, custom_function_no_param
    ):
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
        ).with_modifiers(v=Choices(0.1))
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == [
            {"dataType": "REAL", "kind": "choices", "name": "v", "values": [0.1]}
        ]

    def test_experiment_definition_with_fmu_modifiers(
        self, fmu_with_modifiers, custom_function_no_param
    ):
        definition = SimpleFMUExperimentDefinition(
            fmu_with_modifiers, custom_function=custom_function_no_param
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == [
            {"kind": "value", "name": "PI.K", "value": 20, "dataType": "INTEGER"}
        ]

    def test_experiment_definition_with_extensions(self, fmu, custom_function_no_param):
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = SimpleExperimentExtension({"final_time": 10}).with_modifiers(p=3)
        definition = SimpleFMUExperimentDefinition(
            fmu, custom_function=custom_function_no_param
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {
                "modifiers": {
                    "variables": [
                        {
                            "kind": "value",
                            "name": "p",
                            "value": 2,
                            "dataType": "INTEGER",
                        }
                    ]
                }
            },
            {
                "modifiers": {
                    "variables": [
                        {
                            "kind": "value",
                            "name": "p",
                            "value": 3,
                            "dataType": "INTEGER",
                        }
                    ]
                },
                "analysis": {"parameters": [{"name": "final_time", "value": 10}]},
            },
        ]

    def test_experiment_definition_with_cases(self, fmu, custom_function_no_param):
        definition = SimpleFMUExperimentDefinition(
            fmu,
            custom_function=custom_function_no_param,
        ).with_cases([{"p": 2}, {"p": 3}])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {
                "modifiers": {
                    "variables": [
                        {
                            "kind": "value",
                            "name": "p",
                            "value": 2,
                            "dataType": "INTEGER",
                        }
                    ]
                }
            },
            {
                "modifiers": {
                    "variables": [
                        {
                            "kind": "value",
                            "name": "p",
                            "value": 3,
                            "dataType": "INTEGER",
                        }
                    ]
                }
            },
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
            {"stop_time": 5},
            {"a": 1},
            custom_function_no_param.get_simulation_options().with_values(
                ncp=2000, rtol=0.0001
            ),
        )
        config = ext.to_dict()
        assert config == {
            "analysis": {
                "parameters": [{"name": "stop_time", "value": 5}],
                "simulationOptions": {"ncp": 2000, "rtol": 0.0001},
                "solverOptions": {"a": 1},
            },
        }

    def test_experiment_extension_with_modifiers(self):
        ext = SimpleExperimentExtension().with_modifiers({"PI.k": 10}, P=5, d=15)
        config = ext.to_dict()
        assert config == {
            "modifiers": {
                "variables": [
                    {
                        "kind": "value",
                        "name": "PI.k",
                        "value": 10,
                        "dataType": "INTEGER",
                    },
                    {"kind": "value", "name": "P", "value": 5, "dataType": "INTEGER"},
                    {"kind": "value", "name": "d", "value": 15, "dataType": "INTEGER"},
                ]
            }
        }

    def test_experiment_extension_with_case_label(self):
        ext = SimpleExperimentExtension().with_case_label("Cruise condition")
        config = ext.to_dict()
        assert config == {"caseData": [{"label": "Cruise condition"}]}

    def test_experiment_extension_order_1(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_modifiers({"PI.k": 10}, P=5, d=15)
            .with_initialize_from(experiment)
            .with_case_label("Cruise condition")
            .to_dict()
        )
        assert ext == expected_output

    def test_experiment_extension_order_2(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_initialize_from(experiment)
            .with_modifiers({"PI.k": 10}, P=5, d=15)
            .with_case_label("Cruise condition")
            .to_dict()
        )
        assert ext == expected_output

    def test_experiment_extension_order_3(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_initialize_from(experiment)
            .with_case_label("Cruise condition")
            .with_modifiers({"PI.k": 10}, P=5, d=15)
            .to_dict()
        )
        assert ext == expected_output

    def test_experiment_extension_order_4(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_case_label("Cruise condition")
            .with_initialize_from(experiment)
            .with_modifiers({"PI.k": 10}, P=5, d=15)
        ).to_dict()
        assert ext == expected_output

    def test_experiment_extension_order_5(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_case_label("Cruise condition")
            .with_modifiers({"PI.k": 10}, P=5, d=15)
            .with_initialize_from(experiment)
        ).to_dict()
        assert ext == expected_output

    def test_experiment_extension_order_6(self, custom_function_no_param, experiment):
        expected_output = get_experiment_extension_with_case_label_init_modifier()
        experiment = experiment.entity
        base_ext = get_base_ext(custom_function_no_param)
        ext = (
            base_ext.with_modifiers({"PI.k": 10}, P=5, d=15)
            .with_initialize_from(experiment)
            .with_case_label("Cruise condition")
        ).to_dict()
        assert ext == expected_output

    def test_experiment_extension_with_range_modifier(self):
        ext = SimpleExperimentExtension()
        pytest.raises(ValueError, ext.with_modifiers, {"h0": Range(0.1, 0.5, 3)})

    def test_experiment_extension_with_choices_modifier(self):
        ext = SimpleExperimentExtension()
        pytest.raises(ValueError, ext.with_modifiers, {"h0": Choices(0.1, 0.5, 3)})

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
                "version": 3,
                "base": {
                    "model": {
                        "modelica": {
                            "className": IDs.LOCAL_PROJECT_MODELICA_CLASS_PATH,
                            "compilerOptions": {"c_compiler": "gcc"},
                            "runtimeOptions": {},
                            "compilerLogLevel": "warning",
                            "fmiTarget": "me",
                            "fmiVersion": "2.0",
                            "platform": "auto",
                        }
                    },
                    "modifiers": {"variables": []},
                    "analysis": {
                        "type": "dynamic",
                        "parameters": [],
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
            .with_modifiers({"h0": Uniform(0.1, 0.5)})
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
            .with_modifiers({"h0": Normal(0.1, 0.5)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_extensions([ext])
            .with_cases([{"p": 3}])
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .with_initialize_from(experiment)
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_initialize_from(experiment)
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_cases([{"p": 3}])
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_initialize_from(experiment)
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_cases([{"p": 3}])
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
            .with_cases([{"p": 3}])
            .with_initialize_from(experiment)
            .with_extensions([ext])
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
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
            .with_modifiers({"h0": Range(0.1, 0.5, 3)})
            .with_initialize_from(experiment)
            .with_cases([{"p": 3}])
            .with_extensions([ext])
            .to_dict()
        )
        assert exp_def == expected

    def test_experiment_definition_with_options(self, model, custom_function_no_param):
        compiler_opts = custom_function_no_param.get_compiler_options().with_values(
            a=2, b=1
        )
        sim_opts = custom_function_no_param.get_simulation_options().with_values(
            ncp=2000, rtol=0.0001
        )
        definition = SimpleModelicaExperimentDefinition(
            model.entity,
            custom_function=custom_function_no_param,
            compiler_options=compiler_opts,
            runtime_options={"d": 1},
            simulation_options=sim_opts,
            solver_options={"a": 1},
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["model"]["modelica"]["compilerOptions"] == {
            "a": 2,
            "b": 1,
            "c_compiler": "gcc",
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
        ).with_modifiers({"h0": Range(0.1, 0.5, 3), "v": Choices(0.1, 0.5, 3)})
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == [
            {"kind": "range", "name": "h0", "start": 0.1, "end": 0.5, "steps": 3},
            {
                "kind": "choices",
                "name": "v",
                "values": [0.1, 0.5, 3],
                "dataType": "REAL",
            },
        ]

    def test_given_str_and_bool_when_choices_then_type_error(self):
        with pytest.raises(ValueError):
            Choices("test", True)

    def test_given_int_and_real_when_choices_then_type_real(self):
        assert Choices(1, 2.3).data_type == DataType.REAL

    def test_given_real_and_int_when_choices_then_type_real(self):
        assert Choices(2.3, 1).data_type == DataType.REAL

    def test_given_real_int_and_bool_when_choices_then_type_error(self):
        with pytest.raises(ValueError):
            Choices(2.3, 1, False)

    def test_given_int_and_real_data_type_set_to_real_when_choices_then_type_real(
        self,
    ):
        assert Choices(2.3, 1, data_type=DataType.REAL).data_type == DataType.REAL

    def test_given_int_and_real_data_type_set_to_integer_when_choices_then_type_error(
        self,
    ):
        with pytest.raises(ValueError):
            assert Choices(1, 2.3, data_type=DataType.INTEGER)

    def test_experiment_definition_with_distribution_modifier(
        self, model, custom_function_no_param
    ):
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_modifiers(
            {"h0": Uniform(0.1, 0.5), "v": Beta(0.1, 0.5), "t": Normal(0.1, 0.5, -5)}
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == [
            {"kind": "uniform", "name": "h0", "start": 0.1, "end": 0.5},
            {"kind": "beta", "name": "v", "alpha": 0.1, "beta": 0.5},
            {
                "kind": "normal",
                "name": "t",
                "mean": 0.1,
                "variable": 0.5,
                "start": -5,
                "end": None,
            },
        ]

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
                "test.mat", IDs.WORKSPACE_ID_PRIMARY
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
        case_1 = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
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
            "Case_2", IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY
        )
        definition = definition.with_initialize_from(case_to_init)
        modifiers = definition.to_dict()["experiment"]["base"]["modifiers"]
        assert len(modifiers) == 2
        assert modifiers["initializeFromCase"] == {
            "experimentId": case_to_init.experiment_id,
            "caseId": case_to_init.id,
        }

        # Reinitializing with external result entity
        result_to_init = create_external_result_entity("result_id")
        definition = definition.with_initialize_from(result_to_init)
        modifiers = definition.to_dict()["experiment"]["base"]["modifiers"]
        assert len(modifiers) == 2
        assert modifiers["initializeFromExternalResult"] == result_to_init.id

    def test_experiment_definition_with_extensions(
        self, model, custom_function_no_param
    ):
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = SimpleExperimentExtension({"final_time": 10}).with_modifiers(p=3)
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {
                "modifiers": {
                    "variables": [
                        {
                            "dataType": "INTEGER",
                            "kind": "value",
                            "value": 2,
                            "name": "p",
                        }
                    ]
                }
            },
            {
                "modifiers": {
                    "variables": [
                        {
                            "dataType": "INTEGER",
                            "kind": "value",
                            "value": 3,
                            "name": "p",
                        }
                    ]
                },
                "analysis": {"parameters": [{"name": "final_time", "value": 10}]},
            },
        ]

    def test_model_experiment_definition_with_many_modifiers(
        self, model, custom_function_no_param
    ):
        definition = (
            SimpleModelicaExperimentDefinition(
                model.entity, custom_function=custom_function_no_param
            )
            .with_modifiers({"p1": 1})
            .with_modifiers({"p2": 2})
        )
        modifiers_dict = definition.to_dict()["experiment"]["base"]["modifiers"]
        assert modifiers_dict["variables"] == [
            {"kind": "value", "name": "p1", "value": 1, "dataType": "INTEGER"},
            {"kind": "value", "name": "p2", "value": 2, "dataType": "INTEGER"},
        ]

    def test_fmu_experiment_definition_with_many_modifiers(
        self, fmu, custom_function_no_param
    ):
        definition = (
            SimpleFMUExperimentDefinition(fmu, custom_function=custom_function_no_param)
            .with_modifiers({"p1": 1})
            .with_modifiers({"p2": 2})
        )
        modifiers_dict = definition.to_dict()["experiment"]["base"]["modifiers"]
        assert modifiers_dict["variables"] == [
            {
                "dataType": "INTEGER",
                "kind": "value",
                "value": 1,
                "name": "p1",
            },
            {
                "dataType": "INTEGER",
                "kind": "value",
                "value": 2,
                "name": "p2",
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
        ext2 = SimpleExperimentExtension({"final_time": 10}).with_modifiers(p=3)
        ext2 = ext2.with_initialize_from(experiment)
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {
                "modifiers": {
                    "variables": [
                        {
                            "dataType": "INTEGER",
                            "kind": "value",
                            "value": 2,
                            "name": "p",
                        }
                    ]
                }
            },
            {
                "modifiers": {
                    "initializeFrom": experiment.id,
                    "variables": [
                        {
                            "dataType": "INTEGER",
                            "kind": "value",
                            "value": 3,
                            "name": "p",
                        }
                    ],
                },
                "analysis": {"parameters": [{"name": "final_time", "value": 10}]},
            },
        ]

    def test_experiment_definition_with_extensions_initialize_from_case(
        self, model, custom_function_no_param, experiment
    ):
        case_1 = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
        ext1 = SimpleExperimentExtension().with_modifiers(p=2)
        ext2 = (
            SimpleExperimentExtension({"final_time": 10})
            .with_modifiers(p=3)
            .with_initialize_from(case_1)
        )
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_extensions([ext1, ext2])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {
                "modifiers": {
                    "variables": [
                        {
                            "kind": "value",
                            "name": "p",
                            "value": 2,
                            "dataType": "INTEGER",
                        }
                    ]
                }
            },
            {
                "modifiers": {
                    "initializeFromCase": {
                        "experimentId": case_1.experiment_id,
                        "caseId": case_1.id,
                    },
                    "variables": [
                        {
                            "kind": "value",
                            "name": "p",
                            "value": 3,
                            "dataType": "INTEGER",
                        }
                    ],
                },
                "analysis": {"parameters": [{"name": "final_time", "value": 10}]},
            },
        ]

    def test_experiment_definition_with_extensions_initialize_from_multiple_entities(
        self, model, custom_function_no_param, experiment
    ):
        experiment = experiment.entity
        case_1 = experiment.get_case(IDs.CASE_ID_PRIMARY)
        ext1 = SimpleExperimentExtension({"final_time": 10}).with_modifiers(p=3)
        ext1 = ext1.with_initialize_from(case_1)
        modifiers = ext1.to_dict()["modifiers"]
        assert len(modifiers) == 2
        assert modifiers["initializeFromCase"] == {
            "experimentId": case_1.experiment_id,
            "caseId": case_1.id,
        }

        # Reinitializing with experiment entity
        ext1 = ext1.with_initialize_from(experiment)
        modifiers = ext1.to_dict()["modifiers"]
        assert len(modifiers) == 2
        assert modifiers["initializeFrom"] == case_1.experiment_id

    def test_experiment_definition_with_cases(self, model, custom_function_no_param):
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_cases([{"p": 2}, {"p": 3}])
        config = definition.to_dict()
        assert config["experiment"]["extensions"] == [
            {
                "modifiers": {
                    "variables": [
                        {
                            "dataType": "INTEGER",
                            "kind": "value",
                            "value": 2,
                            "name": "p",
                        }
                    ]
                }
            },
            {
                "modifiers": {
                    "variables": [
                        {
                            "dataType": "INTEGER",
                            "kind": "value",
                            "value": 3,
                            "name": "p",
                        }
                    ]
                }
            },
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

    def test_experiment_definition_with_enum_modifier(
        self, model, custom_function_no_param
    ):
        definition = SimpleModelicaExperimentDefinition(
            model.entity, custom_function=custom_function_no_param
        ).with_modifiers(
            {"e": Enumeration("dataTypes.Enumeration.alt1"), "i": Choices(1, 2, 3)}
        )
        config = definition.to_dict()
        assert config["experiment"]["base"]["modifiers"]["variables"] == [
            {
                "kind": "value",
                "name": "e",
                "value": "dataTypes.Enumeration.alt1",
                "dataType": "ENUMERATION",
            },
            {
                "kind": "choices",
                "name": "i",
                "values": [1, 2, 3],
                "dataType": "INTEGER",
            },
        ]
