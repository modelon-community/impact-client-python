import modelon.impact.client.sal.service
import pytest
import os
import tempfile
import unittest.mock as mock
import modelon.impact.client.options
from modelon.impact.client import exceptions

from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from modelon.impact.client.entities import (
    ExperimentStatus,
    ModelExecutableStatus,
    CaseStatus,
)
from tests.impact.client.utils import (
    get_case_entity,
    get_experiment_entity,
    get_external_result_entity,
    get_model_entity,
    get_model_exe_entity,
    get_workspace_entity,
)
from tests.impact.client.helpers import (
    create_case_entity,
    create_experiment_entity,
    create_external_result_entity,
    create_model_entity,
    create_model_exe_entity,
    create_workspace_entity,
)
from modelon.impact.client.operations import (
    ExperimentOperation,
    ModelExecutableOperation,
    CachedModelExecutableOperation,
)
from tests.impact.client.fixtures import *


class TestWorkspace:
    def test_get_custom_function(self, workspace):
        custom_function = workspace.entity.get_custom_function('dynamic')
        assert 'dynamic' == custom_function.name

    def test_get_custom_functions(self, workspace):
        custom_function_list = [
            custom_function.name
            for custom_function in workspace.entity.get_custom_functions()
        ]
        assert ['dynamic'] == custom_function_list

    def test_delete(self):
        workspace_sal = mock.MagicMock()
        workspace = create_workspace_entity("toDeleteWorkspace", workspace_sal)
        workspace.delete()
        workspace_sal.workspace_delete.assert_called_with("toDeleteWorkspace")

    def test_import_library(self):
        workspace_sal = mock.MagicMock()
        workspace = create_workspace_entity("importLibraryWorkspace", workspace_sal,)

        workspace.upload_model_library(SINGLE_FILE_LIBRARY_PATH)
        workspace_sal.library_import.assert_called_with(
            "importLibraryWorkspace", SINGLE_FILE_LIBRARY_PATH
        )

    def test_import_fmu(self):
        workspace_sal = mock.MagicMock()
        workspace = create_workspace_entity("importFMUWorkspace", workspace_sal)
        workspace.upload_fmu("test.fmu", "Workspace")
        workspace_sal.fmu_import.assert_called_with(
            "importFMUWorkspace",
            "test.fmu",
            "Workspace",
            None,
            False,
            None,
            None,
            None,
            step_size=0.0,
        )

    def test_upload_result(self, workspace_sal_upload_base):
        workspace_service = workspace_sal_upload_base
        workspace = create_workspace_entity('uploadResultWorksapce', workspace_service,)
        upload_op = workspace.upload_result("test.mat", "Workspace")
        workspace_service.result_upload.assert_called_with(
            'uploadResultWorksapce', 'test.mat', description=None, label='Workspace'
        )
        assert upload_op.id == "2f036b9fab6f45c788cc466da327cc78workspace"

    def test_download_workspace(self, workspace):
        t = os.path.join(tempfile.gettempdir(), workspace.entity.id + '.zip')
        resp = workspace.entity.download({}, tempfile.gettempdir())
        assert resp == t

    def test_clone(self, workspace):
        clone = workspace.entity.clone()
        assert clone == create_workspace_entity('MyClonedWorkspace')

    def test_get_custom_function_from_clone(self, workspace):
        clone = workspace.entity.clone()
        custom_function = clone.get_custom_function('dynamic')
        assert 'dynamic' == custom_function.name

    def test_get_model(self, workspace):
        model = workspace.entity.get_model("Modelica.Blocks.PID")
        assert model == create_model_entity("Modelica.Blocks.PID", workspace.entity.id)

    def test_model_repr(self, workspace):
        model = create_model_entity("Modelica.Blocks.PID", workspace.entity.id)
        assert "Class name 'Modelica.Blocks.PID'" == model.__repr__()

    def test_get_fmus(self, workspace):
        fmus = workspace.entity.get_fmus()
        assert fmus == [
            create_model_exe_entity('AwesomeWorkspace', 'as9f-3df5'),
            create_model_exe_entity('AwesomeWorkspace', 'as9D-4df5'),
        ]

    def test_get_fmu(self, workspace):
        fmu = workspace.entity.get_fmu('pid_20090615_134')
        assert fmu == create_model_exe_entity('AwesomeWorkspace', 'pid_20090615_134')

    def test_get_experiment(self, workspace):
        exp = workspace.entity.get_experiment('pid_20090615_134')
        assert exp == create_experiment_entity('AwesomeWorkspace', 'pid_20090615_134')

    def test_get_experiments(self, workspace):
        exps = workspace.entity.get_experiments()
        assert exps == [
            create_experiment_entity('AwesomeWorkspace', 'as9f-3df5'),
            create_experiment_entity('AwesomeWorkspace', 'dd9f-3df5'),
        ]

    def test_create_experiment(self, workspace):
        exp = workspace.entity.create_experiment({})
        assert exp == create_experiment_entity('AwesomeWorkspace', 'pid_2009')

    def test_create_experiment_with_user_data(self, workspace):
        user_data = {"customWsGetKey": "customWsGetValue"}
        exp = workspace.entity.create_experiment({}, user_data)

        workspace.service.experiment_create.assert_has_calls(
            [mock.call('AwesomeWorkspace', {}, user_data)]
        )

    def test_execute_options_dict(self, workspace):
        exp = workspace.entity.execute({})
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
        exp = experiment.entity.execute()
        assert exp == ExperimentOperation('AwesomeWorkspace', 'pid_2009')

    def test_execute_with_case_filter(self, batch_experiment_with_case_filter):
        experiment = batch_experiment_with_case_filter.entity
        exp_sal = batch_experiment_with_case_filter.service
        case_generated = experiment.execute(with_cases=[]).wait()
        exp_sal.experiment_execute.assert_has_calls(
            [mock.call('Workspace', 'Experiment', [])]
        )
        exp_sal.case_put.assert_not_called()

        case_to_execute = case_generated.get_cases()[2]
        result = experiment.execute(with_cases=[case_to_execute]).wait()
        exp_sal.experiment_execute.assert_has_calls(
            [mock.call('Workspace', 'Experiment', ["case_3"])]
        )
        exp_sal.case_put.assert_has_calls(
            [mock.call('Workspace', 'Experiment', "case_3", mock.ANY)]
        )

        assert result == create_experiment_entity('AwesomeWorkspace', 'Experiment')
        assert result.run_info.successful == 1
        assert result.run_info.not_started == 3
        assert experiment.get_case('case_3').is_successful()

    def test_get_cases_label(self, batch_experiment_with_case_filter):
        experiment = batch_experiment_with_case_filter.entity
        cases = experiment.get_cases_with_label('Cruise operating point')
        assert cases == [
            create_case_entity("case_2", "Workspace", "Test"),
            create_case_entity("case_4", "Workspace", "Test"),
        ]

    def test_execute_with_case_filter_no_sync(self, batch_experiment_with_case_filter):
        experiment = batch_experiment_with_case_filter.entity
        exp_sal = batch_experiment_with_case_filter.service
        case_generated = experiment.execute(with_cases=[]).wait()
        case_to_execute = case_generated.get_cases()[2]
        experiment.execute(with_cases=[case_to_execute], sync_case_changes=False).wait()
        exp_sal.experiment_execute.assert_has_calls(
            [mock.call('Workspace', 'Experiment', ["case_3"])]
        )
        exp_sal.case_put.assert_not_called()

    def test_execute_successful(self, experiment):
        experiment = experiment.entity
        assert experiment.id == "Test"
        assert experiment.is_successful()
        assert experiment.run_info.status == ExperimentStatus.DONE
        assert experiment.run_info.errors == []
        assert experiment.run_info.failed == 0
        assert experiment.run_info.successful == 1
        assert experiment.run_info.cancelled == 0
        assert experiment.run_info.not_started == 0
        assert experiment.get_variables() == ["inertia.I", "time"]
        assert experiment.get_cases() == [
            create_case_entity("case_1", "Workspace", "Test")
        ]
        assert experiment.get_case("case_1") == create_case_entity(
            "case_1", "Workspace", "Test"
        )

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
            create_case_entity("case_1", "Workspace", "Experiment"),
            create_case_entity("case_2", "Workspace", "Experiment"),
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
            create_case_entity("case_1", "Workspace", "Experiment"),
            create_case_entity("case_2", "Workspace", "Experiment"),
            create_case_entity("case_3", "Workspace", "Experiment"),
            create_case_entity("case_4", "Workspace", "Experiment"),
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
            create_case_entity("case_1", "Workspace", "Experiment")
        ]
        assert experiment_with_failed_case.get_case("case_1") == create_case_entity(
            "case_1", "Workspace", "Experiment"
        )
        assert not experiment_with_failed_case.is_successful()
        assert experiment_with_failed_case.get_trajectories(['inertia.I']) == {
            'case_1': {'inertia.I': [1, 2, 3, 4]}
        }

    def test_cancelled_execution(self, cancelled_experiment):
        assert cancelled_experiment.run_info.status == ExperimentStatus.CANCELLED
        assert cancelled_experiment.get_cases() == [
            create_case_entity("case_1", "Workspace", "Test")
        ]
        assert cancelled_experiment.get_case("case_1") == create_case_entity(
            "case_1", "Workspace", "Experiment"
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
        pytest.raises(TypeError, experiment.entity.get_trajectories, 'hh')

    def test_exp_trajectories_invalid_keys(self, experiment):
        pytest.raises(ValueError, experiment.entity.get_trajectories, ['s'])

    def test_execute_with_user_data(self, workspace):
        user_data = {"workspaceExecuteKey": "workspaceExecuteValue"}
        workspace.entity.execute({}, user_data).wait()

        workspace.service.experiment_create.assert_has_calls(
            [mock.call('AwesomeWorkspace', {}, user_data)]
        )


def get_case_put_json_input(mock_method_call):
    (args, _) = tuple(mock_method_call)
    (_, _, _, put_json_input) = args
    return put_json_input


def get_case_put_call_consistent_value(mock_method_call):
    json = get_case_put_json_input(mock_method_call)
    return json['run_info']['consistent']


class TestCase:
    def test_case(self, experiment):
        case = experiment.entity.get_case("case_1")
        assert case.id == "case_1"
        assert case.run_info.status == CaseStatus.SUCCESSFUL
        assert case.run_info.consistent is True
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

    def test_case_sync(self, experiment, batch_experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        case.input.parametrization = {'PI.k': 120}
        case.input.analysis.simulation_options = {'ncp': 600}
        case.input.analysis.solver_options = {'atol': 1e-8}
        case.input.analysis.simulation_log_level = "DEBUG"
        case.input.analysis.parameters = {"start_time": 1, "final_time": 2e5}
        case.meta.label = "Cruise operating condition"
        case_2 = batch_experiment.get_case('case_2')
        case.initialize_from_case = case_2
        case.sync()
        exp_sal.case_put.assert_has_calls(
            [
                mock.call(
                    'Workspace',
                    'Test',
                    'case_1',
                    {
                        'id': 'case_1',
                        'run_info': {'status': 'successful', 'consistent': True},
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
                            "initialize_from_external_result": None,
                        },
                        "meta": {'label': 'Cruise operating condition'},
                    },
                )
            ]
        )
        result = case.execute().wait()
        assert result == create_case_entity('case_1', 'AwesomeWorkspace', 'pid_2009')

    def test_case_execute_with_no_sync(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        result = case.execute(sync_case_changes=True).wait()
        exp_sal.case_put.assert_called_once()
        assert result == create_case_entity('case_1', 'AwesomeWorkspace', 'pid_2009')

    def test_case_execute_with_auto_sync(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        result = case.execute(sync_case_changes=False).wait()
        exp_sal.case_put.assert_not_called()
        assert result == create_case_entity('case_1', 'AwesomeWorkspace', 'pid_2009')

    def test_case_sync_second_time_should_call_with_consistent_false(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service

        case = exp.get_case("case_1")
        case.input.parametrization = {'PI.k': 120}
        case.sync()
        case.sync()
        case_put_calls = exp_sal.case_put.call_args_list
        assert len(case_put_calls) == 2
        assert get_case_put_call_consistent_value(case_put_calls[0]) is True
        assert get_case_put_call_consistent_value(case_put_calls[1]) is False

    def test_case_initialize_from_external_result(self, experiment):
        result = create_external_result_entity('upload_id')
        case = experiment.entity.get_case("case_1")
        case.initialize_from_external_result = result
        assert case.initialize_from_external_result == result
        case.sync()
        exp_sal = experiment.service
        exp_sal.case_put.assert_has_calls(
            [
                mock.call(
                    'Workspace',
                    'Test',
                    'case_1',
                    {
                        'id': 'case_1',
                        'run_info': {'status': 'successful', 'consistent': True},
                        'input': {
                            'fmu_id': 'modelica_fluid_examples_heatingsystem_20210130_114628_bbd91f1',
                            'analysis': {
                                'analysis_function': 'dynamic',
                                'parameters': {'start_time': 0, 'final_time': 1},
                                'simulation_options': {},
                                'solver_options': {},
                                'simulation_log_level': 'NOTHING',
                            },
                            'parametrization': {},
                            'structural_parametrization': {},
                            'fmu_base_parametrization': {},
                            'initialize_from_case': None,
                            'initialize_from_external_result': {
                                'uploadId': 'upload_id'
                            },
                        },
                        "meta": {"label": "Cruise operating point"},
                    },
                )
            ]
        )

    def test_reinitiazlizing_result_initialized_case_from_case(self, experiment):
        result = create_external_result_entity('upload_id')
        case_to_init = create_case_entity('Case_2', 'ws_id', 'exp_id')
        case = experiment.entity.get_case("case_1")
        case.initialize_from_external_result = result
        with pytest.raises(Exception) as err:
            case.initialize_from_case = case_to_init
        assert (
            str(err.value) == "A case cannot use both 'initialize_from_case' and "
            "'initialize_from_external_result' to specify what to initialize from! "
            "To resolve this, set the 'initialize_from_external_result' attribute "
            "to None and re-try."
        )

    def test_reinitiazlizing_case_initialized_case_from_result(self, experiment):
        result = create_external_result_entity('upload_id')
        case_to_init = create_case_entity('Case_2', 'ws_id', 'exp_id')
        case = experiment.entity.get_case("case_1")
        case.initialize_from_case = case_to_init
        with pytest.raises(Exception) as err:
            case.initialize_from_external_result = result
        assert (
            str(err.value) == "A case cannot use both 'initialize_from_case' and "
            "'initialize_from_external_result' to specify what to initialize from! "
            "To resolve this, set the 'initialize_from_case' attribute "
            "to None and re-try."
        )

    def test_set_case_label(self, experiment):
        exp = experiment.entity
        exp_sal = experiment.service
        exp.set_label('Label')
        exp_sal.experiment_set_label.assert_has_calls(
            [mock.call('Workspace', 'Test', 'Label')]
        )

    def test_case_input(self, experiment):
        exp = experiment.entity

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

    def test_get_result_invalid_format(self, experiment):
        case = experiment.entity.get_case("case_1")
        pytest.raises(ValueError, case.get_result, 'ma')

