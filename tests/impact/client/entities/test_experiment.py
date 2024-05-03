import pytest

from modelon.impact.client import exceptions
from modelon.impact.client.entities.experiment import (
    ExperimentResultPoint,
    ExperimentStatus,
    _Workflow,
)
from modelon.impact.client.experiment_definition.operators import Choices, Range
from modelon.impact.client.operations.base import Status
from modelon.impact.client.operations.experiment import ExperimentOperation
from tests.impact.client.helpers import ClientHelper, IDs


class TestExperiment:
    @pytest.mark.vcr()
    def test_execute(self, client_helper: ClientHelper):
        exp = client_helper.create_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH, modifiers={}
        )
        result = exp.execute()
        assert isinstance(result, ExperimentOperation)

    @pytest.mark.vcr()
    def test_execute_with_case_filter(self, client_helper: ClientHelper):
        experiment = client_helper.create_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={"PI.yMax": Range(12, 13, 3)},
        )
        result = experiment.execute(with_cases=[]).wait()
        assert result.run_info.not_started == 3

        case_to_execute = experiment.get_cases()[2]
        result = experiment.execute(with_cases=[case_to_execute]).wait()

        assert result.run_info.successful == 1
        assert result.run_info.not_started == 2
        assert experiment.get_case("case_3").is_successful()

    @pytest.mark.vcr()
    def test_get_cases_label(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={"PI.yMax": Range(12, 13, 4)},
        )
        cases = experiment.get_cases()
        for case in cases[1:3]:
            case.meta.label = "Cruise operating point"
            case.sync()
        cases = experiment.get_cases_with_label("Cruise operating point")
        assert len(cases) == 2
        assert cases[0].id == "case_2"
        assert cases[1].id == "case_3"

    @pytest.mark.vcr()
    def test_execute_with_case_filter_no_sync(self, client_helper: ClientHelper):
        experiment = client_helper.create_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={"PI.yMax": Range(12, 13, 4)},
        )
        case_generated = experiment.execute(with_cases=[]).wait()
        case_to_execute = case_generated.get_cases()[2]
        case_to_execute.meta.label = "Test"

        # Executing without syncing case updates
        experiment = experiment.execute(
            with_cases=[case_to_execute], sync_case_changes=False
        ).wait()
        assert experiment.run_info.successful == 1
        assert experiment.run_info.not_started == 3
        case_to_execute = experiment.get_cases()[2]
        assert not case_to_execute.meta.label

    @pytest.mark.vcr()
    def test_experiment_get_last_time_point(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={},
        )
        exp_last_point = experiment.get_last_point(["inertia1.w", "time"])
        assert isinstance(exp_last_point, ExperimentResultPoint)
        assert exp_last_point.cases == ["case_1"]
        assert len(exp_last_point.variables) == 2
        assert exp_last_point.as_lists() == [[0.5000116056397186, 1.0]]

    @pytest.mark.vcr()
    def test_experiment_get_last_time_point_all_variables(
        self, client_helper: ClientHelper
    ):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={},
        )
        exp_last_point = experiment.get_last_point()
        assert isinstance(exp_last_point, ExperimentResultPoint)
        assert exp_last_point.cases == ["case_1"]
        assert len(exp_last_point.variables) == 140
        values = exp_last_point.as_lists()
        assert len(values) == 1
        assert values[0] and len(values[0]) == 140

    @pytest.mark.vcr()
    def test_successful_model_based_experiment(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            modifiers={},
        )
        assert experiment.id
        assert experiment.is_successful()
        assert experiment.run_info.status == ExperimentStatus.DONE
        assert experiment.run_info.errors == []
        assert experiment.run_info.failed == 0
        assert experiment.run_info.successful == 1
        assert experiment.run_info.cancelled == 0
        assert experiment.run_info.not_started == 0
        variables = experiment.get_variables()
        assert len(variables) == 140
        assert len(experiment.get_cases()) == 1
        assert experiment.get_case(IDs.CASE_ID_PRIMARY)

        exp = experiment.get_trajectories(["inertia1.w", "time"])
        assert exp[IDs.CASE_ID_PRIMARY]["inertia1.w"][-1] == 0.5000116056397186
        assert exp[IDs.CASE_ID_PRIMARY]["time"][-1] == 1.0

        assert experiment.get_class_name() == IDs.PID_MODELICA_CLASS_PATH
        assert experiment.custom_function == IDs.DYNAMIC_CF
        assert dict(experiment.get_compiler_options()) == {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        }
        assert dict(experiment.get_runtime_options()) == {}
        assert dict(experiment.get_solver_options()) == {}
        assert dict(experiment.get_simulation_options()) == {
            "dynamic_diagnostics": False,
            "ncp": 500,
        }

    @pytest.mark.vcr()
    def test_successful_fmu_based_experiment(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            workflow=_Workflow.FMU_BASED,
            modifiers={},
        )
        assert experiment.id
        assert experiment.is_successful()
        assert experiment.run_info.status == ExperimentStatus.DONE
        assert experiment.run_info.errors == []
        assert experiment.run_info.failed == 0
        assert experiment.run_info.successful == 1
        assert experiment.run_info.cancelled == 0
        assert experiment.run_info.not_started == 0
        variables = experiment.get_variables()
        assert len(variables) == 140
        assert len(experiment.get_cases()) == 1
        assert experiment.get_case(IDs.CASE_ID_PRIMARY)

        exp = experiment.get_trajectories(["inertia1.w", "time"])
        assert exp[IDs.CASE_ID_PRIMARY]["inertia1.w"][-1] == 0.5000116056397186
        assert exp[IDs.CASE_ID_PRIMARY]["time"][-1] == 1.0

        assert experiment.get_class_name() == IDs.PID_MODELICA_CLASS_PATH
        assert experiment.custom_function == IDs.DYNAMIC_CF
        assert dict(experiment.get_compiler_options()) == {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        }
        assert dict(experiment.get_runtime_options()) == {}
        assert dict(experiment.get_solver_options()) == {}
        assert dict(experiment.get_simulation_options()) == {
            "dynamic_diagnostics": False,
            "ncp": 500,
        }

    @pytest.mark.vcr()
    def test_successful_batch_execute(self, client_helper: ClientHelper):
        batch_experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            workflow=_Workflow.FMU_BASED,
            modifiers={"PI.k": Range(100, 120, 2)},
        )
        assert batch_experiment.is_successful()
        assert batch_experiment.run_info.status == ExperimentStatus.DONE
        assert batch_experiment.run_info.failed == 0
        assert batch_experiment.run_info.successful == 2
        assert batch_experiment.run_info.cancelled == 0
        assert batch_experiment.run_info.not_started == 0
        variables = batch_experiment.get_variables()
        assert len(variables) == 140
        assert len(batch_experiment.get_cases()) == 2
        exp = batch_experiment.get_trajectories(["inertia1.w"])
        assert exp[IDs.CASE_ID_PRIMARY]["inertia1.w"][-1] == 0.5000116056397186
        assert exp[IDs.CASE_ID_SECONDARY]["inertia1.w"][-1] == 0.49997531053261374

    @pytest.mark.vcr()
    def test_some_successful_batch_execute(self, client_helper: ClientHelper):
        batch_experiment_some_successful = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            workflow=_Workflow.CLASS_BASED,
            modifiers={"inertia1.J": Choices(1, 0, 2)},
        )
        assert not batch_experiment_some_successful.is_successful()
        assert batch_experiment_some_successful.run_info.status == ExperimentStatus.DONE
        assert batch_experiment_some_successful.run_info.failed == 1
        assert batch_experiment_some_successful.run_info.successful == 2
        assert batch_experiment_some_successful.run_info.cancelled == 0
        assert batch_experiment_some_successful.run_info.not_started == 0
        assert len(batch_experiment_some_successful.get_cases()) == 3

    @pytest.mark.vcr()
    def test_running_execution(self, client_helper: ClientHelper):
        running_experiment_ops = client_helper.create_and_execute_experiment(
            model_path=IDs.BATCH_PLANT_MODELICA_CLASS_PATH,
            workflow=_Workflow.CLASS_BASED,
            modifiers={},
            wait_for_completion=False,
        )
        running_experiment = client_helper.workspace.get_experiment(
            running_experiment_ops.id
        )
        assert running_experiment.run_info.status == ExperimentStatus.NOTSTARTED
        assert not running_experiment.is_successful()
        pytest.raises(
            exceptions.OperationNotCompleteError, running_experiment.get_variables
        )
        pytest.raises(
            exceptions.OperationNotCompleteError,
            running_experiment.get_trajectories,
            ["inertia1.w"],
        )

    @pytest.mark.vcr()
    def test_failed_execution(self, client_helper: ClientHelper):
        failed_experiment = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            workflow=_Workflow.FMU_BASED,
            modifiers={"PI.yMax": Range(12, 13, 3)},
        )
        assert failed_experiment.run_info.status == ExperimentStatus.FAILED
        assert not failed_experiment.is_successful()
        assert failed_experiment.run_info.errors == [
            "Modifiers can only be set for non-structural parameters on a model"
            " compiled to an FMU. Please remove range or any other modifier value "
            "set for 'PI.yMax', as these parameters are not settable",
        ]

    @pytest.mark.vcr()
    def test_execution_with_failed_cases(self, client_helper: ClientHelper):
        experiment_with_failed_case = client_helper.create_and_execute_experiment(
            model_path=IDs.PID_MODELICA_CLASS_PATH,
            workflow=_Workflow.FMU_BASED,
            modifiers={"inertia1.J": 0},
        )
        assert experiment_with_failed_case.run_info.status == ExperimentStatus.DONE
        assert len(experiment_with_failed_case.get_cases()) == 1
        assert experiment_with_failed_case.get_case(IDs.CASE_ID_PRIMARY)
        assert not experiment_with_failed_case.is_successful()
        assert experiment_with_failed_case.get_trajectories(["inertia1.w"]) == {
            IDs.CASE_ID_PRIMARY: {"inertia1.w": [0.0]}
        }

    @pytest.mark.vcr()
    def test_cancelled_execution(self, client_helper: ClientHelper):
        cancelled_experiment = client_helper.create_and_execute_experiment(
            wait_for_completion=False
        )
        cancelled_experiment.cancel()
        cancelled_experiment = cancelled_experiment.wait(status=Status.CANCELLED)
        assert cancelled_experiment.run_info.status == ExperimentStatus.CANCELLED
        assert not cancelled_experiment.is_successful()
        pytest.raises(
            exceptions.OperationFailureError, cancelled_experiment.get_variables
        )
        pytest.raises(
            exceptions.OperationFailureError,
            cancelled_experiment.get_trajectories,
            ["inertia.I"],
        )

    @pytest.mark.vcr()
    def test_exp_trajectories_non_list_entry(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment()
        pytest.raises(TypeError, experiment.get_trajectories, "hh")

    @pytest.mark.vcr()
    def test_exp_trajectories_invalid_keys(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment()
        pytest.raises(ValueError, experiment.get_trajectories, ["s"])

    @pytest.mark.vcr()
    def test_execute_with_user_data(self, client_helper: ClientHelper):
        user_data = {"workspaceExecuteKey": "workspaceExecuteValue"}
        experiment = client_helper.create_and_execute_experiment(user_data=user_data)
        assert experiment.metadata.user_data == user_data

    @pytest.mark.vcr()
    def test_set_experiment_label(self, client_helper: ClientHelper):
        experiment = client_helper.create_and_execute_experiment()
        experiment.set_label(IDs.EXPERIMENT_LABEL)
        assert experiment.label == IDs.EXPERIMENT_LABEL
