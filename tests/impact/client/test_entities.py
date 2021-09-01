import modelon.impact.client.sal.service
import pytest
import os
import tempfile
import unittest.mock as mock
import modelon.impact.client.options
from modelon.impact.client import exceptions

from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from modelon.impact.client.entities import (
    Workspace,
    Model,
    ModelExecutable,
    Experiment,
    Case,
    ExperimentStatus,
    ModelExecutableStatus,
    CaseStatus,
)
from modelon.impact.client.operations import (
    ExperimentOperation,
    ModelExecutableOperation,
    CachedModelExecutableOperation,
)
from tests.impact.client.fixtures import *


class TestWorkspace:
    def test_get_custom_function(self, workspace):
        custom_function = workspace.get_custom_function('dynamic')
        assert 'dynamic' == custom_function.name

    def test_get_custom_functions(self, workspace):
        custom_function_list = [
            custom_function.name for custom_function in workspace.get_custom_functions()
        ]
        assert ['dynamic'] == custom_function_list

    def test_delete(self, workspace_ops, delete_workspace):
        workspace_ops.delete()
        delete_call = delete_workspace.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace' == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_import_library(self, workspace_ops, import_lib):
        workspace_ops.upload_model_library(SINGLE_FILE_LIBRARY_PATH)
        import_call = import_lib.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/libraries'
            == import_call.url
        )
        assert 'POST' == import_call.method

    def test_import_fmu(self, workspace_ops, import_fmu):
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            workspace_ops.upload_fmu("test.fmu", "Workspace")
            mock_file.assert_called_with("test.fmu", "rb")

        import_fmu_call = import_fmu.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/libraries/Workspace/models'
            == import_fmu_call.url
        )
        assert 'POST' == import_fmu_call.method

    def test_lock(self, workspace_ops, lock_workspace):
        workspace_ops.lock()
        lock_call = lock_workspace.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/lock'
            == lock_call.url
        )
        assert 'POST' == lock_call.method

    def test_unlock(self, workspace_ops, unlock_workspace):
        workspace_ops.unlock()
        unlock_call = unlock_workspace.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/lock'
            == unlock_call.url
        )
        assert 'DELETE' == unlock_call.method

    def test_download_workspace(self, workspace):
        t = os.path.join(tempfile.gettempdir(), workspace.id + '.zip')
        resp = workspace.download({}, tempfile.gettempdir())
        assert resp == t

    def test_clone(self, workspace):
        clone = workspace.clone()
        assert clone == Workspace('MyClonedWorkspace')

    def test_get_custom_function_from_clone(self, workspace):
        clone = workspace.clone()
        custom_function = clone.get_custom_function('dynamic')
        assert 'dynamic' == custom_function.name

    def test_get_model(self, workspace):
        model = workspace.get_model("Modelica.Blocks.PID")
        assert model == Model("Modelica.Blocks.PID", workspace.id)

    def test_model_repr(self, workspace):
        model = Model("Modelica.Blocks.PID", workspace.id)
        assert "Class name 'Modelica.Blocks.PID'" == model.__repr__()

    def test_get_fmus(self, workspace):
        fmus = workspace.get_fmus()
        assert fmus == [
            ModelExecutable('AwesomeWorkspace', 'as9f-3df5'),
            ModelExecutable('AwesomeWorkspace', 'as9D-4df5'),
        ]

    def test_get_fmu(self, workspace):
        fmu = workspace.get_fmu('pid_20090615_134')
        assert fmu == ModelExecutable('AwesomeWorkspace', 'pid_20090615_134')

    def test_get_experiment(self, workspace):
        exp = workspace.get_experiment('pid_20090615_134')
        assert exp == Experiment('AwesomeWorkspace', 'pid_20090615_134')

    def test_get_experiments(self, workspace):
        exps = workspace.get_experiments()
        assert exps == [
            Experiment('AwesomeWorkspace', 'as9f-3df5'),
            Experiment('AwesomeWorkspace', 'dd9f-3df5'),
        ]

    def test_create_experiment(self, workspace):
        exp = workspace.create_experiment({})
        assert exp == Experiment('AwesomeWorkspace', 'pid_2009')

    def test_execute_options_dict(self, workspace):
        exp = workspace.execute({})
        assert exp == ExperimentOperation('AwesomeWorkspace', 'pid_2009')


