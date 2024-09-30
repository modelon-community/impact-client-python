import os
import tempfile
from datetime import datetime

import pytest

from modelon.impact.client import Range, exceptions
from modelon.impact.client.entities.case import CaseStatus
from modelon.impact.client.entities.file_uri import CustomArtifactURI
from tests.files.paths import TEST_CSV_RESULT_PATH
from tests.impact.client.helpers import (
    ClientHelper,
    IDs,
    create_case_entity,
    create_external_result_entity,
)


class TestCase:
    @pytest.mark.vcr()
    def test_case(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        assert case.id == IDs.CASE_ID_PRIMARY
        assert str(case) == f"Case with id '{IDs.CASE_ID_PRIMARY}'"
        assert case.run_info.status == CaseStatus.SUCCESSFUL
        assert case.run_info.consistent
        assert isinstance(case.run_info.started, datetime)
        assert isinstance(case.run_info.finished, datetime)
        assert "Final Run Statistics:" in case.get_log()
        result, name = case.get_result()
        assert name.startswith(IDs.PID_MODELICA_CLASS_PATH)
        assert isinstance(result, bytes)
        assert case.is_successful()
        assert case.get_trajectories()["inertia1.w"][-1] == 0.5000116056397186
        fmu = case.get_fmu()
        assert fmu.id
        analysis_function = case.input.analysis.analysis_function
        assert analysis_function == "dynamic"

    @pytest.mark.vcr()
    def test_multiple_cases(self, client_helper: ClientHelper):
        batch_experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={"PI.yMax": Range(12, 13, 2)},
        )
        case_2 = batch_experiment.get_case(IDs.CASE_ID_SECONDARY)
        assert case_2.id == IDs.CASE_ID_SECONDARY
        assert case_2.run_info.status == CaseStatus.SUCCESSFUL
        assert "Final Run Statistics:" in case_2.get_log()
        result, name = case_2.get_result()
        assert name.startswith(IDs.PID_MODELICA_CLASS_PATH)
        assert isinstance(result, bytes)
        assert case_2.is_successful()
        result = case_2.get_trajectories()
        assert len(result.keys()) == 140
        assert result["inertia1.w"][-1] == 0.5000116056397186
        assert case_2.input.structural_parametrization == {"PI.yMax": 13}
        assert case_2.input.fmu_base_parametrization == {}

    @pytest.mark.vcr()
    def test_failed_case(self, client_helper: ClientHelper):
        experiment_with_failed_case = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={"inertia1.J": 0},
        )
        failed_case = experiment_with_failed_case.get_case(IDs.CASE_ID_PRIMARY)
        assert failed_case.id == IDs.CASE_ID_PRIMARY
        assert failed_case.run_info.status == CaseStatus.FAILED
        assert not failed_case.is_successful()
        pytest.raises(exceptions.OperationFailureError, failed_case.get_result)
        assert failed_case.get_trajectories()["inertia1.w"][-1] == 0.0

    @pytest.mark.vcr()
    def test_failed_execution_result(self, client_helper: ClientHelper):
        experiment_with_failed_case = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={"inertia1.J": 0},
        )
        pytest.raises(
            exceptions.OperationFailureError,
            experiment_with_failed_case.get_case(IDs.CASE_ID_PRIMARY).get_result,
        )

    @pytest.mark.vcr()
    def test_case_execute_explicit_sync(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={},
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case.input.parametrization = {"PI.k": 120}
        case.input.analysis.simulation_options = {"ncp": 600}
        case.input.analysis.solver_options = {"atol": 1e-8}
        case.input.analysis.simulation_log_level = "DEBUG"
        case.input.analysis.parameters = {"start_time": 1, "final_time": 2e5}
        case.meta.label = "Cruise operating condition"

        case.sync()

        result_case = case.execute(sync_case_changes=False).wait()
        assert result_case.input.parametrization == {"PI.k": 120}
        assert result_case.input.analysis.simulation_options == {"ncp": 600}
        assert result_case.input.analysis.solver_options == {"atol": 1e-8}
        assert result_case.input.analysis.simulation_log_level == "DEBUG"
        assert result_case.input.analysis.parameters == {
            "start_time": 1,
            "final_time": 2e5,
        }
        assert result_case.meta.label == "Cruise operating condition"

    @pytest.mark.vcr()
    def test_case_execute_implicit_sync(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case.input.parametrization = {"PI.k": 120}

        result_case = case.execute(sync_case_changes=True).wait()

        assert result_case.input.parametrization == {"PI.k": 120}

    @pytest.mark.vcr()
    def test_case_execute_with_auto_sync(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case.input.parametrization = {"PI.k": 120}

        result_case = case.execute(sync_case_changes=False).wait()

        assert result_case.input.parametrization == {}

    @pytest.mark.vcr()
    def test_consistent_flag_set_to_false_when_calling_sync(
        self, client_helper: ClientHelper
    ):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case.input.parametrization = {"PI.k": 120}

        assert case.run_info.consistent

        case.sync()

        assert not case.run_info.consistent

    @pytest.mark.vcr()
    def test_case_initialize_from_external_result(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        result = create_external_result_entity(IDs.EXTERNAL_RESULT_ID)
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case.initialize_from_external_result = result
        assert case.initialize_from_external_result == result

        case.sync()

        assert (
            case.info["input"]["initializeFromExternalResult"]["uploadId"]
            == IDs.EXTERNAL_RESULT_ID
        )

    @pytest.mark.vcr()
    def test_reinitiazlizing_result_initialized_case_from_case(
        self, client_helper: ClientHelper
    ):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        result = create_external_result_entity("upload_id")
        case_to_init = create_case_entity(
            IDs.CASE_ID_SECONDARY, IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case.initialize_from_external_result = result
        with pytest.raises(Exception) as err:
            case.initialize_from_case = case_to_init
        assert (
            str(err.value) == "A case cannot use both 'initialize_from_case' and "
            "'initialize_from_external_result' to specify what to initialize from! "
            "To resolve this, set the 'initialize_from_external_result' attribute "
            "to None and re-try."
        )

    @pytest.mark.vcr()
    def test_reinitiazlizing_case_initialized_case_from_result(
        self, client_helper: ClientHelper
    ):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        result = create_external_result_entity(IDs.EXTERNAL_RESULT_ID)
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)

        case_to_init = create_case_entity(
            IDs.CASE_ID_SECONDARY, IDs.WORKSPACE_ID_PRIMARY, IDs.EXPERIMENT_ID_PRIMARY
        )
        case.initialize_from_case = case_to_init

        with pytest.raises(Exception) as err:
            case.initialize_from_external_result = result
        assert (
            str(err.value) == "A case cannot use both 'initialize_from_case' and "
            "'initialize_from_external_result' to specify what to initialize from! "
            "To resolve this, set the 'initialize_from_case' attribute "
            "to None and re-try."
        )

    @pytest.mark.vcr()
    def test_case_input(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case.input.analysis.parameters = {"start_time": 0, "final_time": 90}
        case.input.analysis.simulation_options = {"ncp": 600}
        case.input.analysis.solver_options = {"atol": 1e-8}
        case.input.analysis.simulation_log_level = "DEBUG"
        case.input.parametrization = {"PI.k": 120}

        assert case.input.analysis.parameters == {"start_time": 0, "final_time": 90}
        assert case.input.analysis.simulation_options == {"ncp": 600}
        assert case.input.analysis.solver_options == {"atol": 1e-8}
        assert case.input.parametrization == {"PI.k": 120}

    @pytest.mark.vcr()
    def test_get_result_invalid_format(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        pytest.raises(ValueError, case.get_result, "ma")

    def test_get_custom_artifacts(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
        artifacts = case.get_artifacts()
        assert len(artifacts) == 1
        assert artifacts[0].id == IDs.CUSTOM_ARTIFACT_ID
        assert artifacts[0].download_as == IDs.RESULT_MAT
        t = os.path.join(tempfile.gettempdir(), artifacts[0].download_as)
        resp = artifacts[0].download(tempfile.gettempdir())
        assert resp == t
        artifact_stream = artifacts[0].get_data()
        assert artifact_stream == b"\x00\x00\x00\x00"

    def test_get_custom_artifact(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
        artifact = case.get_artifact(IDs.CUSTOM_ARTIFACT_ID)
        assert artifact.id == IDs.CUSTOM_ARTIFACT_ID
        assert artifact.download_as == IDs.RESULT_MAT
        t = os.path.join(tempfile.gettempdir(), artifact.download_as)
        resp = artifact.download(tempfile.gettempdir())
        assert resp == t
        artifact_stream = artifact.get_data()
        assert artifact_stream == b"\x00\x00\x00\x00"

    @pytest.mark.experimental
    def test_get_custom_artifact_uri(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
        artifact = case.get_artifact(IDs.CUSTOM_ARTIFACT_ID)
        artifact_uri = artifact.get_uri()
        assert isinstance(artifact_uri, CustomArtifactURI)
        assert str(artifact_uri) == IDs.ARTIFACT_RESOURCE_URI

    def test_get_custom_artifact_with_download_as(self, experiment):
        case = experiment.entity.get_case(IDs.CASE_ID_PRIMARY)
        artifact = case.get_artifact(IDs.CUSTOM_ARTIFACT_ID, "something.mat")
        assert artifact.id == IDs.CUSTOM_ARTIFACT_ID
        assert artifact.download_as == "something.mat"
        t = os.path.join(tempfile.gettempdir(), artifact.download_as)
        resp = artifact.download(tempfile.gettempdir())
        assert resp == t
        artifact_stream = artifact.get_data()
        assert artifact_stream == b"\x00\x00\x00\x00"

    @pytest.mark.vcr()
    def test_get_csv_result(self, client_helper: ClientHelper):
        batch_experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={},
        )
        case = batch_experiment.get_case(IDs.CASE_ID_PRIMARY)
        assert case.run_info.status == CaseStatus.SUCCESSFUL
        result, name = case.get_result(format="csv")
        assert name.startswith(IDs.PID_MODELICA_CLASS_PATH)
        assert isinstance(result, str)

    @pytest.mark.vcr()
    def test_case_get_variables(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        case_vars = case.get_variables()
        assert len(case_vars) == 140

    @pytest.mark.vcr()
    def test_case_import_custom_artifact(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        custom_artifact = case.import_custom_artifact(
            path_to_artifact=TEST_CSV_RESULT_PATH, artifact_id=IDs.CUSTOM_ARTIFACT_ID
        ).wait()

        # Attempt reimport with same ID fails
        assert custom_artifact.id == IDs.CUSTOM_ARTIFACT_ID
        with pytest.raises(exceptions.IllegalCustomArtifactImport):
            custom_artifact = case.import_custom_artifact(
                path_to_artifact=TEST_CSV_RESULT_PATH,
                artifact_id=IDs.CUSTOM_ARTIFACT_ID,
            ).wait()

        # Overwrite artifact with same ID
        custom_artifact = case.import_custom_artifact(
            path_to_artifact=TEST_CSV_RESULT_PATH,
            artifact_id=IDs.CUSTOM_ARTIFACT_ID,
            overwrite=True,
        ).wait()
        assert custom_artifact.id == IDs.CUSTOM_ARTIFACT_ID

    @pytest.mark.vcr()
    def test_case_import_custom_artifact_default_artifact_id(
        self, client_helper: ClientHelper
    ):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        custom_artifact = case.import_custom_artifact(
            path_to_artifact=TEST_CSV_RESULT_PATH
        ).wait()

        assert custom_artifact.id == "imported_1"

        # TODO: extend test
        #    data = custom_artifact.get_data()
        #    assert data == open(TEST_CSV_RESULT_PATH, "rb").read()

    @pytest.mark.vcr()
    def test_case_import_result(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)

        # Attempt import with existing result fails
        with pytest.raises(exceptions.IllegalCaseResultImport):
            result = case.import_result(path_to_result=TEST_CSV_RESULT_PATH).wait()

        # Overwrite result
        result = case.import_result(
            path_to_result=TEST_CSV_RESULT_PATH, overwrite=True
        ).wait()
        assert result["J1.w"] == [1.0]

        case = experiment.get_case(IDs.CASE_ID_PRIMARY)
        assert not case.run_info.consistent
