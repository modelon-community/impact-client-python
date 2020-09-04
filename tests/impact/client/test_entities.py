import modelon.impact.client.sal.service
import pytest
import os
import tempfile
import modelon.impact.client.options
from modelon.impact.client import exceptions

from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from modelon.impact.client.entities import (
    Workspace,
    Model,
    ModelExecutable,
    Experiment,
    Case,
)
from modelon.impact.client.operations import (
    ExperimentOperation,
    ModelExecutableOperation,
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
        workspace_ops.import_library(SINGLE_FILE_LIBRARY_PATH)
        import_call = import_lib.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/libraries'
            == import_call.url
        )
        assert 'POST' == import_call.method

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
        t = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        resp = workspace.download({}, t)
        assert resp == t

    def test_clone(self, workspace):
        clone = workspace.clone()
        assert clone == Workspace('MyClonedWorkspace')

    def test_get_model(self, workspace):
        model = workspace.get_model("Modelica.Blocks.PID")
        assert model == Model("Modelica.Blocks.PID", workspace.id)

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
            p1=3.4, p2=False, p3='då', p4='new string'
        )
        assert new.parameter_values == {
            'p1': 3.4,
            'p2': False,
            'p3': 'då',
            'p4': 'new string',
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
        self, custom_function,
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3=4.6)

    def test_custom_function_with_parameters_cannot_set_string_type(
        self, custom_function
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p4=4.6)

    def test_custom_function_with_parameters_cannot_set_enumeration_value(
        self, custom_function,
    ):
        pytest.raises(ValueError, custom_function.with_parameters, p3='not in values')

    def test_options(self, custom_function):
        new = custom_function.options()
        assert new.to_dict() == {
            "compiler": {"c_compiler": "gcc"},
            "runtime": {},
            "simulation": {"ncp": 500},
            "solver": {},
        }
        assert isinstance(new, modelon.impact.client.options.ExecutionOptions)


class TestModel:
    def test_compile(self, model_compiled, options):
        fmu = model_compiled.compile(options)
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_compile_dict_options(self, model_compiled):
        fmu = model_compiled.compile({'c_compiler': 'gcc'})
        assert fmu == ModelExecutableOperation('AwesomeWorkspace', 'test_pid_fmu_id')

    def test_compile_invalid_type_options(self, model_compiled):
        pytest.raises(TypeError, model_compiled.compile, [])


class TestModelExecutable:
    def test_compile_successful(self, fmu):
        assert fmu.id == 'Test'
        assert fmu.is_successful()
        assert fmu.settable_parameters() == ['h0', 'v']
        assert fmu.get_log() == "Successful Log"
        assert fmu.metadata == {
            "steady_state": {
                "residual_variable_count": 1,
                "iteration_variable_count": 2,
            }
        }
        assert fmu.info == {'run_info': {'status': 'successful'}}

    def test_compilation_running(self, fmu_compile_running):
        assert fmu_compile_running.info["run_info"]["status"] == "not_started"
        pytest.raises(
            exceptions.OperationNotCompleteError, fmu_compile_running.log,
        )
        pytest.raises(
            exceptions.OperationNotCompleteError,
            fmu_compile_running.settable_parameters,
        )
        pytest.raises(
            exceptions.OperationNotCompleteError, fmu_compile_running.is_successful,
        )

    def test_compilation_failed(self, fmu_compile_failed):
        assert fmu_compile_failed.info["run_info"]["status"] == "failed"
        assert not fmu_compile_failed.is_successful()
        assert fmu_compile_failed.get_log() == "Failed Log"
        pytest.raises(
            exceptions.OperationFailureError, fmu_compile_failed.settable_parameters,
        )

    def test_compilation_cancelled(self, fmu_compile_cancelled):
        assert fmu_compile_cancelled.info["run_info"]["status"] == "cancelled"
        pytest.raises(
            exceptions.OperationFailureError, fmu_compile_cancelled.is_successful,
        )
        pytest.raises(
            exceptions.OperationFailureError, fmu_compile_cancelled.log,
        )
        pytest.raises(
            exceptions.OperationFailureError, fmu_compile_cancelled.settable_parameters,
        )

    def test_create_experiment_definition(self, fmu, custom_function):
        experiment_definition = fmu.new_experiment_definition(
            custom_function=custom_function,
            options=custom_function.options().with_simulation_options(
                ncp=2000, rtol=0.1
            ),
        )
        config = experiment_definition.to_dict()
        assert config['experiment']['fmu_id'] == fmu.id
        assert config['experiment']['analysis']['simulation_options'] == {
            'ncp': 2000,
            'rtol': 0.1,
        }