class TestCustomFunction:
    def test_custom_function_with_parameters_ok(self, custom_function):
        new = custom_function.with_parameters(
            p1=3.4, p2=False, p3='då', p4='new string', p5=4
        )
        assert new.parameter_values == {
            'p1': 3.4,
            'p2': False,
            'p3': 'då',
            'p4': 'new string',
            'p5': 4.0,
        }

    def test_custom_function_with_parameters_no_such_parameter(self, custom_function):
        pytest.raises(ValueError, custom_function.with_parameters, does_not_exist=3.4)

    def test_custom_function_with_parameters_cannot_set_number_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p1='not a number')

    def test_custom_function_with_parameters_cannot_set_boolean_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p2='not a boolean')

    def test_custom_function_with_parameters_cannot_set_enumeration_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3=4.6)

    def test_custom_function_with_parameters_cannot_set_string_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p4=4.6)

    def test_custom_function_with_parameters_cannot_set_enumeration_value(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3='not in values')

    def test_compiler_options(self, custom_function):
        new = custom_function.get_compiler_options().with_values(c_compiler='gcc')
        assert dict(new) == {"c_compiler": "gcc"}
        assert isinstance(new, modelon.impact.client.options.ExecutionOptions)

    def test_runtime_options(self, custom_function):
        new = custom_function.get_runtime_options().with_values(cs_solver=0)
        assert dict(new) == {"cs_solver": 0}
        assert isinstance(new, modelon.impact.client.options.ExecutionOptions)

    def test_simulation_options(self, custom_function):
        new = custom_function.get_simulation_options().with_values(ncp=500)
        assert dict(new) == {"ncp": 500}
        assert isinstance(new, modelon.impact.client.options.ExecutionOptions)

    def test_solver_options(self, custom_function):
        new = custom_function.get_solver_options().with_values(atol=1e-7, rtol=1e-9)
        assert dict(new) == {'atol': 1e-7, 'rtol': 1e-9}
        assert isinstance(new, modelon.impact.client.options.ExecutionOptions)


class TestModel:
    def test_find_cached(self, model_cached, compiler_options, runtime_options):
        fmu = model_cached.compile(compiler_options, runtime_options)
        assert fmu == CachedModelExecutableOperation(
            'AwesomeWorkspace', 'test_pid_fmu_id'
        )

    def test_force_compile(self, model_compiled, compiler_options, runtime_options):
        fmu = model_compiled.compile(
            compiler_options, runtime_options, force_compilation=True
        )
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_force_compile_dict_options(self, model_compiled):
        fmu = model_compiled.compile({'c_compiler': 'gcc'}, force_compilation=True)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_compile_invalid_type_options(self, model_compiled):
        pytest.raises(TypeError, model_compiled.compile, [])


