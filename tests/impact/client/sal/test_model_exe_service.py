import modelon.impact.client.sal.service
from modelon.impact.client.sal.uri import URI
from tests.impact.client.helpers import IDs
from tests.impact.client.fixtures import *


class TestModelExecutbleService:
    def test_compile_model(self, model_compile):
        uri = URI(model_compile.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=model_compile.context
        )
        options = {
            "input": {
                "class_name": "Workspace.PID_Controller",
                "compiler_options": {},
                "runtime_options": {"log_level": 4},
                "compiler_log_level": "warning",
                "fmi_target": "me",
                "fmi_version": "2.0",
                "platform": "win64",
            }
        }
        fmu_id, modifiers = service.model_executable.fmu_setup(
            IDs.WORKSPACE_PRIMARY, options, get_cached=False
        )
        assert fmu_id, modifiers == (None, {})
        service.model_executable.compile_model(IDs.WORKSPACE_PRIMARY, fmu_id)
        compile_call = model_compile.adapter.request_history
        assert len(compile_call) == 2
        assert f"http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables/"
        f"{IDs.FMU_PRIMARY}/compilation" == compile_call[1].url

    def test_get_cached_fmu_id(self, get_cached_fmu_id):
        uri = URI(get_cached_fmu_id.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_cached_fmu_id.context
        )
        options = {
            "input": {
                "class_name": "Workspace.PID_Controller",
                "compiler_options": {},
                "runtime_options": {"log_level": 4},
                "compiler_log_level": "warning",
                "fmi_target": "me",
                "fmi_version": "2.0",
                "platform": "win64",
            }
        }
        fmu_id, modifiers = service.model_executable.fmu_setup(
            IDs.WORKSPACE_PRIMARY, options, get_cached=True
        )
        cached_call = get_cached_fmu_id.adapter.request_history
        assert fmu_id, modifiers == (IDs.FMU_PRIMARY, {})
        assert len(cached_call) == 1
        assert (
            f"http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}/model-executables?getCached=true"
            == cached_call[0].url
        )

    def test_get_compile_log(self, get_compile_log):
        uri = URI(get_compile_log.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_compile_log.context
        )
        data = service.model_executable.compile_log(
            IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY
        )
        assert data == "Compiler arguments:..."

    def test_get_compile_status(self, get_compile_status):
        uri = URI(get_compile_status.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_compile_status.context
        )
        data = service.model_executable.compile_status(
            IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY
        )
        assert data == {
            "finished_executions": 0,
            "total_executions": 1,
            "status": "running",
            "progress": [{"message": "Compiling", "percentage": 0}],
        }

    def test_cancel_compile(self, cancel_compile):
        uri = URI(cancel_compile.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=cancel_compile.context
        )
        service.model_executable.compile_cancel(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
        assert cancel_compile.adapter.called

    def test_get_settable_parameters(self, get_settable_parameters):
        uri = URI(get_settable_parameters.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_settable_parameters.context
        )
        data = service.model_executable.settable_parameters_get(
            IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY
        )
        assert data == ["param1", "param3"]

    def test_get_ss_fmu_metadata(self, get_ss_fmu_metadata):
        uri = URI(get_ss_fmu_metadata.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_ss_fmu_metadata.context
        )
        data = service.model_executable.ss_fmu_metadata_get(
            IDs.WORKSPACE_PRIMARY,
            IDs.FMU_PRIMARY,
            parameter_state={"parameterState": {"x": 15}},
        )
        assert data == {
            "steady_state": {
                "residual_variable_count": 1,
                "iteration_variable_count": 2,
            }
        }

    def test_delete_fmu(self, delete_fmu):
        uri = URI(delete_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_fmu.context
        )
        service.model_executable.fmu_delete(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
        assert delete_fmu.adapter.called
