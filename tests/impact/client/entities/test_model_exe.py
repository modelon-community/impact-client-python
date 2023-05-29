import pytest
import os
import tempfile
from xml.etree import ElementTree
from modelon.impact.client import exceptions

from modelon.impact.client.entities.model_executable import ModelExecutableStatus
from tests.impact.client.helpers import IDs, MODEL_DESCRIPTION_XML


class TestModelExecutable:
    def test_compile_successful(self, fmu):
        assert fmu.id == IDs.FMU_PRIMARY
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

    def test_parse_model_description(self, fmu):
        model_description = fmu.get_model_description()
        assert model_description == MODEL_DESCRIPTION_XML
        tree = ElementTree.fromstring(model_description)
        model_variables =tree.find('ModelVariables')
        variable_names = [child.attrib.get('name') for child in model_variables]  
        assert variable_names == ['_block_jacobian_check', '_block_jacobian_check_tol']


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

    def test_download_fmu_failed_compilation(self, fmu_compile_failed):
        pytest.raises(
            exceptions.OperationFailureError,
            fmu_compile_failed.download,
        )

    def test_download_fmu_no_path(self, fmu):
        t = os.path.join(tempfile.gettempdir(), 'impact-downloads', fmu.id + '.fmu')
        resp = fmu.download()
        assert resp == t

    def test_can_be_put_uniquely_in_set(self, fmu):
        fmu_set = set([fmu, fmu])
        assert len(fmu_set) == 1