class TestExperiment:
    def test_execute_successful(self, experiment):
        assert experiment.id == "Test"
        assert experiment.is_successful()
        assert experiment.info == {
            "run_info": {"status": "done", "failed": 0, "successful": 1, "cancelled": 0}
        }
        assert experiment.variables() == ["inertia.I", "time"]
        assert experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert experiment.case("case_1") == Case("case_1", "Workspace", "Test")
        exp = experiment.trajectories(['inertia.I', 'time'])
        assert exp['case_1']['inertia.I'] == [1, 2, 3, 4]
        assert exp['case_1']['time'] == [5, 2, 9, 4]

    def test_successful_batch_execute(self, batch_experiment):
        assert batch_experiment.is_successful()
        assert batch_experiment.info == {
            "run_info": {"status": "done", "failed": 0, "successful": 2, "cancelled": 0}
        }
        assert batch_experiment.variables() == ["inertia.I", "time"]
        assert batch_experiment.cases() == [
            Case("case_1", "Workspace", "Test"),
            Case("case_2", "Workspace", "Test"),
        ]
        exp = batch_experiment.trajectories(['inertia.I'])
        assert exp['case_1']['inertia.I'] == [1, 2, 3, 4]
        assert exp['case_2']['inertia.I'] == [14, 4, 4, 74]

    def test_running_execution(self, running_experiment):
        assert running_experiment.info["run_info"]["status"] == "not_started"
        pytest.raises(
            exceptions.OperationNotCompleteError, running_experiment.variables,
        )
        pytest.raises(
            exceptions.OperationNotCompleteError,
            running_experiment.trajectories,
            ['inertia.I'],
        )

    def test_failed_execution(self, failed_experiment):
        assert failed_experiment.info["run_info"]["status"] == "done"
        assert failed_experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert failed_experiment.case("case_1") == Case("case_1", "Workspace", "Test")
        assert not failed_experiment.is_successful()
        pytest.raises(
            exceptions.OperationFailureError, failed_experiment.variables,
        )
        pytest.raises(
            exceptions.OperationFailureError,
            failed_experiment.trajectories,
            ['inertia.I'],
        )

    def test_cancelled_execution(self, cancelled_experiment):
        assert cancelled_experiment.info["run_info"]["status"] == "cancelled"
        assert cancelled_experiment.cases() == [Case("case_1", "Workspace", "Test")]
        assert cancelled_experiment.case("case_1") == Case(
            "case_1", "Workspace", "Test"
        )
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.is_successful,
        )
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.variables,
        )
        pytest.raises(
            exceptions.OperationFailureError,
            cancelled_experiment.trajectories,
            ['inertia.I'],
        )

    def test_exp_trajectories_non_list_entry(self, experiment):
        pytest.raises(TypeError, experiment.trajectories, 'hh')

    def test_exp_trajectories_invalid_keys(self, experiment):
        pytest.raises(ValueError, experiment.trajectories, ['s'])


class TestCase:
    def test_case(self, experiment):
        case = experiment.case("case_1")
        assert case.id == "case_1"
        assert case.info["run_info"]["status"] == "successful"
        assert case.get_log() == "Successful Log"
        result, name = case.result()
        assert (result, name) == (b'\x00\x00\x00\x00', 'result.mat')
        assert case.is_successful()
        assert case.trajectories()['inertia.I'] == [1, 2, 3, 4]

    def test_multiple_cases(self, batch_experiment):
        case = batch_experiment.case("case_2")
        assert case.id == "case_2"
        assert case.info["run_info"]["status"] == "successful"
        assert case.get_log() == "Successful Log"
        result, name = case.result()
        assert (result, name) == (b'\x00\x00\x00\x00', 'result.mat')
        assert case.is_successful()
        assert case.trajectories()['inertia.I'] == [14, 4, 4, 74]

    def test_failed_case(self, failed_experiment):
        failed_case = failed_experiment.case("case_2")
        assert failed_case.id == "case_1"
        assert failed_case.info["run_info"]["status"] == "failed"
        assert not failed_case.is_successful()
        pytest.raises(
            exceptions.OperationFailureError, failed_case.result,
        )
        pytest.raises(
            exceptions.OperationFailureError, failed_case.trajectories,
        )

    def test_failed_execution_result(self, failed_experiment):
        pytest.raises(
            exceptions.OperationFailureError, failed_experiment.case("case_2").result,
        )
