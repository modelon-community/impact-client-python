import unittest.mock
import modelon.impact.client.sal.service
import pytest
import os
import tempfile
import modelon.impact.client.operations
import modelon.impact.client.options
from tests.files.paths import SINGLE_FILE_LIBRARY_PATH
from tests.impact.client.fixtures import *


class TestWorkspace:
    def test_workspace_get_custom_function(self, custom_function_parameter_list):
        custom_function_service = unittest.mock.MagicMock()
        custom_function_service.custom_function_get.return_value = {
            'name': 'dynamic',
            'parameters': custom_function_parameter_list,
        }
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', custom_function_service=custom_function_service
        )
        custom_function = ws.get_custom_function('dynamic')
        assert 'dynamic' == custom_function.name

    def test_workspace_get_custom_functions(self, custom_function_parameter_list):
        custom_function_service = unittest.mock.MagicMock()
        custom_function_service.custom_functions_get.return_value = {
            'data': {
                'items': [
                    {'name': 'dynamic', 'parameters': custom_function_parameter_list}
                ]
            }
        }
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', custom_function_service=custom_function_service
        )
        custom_function_list = [
            custom_function.name for custom_function in ws.get_custom_functions()
        ]
        assert ['dynamic'] == custom_function_list

    def test_del_workspace(self, workspace, delete_workspace):
        workspace.delete()
        delete_call = delete_workspace.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace' == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_import_lib(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.library_import.return_value = {
            "name": "Single",
            "uses": {"Modelica": {"version": "3.2.2"}},
        }
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        resp = ws.import_library(SINGLE_FILE_LIBRARY_PATH)
        assert resp == {
            "name": "Single",
            "uses": {"Modelica": {"version": "3.2.2"}},
        }

    def test_get_model(self):
        ws = modelon.impact.client.entities.Workspace('AwesomeWorkspace')
        model = ws.get_model("Modelica.Blocks.PID")
        assert model == modelon.impact.client.entities.Model(
            "Modelica.Blocks.PID", ws.id
        )

    def test_lock_workspace(self, workspace, lock_workspace):
        workspace.lock()
        lock_call = lock_workspace.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/lock'
            == lock_call.url
        )
        assert 'POST' == lock_call.method

    def test_unlock_workspace(self, workspace, unlock_workspace):
        workspace.unlock()
        unlock_call = unlock_workspace.adapter.request_history[3]
        assert (
            'http://mock-impact.com/api/workspaces/AwesomeWorkspace/lock'
            == unlock_call.url
        )
        assert 'DELETE' == unlock_call.method

    def test_clone_workspace(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.workspace_clone.return_value = {"workspace_id": "MyClonedWorkspace"}
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        resp = ws.clone()
        assert resp == modelon.impact.client.entities.Workspace(
            'MyClonedWorkspace', workspace_service=ws_service
        )

    def test_get_fmus(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.fmus_get.return_value = {
            'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'as9D-4df5'}]}
        }
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        resp = ws.get_fmus()
        assert resp == [
            modelon.impact.client.entities.ModelExecutable(
                'AwesomeWorkspace', 'as9f-3df5'
            ),
            modelon.impact.client.entities.ModelExecutable(
                'AwesomeWorkspace', 'as9D-4df5'
            ),
        ]

    def test_get_fmu(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.fmu_get.return_value = {'id': 'pid_20090615_134'}
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        resp = ws.get_fmu('pid_20090615_134')
        assert resp == modelon.impact.client.entities.ModelExecutable(
            'AwesomeWorkspace', 'pid_20090615_134'
        )

    def test_get_experiment(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.experiment_get.return_value = {'id': 'pid_20090615_134'}
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        resp = ws.get_experiment('pid_20090615_134')
        assert resp == modelon.impact.client.entities.Experiment(
            'AwesomeWorkspace', 'pid_20090615_134'
        )

    def test_get_experiments(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.experiments_get.return_value = {
            'data': {'items': [{'id': 'as9f-3df5'}, {'id': 'dd9f-3df5'}]}
        }
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        resp = ws.get_experiments()
        assert resp == [
            modelon.impact.client.entities.Experiment('AwesomeWorkspace', 'as9f-3df5'),
            modelon.impact.client.entities.Experiment('AwesomeWorkspace', 'dd9f-3df5'),
        ]

    def test_create_experiment(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.experiment_create.return_value = {"experiment_id": "pid_2009"}
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        resp = ws.create_experiment({})
        assert resp == modelon.impact.client.entities.Experiment(
            'AwesomeWorkspace', 'pid_2009'
        )

    def test_download_workspace(self):
        ws_service = unittest.mock.MagicMock()
        ws_service.workspace_download.return_value = '\x00\x00\x00\x00'
        ws = modelon.impact.client.entities.Workspace(
            'AwesomeWorkspace', workspace_service=ws_service
        )
        t = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        resp = ws.download({}, t)
        assert resp == t


class TestModel:
    def test_model_compile(self):
        model_exe_service = unittest.mock.MagicMock()
        model_exe_service.compile_model.return_value = 'test_pid_fmu_id'
        model = modelon.impact.client.entities.Model(
            'Test.PID', 'AwesomeWorkspace', model_exe_service=model_exe_service,
        )
        fmu = model.compile({})
        assert fmu == modelon.impact.client.operations.ModelExecutable(
            'AwesomeWorkspace', fmu.id
        )
        assert fmu.id == 'test_pid_fmu_id'


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
        options = {"compiler": {"c_compiler": "gcc"}}
        custom_function._custom_func_sal.custom_function_options_get.return_value = (
            options
        )
        new = custom_function.options()
        assert new.to_dict() == {"compiler": {"c_compiler": "gcc"}}
        assert isinstance(new, modelon.impact.client.options.ExecutionOption)
