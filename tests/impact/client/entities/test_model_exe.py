import os
import tempfile
from xml.etree import ElementTree

import pytest

from modelon.impact.client import exceptions
from modelon.impact.client.entities.model_executable import (
    ModelExecutable,
    ModelExecutableStatus,
)
from modelon.impact.client.operations.model_executable import ModelExecutableOperation
from tests.impact.client.helpers import ClientHelper, IDs


class TestModelExecutable:
    @pytest.mark.vcr()
    def test_compile_successful(self, capfd, client_helper: ClientHelper):
        fmu = client_helper.compile_fmu(
            model_path=IDs.FILTER_MODELICA_CLASS_PATH,
            custom_function_name="steady state",
        )
        assert isinstance(fmu, ModelExecutable)
        assert fmu.id
        assert fmu.is_successful()
        settable_params = fmu.get_settable_parameters()
        assert len(settable_params) == 76
        assert "Bessel.gain" in settable_params
        log = fmu.get_log()
        assert log == "\n"
        log.show()
        out, err = capfd.readouterr()
        assert out == "\n\n"
        assert fmu.metadata == {
            "steady_state": {
                "residual_variable_count": 0,
                "iteration_variable_count": 0,
            }
        }
        assert fmu.run_info.status == ModelExecutableStatus.SUCCESSFUL
        assert fmu.run_info.errors == []

    @pytest.mark.vcr()
    def test_delete_fmu(self, client_helper: ClientHelper):
        fmu = client_helper.compile_fmu(
            model_path=IDs.FILTER_MODELICA_CLASS_PATH,
            custom_function_name="steady state",
        )
        assert isinstance(fmu, ModelExecutable)
        fmus = client_helper.workspace.get_fmus()
        assert len(fmus) == 1
        assert fmus[0].id == fmu.id

        fmu.delete()

        fmus = client_helper.workspace.get_fmus()
        assert len(fmus) == 0

    @pytest.mark.vcr()
    def test_parse_model_description(self, client_helper: ClientHelper):
        fmu = client_helper.compile_fmu()
        assert isinstance(fmu, ModelExecutable)
        model_description = fmu.get_model_description()
        tree = ElementTree.fromstring(model_description)
        model_variables = tree.find("ModelVariables")
        variable_names = [child.attrib.get("name") for child in model_variables]
        assert "PI.Dzero.k" in variable_names

    @pytest.mark.vcr()
    def test_compilation_running(self, client_helper: ClientHelper):
        fmu_compile_running_ops = client_helper.compile_fmu(wait_for_completion=False)
        assert isinstance(fmu_compile_running_ops, ModelExecutableOperation)
        fmu_compile_running = client_helper.workspace.get_fmu(
            fmu_compile_running_ops.id
        )
        assert fmu_compile_running.run_info.status == ModelExecutableStatus.NOTSTARTED
        pytest.raises(exceptions.OperationNotCompleteError, fmu_compile_running.get_log)
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_running.get_settable_parameters,
        )
        assert not fmu_compile_running.is_successful()

    @pytest.mark.vcr()
    def test_compilation_failed(self, client_helper: ClientHelper):
        fmu_compile_failed = client_helper.compile_fmu(
            model_path=IDs.PID_MODELICA_CLASS_PATH + "(inertia1.J=True)"
        )
        assert isinstance(fmu_compile_failed, ModelExecutable)
        assert fmu_compile_failed.run_info.status == ModelExecutableStatus.FAILED
        assert not fmu_compile_failed.is_successful()
        assert (
            fmu_compile_failed.get_log() == "Error at line 2, column 52, in model "
            "'Modelica.Blocks.Examples.PID_Controller':\n    Cannot find declaration "
            "for True\n"
        )
        pytest.raises(
            exceptions.OperationFailureError, fmu_compile_failed.get_settable_parameters
        )

    def test_compilation_cancelled(self, fmu_compile_cancelled):
        assert fmu_compile_cancelled.run_info.status == ModelExecutableStatus.CANCELLED
        assert not fmu_compile_cancelled.is_successful()
        pytest.raises(exceptions.OperationFailureError, fmu_compile_cancelled.get_log)
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_cancelled.get_settable_parameters,
        )

    @pytest.mark.vcr()
    def test_create_experiment_definition(self, client_helper: ClientHelper):
        fmu = client_helper.compile_fmu()
        custom_function = client_helper.workspace.get_custom_function("dynamic")
        assert isinstance(fmu, ModelExecutable)
        experiment_definition = fmu.new_experiment_definition(
            custom_function=custom_function,
            simulation_options=custom_function.get_simulation_options().with_values(
                ncp=2000, rtol=0.1
            ),
        )
        config = experiment_definition.to_dict()
        assert config["experiment"]["base"]["model"]["fmu"]["id"] == fmu.id
        assert config["experiment"]["base"]["analysis"]["simulationOptions"] == {
            "ncp": 2000,
            "rtol": 0.1,
            "dynamic_diagnostics": False,
        }

    @pytest.mark.vcr()
    def test_download_fmu(self, client_helper: ClientHelper):
        fmu = client_helper.compile_fmu()
        assert isinstance(fmu, ModelExecutable)
        t = os.path.join(tempfile.gettempdir(), fmu.id + ".fmu")
        resp = fmu.download(tempfile.gettempdir())
        assert resp == t

    @pytest.mark.vcr()
    def test_download_fmu_failed_compilation(self, client_helper: ClientHelper):
        fmu_compile_failed = client_helper.compile_fmu(
            model_path=IDs.PID_MODELICA_CLASS_PATH + "(inertia1.J=True)"
        )
        assert isinstance(fmu_compile_failed, ModelExecutable)
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_failed.download,
        )

    @pytest.mark.vcr()
    def test_download_fmu_no_path(self, client_helper: ClientHelper):
        fmu = client_helper.compile_fmu()
        assert isinstance(fmu, ModelExecutable)
        t = os.path.join(tempfile.gettempdir(), "impact-downloads", fmu.id + ".fmu")
        resp = fmu.download()
        assert resp == t

    @pytest.mark.vcr()
    def test_can_be_put_uniquely_in_set(self, fmu):
        fmu_set = set([fmu, fmu])
        assert len(fmu_set) == 1