class TestModelExecutable:
    def test_compile_successful(self, fmu):
        assert fmu.id == 'Test'
        assert fmu.is_successful()
        assert fmu.get_settable_parameters() == ['h0', 'v']
        assert fmu.get_log() == "Successful Log"
        assert fmu.metadata == {
            "steady_state": {
                "residual_variable_count": 1,
                "iteration_variable_count": 2,
            }
        }
        assert fmu.run_info.status == ModelExecutableStatus.SUCCESSFUL
        assert fmu.run_info.errors == []

    def test_compilation_running(self, fmu_compile_running):
        assert fmu_compile_running.run_info.status == ModelExecutableStatus.NOTSTARTED
        pytest.raises(exceptions.OperationNotCompleteError, fmu_compile_running.get_log)
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_running.get_settable_parameters,
        )
        assert not fmu_compile_running.is_successful()

    def test_compilation_failed(self, fmu_compile_failed):
        assert fmu_compile_failed.run_info.status == ModelExecutableStatus.FAILED
        assert not fmu_compile_failed.is_successful()
        assert fmu_compile_failed.get_log() == "Failed Log"
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_failed.get_settable_parameters,
        )

    def test_compilation_cancelled(self, fmu_compile_cancelled):
        assert fmu_compile_cancelled.run_info.status == ModelExecutableStatus.CANCELLED
        assert not fmu_compile_cancelled.is_successful()
        pytest.raises(exceptions.OperationFailureError, fmu_compile_cancelled.get_log)
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_cancelled.get_settable_parameters,
        )

    def test_create_experiment_definition(self, fmu, custom_function):
        experiment_definition = fmu.new_experiment_definition(
            custom_function=custom_function,
            simulation_options=custom_function.get_simulation_options().with_values(
                ncp=2000, rtol=0.1
            ),
        )
        config = experiment_definition.to_dict()
        assert config['experiment']['base']['model']['fmu']['id'] == fmu.id
        assert config['experiment']['base']['analysis']['simulationOptions'] == {
            'ncp': 2000,
            'rtol': 0.1,
        }

    def test_download_fmu(self, fmu):
        t = os.path.join(tempfile.gettempdir(), fmu.id + '.fmu')
        resp = fmu.download(tempfile.gettempdir())
        assert resp == t

    def test_download_fmu_no_path(self, fmu):
        t = os.path.join(tempfile.gettempdir(), 'impact-downloads', fmu.id + '.fmu')
        resp = fmu.download()
        assert resp == t

    def test_can_be_put_uniquely_in_set(self, fmu):
        fmu_set = set([fmu, fmu])
        assert len(fmu_set) == 1


