from modelon.impact.client.sal.uri import URI
import modelon.impact.client.sal.service
from modelon.impact.client.sal.experiment import ResultFormat
from tests.impact.client.helpers import IDs
from tests.impact.client.fixtures import *


class TestExperimentService:
    def test_model_execute(self, experiment_execute):
        uri = URI(experiment_execute.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_execute.context
        )
        service.experiment.experiment_execute(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        assert experiment_execute.adapter.called

    def test_model_execute_with_case_filter(self, experiment_execute):
        uri = URI(experiment_execute.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_execute.context
        )
        service.experiment.experiment_execute(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, case_ids=['case_1']
        )
        assert experiment_execute.adapter.called
        assert experiment_execute.adapter.request_history[0].json() == {
            'includeCases': {'ids': ['case_1']}
        }

    def test_set_label_for_experiment(self, set_experiment_label):
        uri = URI(set_experiment_label.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=set_experiment_label.context
        )
        service.experiment.experiment_set_label(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, "Label"
        )
        assert set_experiment_label.adapter.called
        assert set_experiment_label.adapter.request_history[0].json() == {
            'label': "Label"
        }

    def test_delete_experiment(self, delete_experiment):
        uri = URI(delete_experiment.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_experiment.context
        )
        service.experiment.experiment_delete(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        assert delete_experiment.adapter.called

    def test_get_experiment_status(self, experiment_status):
        uri = URI(experiment_status.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_status.context
        )
        data = service.experiment.execute_status(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        assert data == {
            "finished_executions": 1,
            "total_executions": 2,
            "status": "running",
            "progress": [{"message": "Simulating at 1.0", "percentage": 1}],
        }

    def test_cancel_execute(self, cancel_execute):
        uri = URI(cancel_execute.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=cancel_execute.context
        )
        service.experiment.execute_cancel(IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY)
        assert cancel_execute.adapter.called

    def test_get_result_variables(self, get_result_variables):
        uri = URI(get_result_variables.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_result_variables.context
        )
        data = service.experiment.result_variables_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        assert data == ["PI.J", "inertia.I"]

    def test_get_trajectories(self, get_trajectories):
        uri = URI(get_trajectories.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_trajectories.context
        )
        data = service.experiment.trajectories_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, ["variable1", "variable2"]
        )
        assert data == [[[1.0, 1.0], [3.0, 3.0], [5.0, 5.0]]]

    def test_get_cases(self, get_cases):
        uri = URI(get_cases.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_cases.context
        )
        data = service.experiment.cases_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        assert data == {"data": {"items": [{"id": "case_1"}]}}

    def test_get_case(self, get_case):
        uri = URI(get_case.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case.context
        )
        data = service.experiment.case_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, "case_1"
        )
        assert data == {"id": "case_1"}

    def test_put_case(self, put_case):
        uri = URI(put_case.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=put_case.context
        )
        service.experiment.case_put(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, "case_1", {}
        )
        assert put_case.adapter.called

    def test_get_case_log(self, get_case_log):
        uri = URI(get_case_log.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case_log.context
        )
        data = service.experiment.case_get_log(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, "case_1"
        )
        assert data == 'Simulation log..'

    def test_get_mat_case_result(self, get_mat_case_results):
        uri = URI(get_mat_case_results.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_mat_case_results.context
        )
        data, name = service.experiment.case_result_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, "case_1", ResultFormat.MAT,
        )
        assert data == b'\x00\x00\x00\x00'
        assert name == 'Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.mat'

    def test_get_csv_case_result(self, get_csv_case_results):
        uri = URI(get_csv_case_results.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_csv_case_results.context
        )
        data, name = service.experiment.case_result_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, "case_1", ResultFormat.CSV,
        )
        assert data == '1;2;3'
        assert name == 'Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.csv'

    def test_get_case_artifact(self, get_case_artifact):
        uri = URI(get_case_artifact.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case_artifact.context
        )
        data, name = service.experiment.case_artifact_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY, "case_1", "ABCD"
        )
        assert data == b'\x00\x00\x00\x00'
        assert name == 'Modelica.Blocks.Examples.PID_Controller_2020-10-22_06-03.mat'

    def test_case_get_trajectories(self, get_case_trajectories):
        uri = URI(get_case_trajectories.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_case_trajectories.context
        )
        data = service.experiment.case_trajectories_get(
            IDs.WORKSPACE_PRIMARY,
            IDs.EXPERIMENT_PRIMARY,
            "case_1",
            ["variable1", "variable2"],
        )
        assert data == [[1.0, 2.0, 7.0], [2.0, 3.0, 5.0]]