class TestExperiment:
    def test_execute(self, experiment):
        exp = experiment.experiment.execute()
        assert exp == ExperimentOperation('AwesomeWorkspace', 'pid_2009')

    def test_execute_with_case_filter(self, batch_experiment_with_case_filter):
        experiment = batch_experiment_with_case_filter.experiment
        exp_sal = batch_experiment_with_case_filter.exp_service
        case_generated = experiment.execute(with_cases=[]).wait()
        exp_sal.experiment_execute.assert_has_calls(
            [mock.call('Workspace', 'Test', [])]
        )
        case_to_execute = case_generated.get_cases()[2]
        result = experiment.execute(with_cases=[case_to_execute]).wait()
        exp_sal.experiment_execute.assert_has_calls(
            [mock.call('Workspace', 'Test', ["case_3"])]
        )
        assert result == Experiment('AwesomeWorkspace', 'pid_2009')
        assert result.run_info.successful == 1
        assert result.run_info.not_started == 3
        assert experiment.get_case('case_3').is_successful()

    def test_execute_successful(self, experiment):
        experiment = experiment.experiment
        assert experiment.id == "Test"
        assert experiment.is_successful()
        assert experiment.run_info.status == ExperimentStatus.DONE
        assert experiment.run_info.errors == []
        assert experiment.run_info.failed == 0
        assert experiment.run_info.successful == 1
        assert experiment.run_info.cancelled == 0
        assert experiment.run_info.not_started == 0
        assert experiment.get_variables() == ["inertia.I", "time"]
        assert experiment.get_cases() == [Case("case_1", "Workspace", "Test")]
        assert experiment.get_case("case_1") == Case("case_1", "Workspace", "Test")
        exp = experiment.get_trajectories(['inertia.I', 'time'])
        assert exp['case_1']['inertia.I'] == [1, 2, 3, 4]
        assert exp['case_1']['time'] == [5, 2, 9, 4]

    def test_successful_batch_execute(self, batch_experiment):
        assert batch_experiment.is_successful()
        assert batch_experiment.run_info.status == ExperimentStatus.DONE
        assert batch_experiment.run_info.failed == 0
        assert batch_experiment.run_info.successful == 2
        assert batch_experiment.run_info.cancelled == 0
        assert batch_experiment.run_info.not_started == 0
        assert batch_experiment.get_variables() == ["inertia.I", "time"]
        assert batch_experiment.get_cases() == [
            Case("case_1", "Workspace", "Test"),
            Case("case_2", "Workspace", "Test"),
        ]
        exp = batch_experiment.get_trajectories(['inertia.I'])
        assert exp['case_1']['inertia.I'] == [1, 2, 3, 4]
        assert exp['case_2']['inertia.I'] == [14, 4, 4, 74]

    def test_some_successful_batch_execute(self, batch_experiment_some_successful):
        assert not batch_experiment_some_successful.is_successful()
        assert batch_experiment_some_successful.run_info.status == ExperimentStatus.DONE
        assert batch_experiment_some_successful.run_info.failed == 1
        assert batch_experiment_some_successful.run_info.successful == 2
        assert batch_experiment_some_successful.run_info.cancelled == 0
        assert batch_experiment_some_successful.run_info.not_started == 1
        assert batch_experiment_some_successful.get_cases() == [
            Case("case_1", "Workspace", "Test"),
            Case("case_2", "Workspace", "Test"),
            Case("case_3", "Workspace", "Test"),
            Case("case_4", "Workspace", "Test"),
        ]

    def test_running_execution(self, running_experiment):
        assert running_experiment.run_info.status == ExperimentStatus.NOTSTARTED
        assert not running_experiment.is_successful()
        pytest.raises(
            exceptions.OperationNotCompleteError, running_experiment.get_variables
        )
        pytest.raises(
            exceptions.OperationNotCompleteError,
            running_experiment.get_trajectories,
            ['inertia.I'],
        )

    def test_failed_execution(self, failed_experiment):
        assert failed_experiment.run_info.status == ExperimentStatus.FAILED
        assert not failed_experiment.is_successful()
        assert failed_experiment.run_info.errors == [
            'out of licenses',
            'too large experiment',
        ]

    def test_execution_with_failed_cases(self, experiment_with_failed_case):
        assert experiment_with_failed_case.run_info.status == ExperimentStatus.DONE
        assert experiment_with_failed_case.get_cases() == [
            Case("case_1", "Workspace", "Test")
        ]
        assert experiment_with_failed_case.get_case("case_1") == Case(
            "case_1", "Workspace", "Test"
        )
        assert not experiment_with_failed_case.is_successful()
        assert experiment_with_failed_case.get_trajectories(['inertia.I']) == {
            'case_1': {'inertia.I': [1, 2, 3, 4]}
        }

    def test_cancelled_execution(self, cancelled_experiment):
        assert cancelled_experiment.run_info.status == ExperimentStatus.CANCELLED
        assert cancelled_experiment.get_cases() == [Case("case_1", "Workspace", "Test")]
        assert cancelled_experiment.get_case("case_1") == Case(
            "case_1", "Workspace", "Test"
        )
        assert not cancelled_experiment.is_successful()
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.get_variables
        )
        pytest.raises(
            exceptions.OperationFailureError,
            cancelled_experiment.get_trajectories,
            ['inertia.I'],
        )

    def test_exp_trajectories_non_list_entry(self, experiment):
        pytest.raises(TypeError, experiment.experiment.get_trajectories, 'hh')

    def test_exp_trajectories_invalid_keys(self, experiment):
        pytest.raises(ValueError, experiment.experiment.get_trajectories, ['s'])


class TestCase:
    def test_case(self, experiment):
        case = experiment.experiment.get_case("case_1")
        assert case.id == "case_1"
        assert case.run_info.status == CaseStatus.SUCCESSFUL
        assert case.get_log() == "Successful Log"
        result, name = case.get_result()
        assert (result, name) == (b'\x00\x00\x00\x00', 'result.mat')
        artifact, name = case.get_artifact('ABCD')
        assert (artifact, name) == (b'\x00\x00\x00\x00', 'result.mat')
        assert case.is_successful()
        assert case.get_trajectories()['inertia.I'] == [1, 2, 3, 4]
        fmu = case.get_fmu()
        assert fmu.id == "modelica_fluid_examples_heatingsystem_20210130_114628_bbd91f1"

    def test_multiple_cases(self, batch_experiment):
        case = batch_experiment.get_case("case_2")
        assert case.id == "case_2"
        assert case.run_info.status == CaseStatus.SUCCESSFUL
        assert case.get_log() == "Successful Log"
        result, name = case.get_result()
        assert (result, name) == (b'\x00\x00\x00\x00', 'result.mat')
        artifact, name = case.get_artifact('ABCD')
        assert (artifact, name) == (b'\x00\x00\x00\x00', 'result.mat')
        assert case.is_successful()
        assert case.get_trajectories()['inertia.I'] == [14, 4, 4, 74]

    def test_failed_case(self, experiment_with_failed_case):
        failed_case = experiment_with_failed_case.get_case("case_2")
        assert failed_case.id == "case_1"
        assert failed_case.run_info.status == CaseStatus.FAILED
        assert not failed_case.is_successful()
        pytest.raises(exceptions.OperationFailureError, failed_case.get_result)
        assert failed_case.get_trajectories()["inertia.I"] == [1, 2, 3, 4]

    def test_failed_execution_result(self, experiment_with_failed_case):
        pytest.raises(
            exceptions.OperationFailureError,
            experiment_with_failed_case.get_case("case_2").get_result,
        )

    def test_case_update(self, experiment, batch_experiment):
        exp = experiment.experiment
        exp_sal = experiment.exp_service

        case = exp.get_case("case_1")
        case.input.parametrization = {'PI.k': 120}
        case.input.analysis.simulation_options = {'ncp': 600}
        case.input.analysis.solver_options = {'atol': 1e-8}
        case.input.analysis.simulation_log_level = "DEBUG"
        case.input.analysis.parameters = {"start_time": 1, "final_time": 2e5}
        case_2 = batch_experiment.get_case('case_2')
        case.initialize_from_case = case_2
        case.update()
        exp_sal.case_put.assert_has_calls(
            [
                mock.call(
                    'Workspace',
                    'Test',
                    'case_1',
                    {
                        'id': 'case_1',
                        'run_info': {'status': 'successful'},
                        'input': {
                            'fmu_id': 'modelica_fluid_examples_heatingsystem_20210130_114628_bbd91f1',
                            'analysis': {
                                'analysis_function': 'dynamic',
                                'parameters': {'start_time': 1, 'final_time': 200000.0},
                                'simulation_options': {'ncp': 600},
                                'solver_options': {'atol': 1e-08},
                                'simulation_log_level': 'DEBUG',
                            },
                            'parametrization': {'PI.k': 120},
                            'structural_parametrization': {},
                            'fmu_base_parametrization': {},
                            'initialize_from_case': {
                                'experimentId': 'Test',
                                'caseId': 'case_2',
                            },
                        },
                    },
                )
            ]
        )
        result = case.execute().wait()
        assert result == Case('case_1', 'AwesomeWorkspace', 'pid_2009')

    def test_set_case_label(self, experiment):
        exp = experiment.experiment
        exp_sal = experiment.exp_service
        exp.set_label('Label')
        exp_sal.experiment_set_label.assert_has_calls(
            [mock.call('Workspace', 'Test', 'Label')]
        )

    def test_case_input(self, experiment):
        exp = experiment.experiment

        case = exp.get_case("case_1")
        case.input.analysis.parameters = {"start_time": 0, "final_time": 90}
        case.input.analysis.simulation_options = {'ncp': 600}
        case.input.analysis.solver_options = {'atol': 1e-8}
        case.input.analysis.simulation_log_level = "DEBUG"
        case.input.parametrization = {'PI.k': 120}

        assert case.input.analysis.parameters == {"start_time": 0, "final_time": 90}
        assert case.input.analysis.simulation_options == {'ncp': 600}
        assert case.input.analysis.solver_options == {'atol': 1e-8}
        assert case.input.analysis.simulation_log_level == "DEBUG"
        assert case.input.parametrization == {'PI.k': 120}
