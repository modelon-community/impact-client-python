import os
import requests
import uuid
import time
import logging


def get_workspace_id():
    workspace_id = uuid.uuid4().hex
    return workspace_id


def default_experiment(fmu_id, analysis_function):
    return {
        "analysis": {
            "analysis_function": analysis_function,
            "parameters": {"start_time": 0, "final_time": 1},
            "simulation_options": {},
            "solver_options": {},
            "simulation_log_level": "WARNING",
        },
        "fmu_id": fmu_id,
        "modifiers": {},
    }


def wait_for_status(status, get_status_resp, timeout=120):
    start_t = time.time()

    while True:
        time.sleep(0.5)

        status_resp = get_status_resp()
        assert 200 == status_resp.status_code
        execution_status = status_resp.json()["status"]

        logging.info("execution status {}".format(execution_status))
        if execution_status == status:
            return

        current_t = time.time()
        assert current_t - start_t < timeout, "waited for too long"


class Session:
    def __init__(self):
        self._session = requests.Session()
        self._base_url = os.environ["TEST_URL"]

    def _get_workspace_url(self, workspace_id):
        workspace_url = "{}/api/workspaces/{}".format(self._base_url, workspace_id)
        return workspace_url

    def setup_workspace(self, workspace_id):
        resp = self._session.post(
            "{}/api/workspaces".format(self._base_url),
            json={"new": {"name": workspace_id}},
        )
        assert 200 == resp.status_code

    def get_all_workspaces(self):
        resp = self._session.get("{}/api/workspaces".format(self._base_url))
        workspaces = resp.json()
        assert 200 == resp.status_code
        return workspaces

    def add_mo_file_to_workspace(self, workspace_id, MO_PATH):
        workspace_url = self._get_workspace_url(workspace_id)
        with open(MO_PATH, "rb") as mo_file:
            files = {"file": mo_file}
            resp = self._session.post("{}/libraries".format(workspace_url), files=files)
            assert 200 == resp.status_code

    def get_execution_options(self, workspace_id, custom_function):
        workspace_url = self._get_workspace_url(workspace_id)
        options = self._session.get(
            "{}/custom-functions/{}/options".format(workspace_url, custom_function),
        )
        assert 200 == options.status_code
        return options

    def set_execution_options(self, workspace_id, custom_function, execution_options):
        workspace_url = self._get_workspace_url(workspace_id)
        options = self._session.post(
            "{}/custom-functions/{}/options".format(workspace_url, custom_function),
            json=execution_options,
        )
        assert 200 == options.status_code

    def del_execution_options(self, workspace_id, custom_function, execution_options):
        workspace_url = self._get_workspace_url(workspace_id)
        options = self._session.delete(
            "{}/custom-functions/{}/options".format(workspace_url, custom_function),
            json=execution_options,
        )
        assert 200 == options.status_code

    def compile_fmu(self, workspace_id, compilation_input):
        workspace_url = self._get_workspace_url(workspace_id)
        resp = self._session.post(
            "{}/model-executables".format(workspace_url), json=compilation_input,
        )

        assert 200 == resp.status_code
        fmu_id = resp.json()["id"]

        # Compile the model
        compile_url = "{}/model-executables/{}/compilation".format(
            workspace_url, fmu_id
        )
        resp = self._session.post(compile_url)
        assert 200 == resp.status_code

        # Wait for compilation to finished
        wait_for_status("done", lambda: self._session.get(compile_url))

        # Get the compilation info
        resp = self._session.get(
            "{}/model-executables/{}".format(workspace_url, fmu_id)
        )
        assert 200 == resp.status_code
        assert resp.json()["run_info"]["status"] == "successful"

        return fmu_id

    def _get_execution_url(self, workspace_id, exp_id):
        workspace_url = self._get_workspace_url(workspace_id)
        execution_url = "{}/experiments/{}/execution".format(workspace_url, exp_id)
        return execution_url

    def setup_experiment(self, workspace_id, experiment):
        # Setup experiment
        workspace_url = self._get_workspace_url(workspace_id)
        request_body = {"experiment": experiment}
        resp = self._session.post(
            "{}/experiments".format(workspace_url), json=request_body
        )
        assert 200 == resp.status_code
        exp_id = resp.json()["experiment_id"]
        return exp_id

    def start_experiment(
        self, workspace_id, experiment, keep_model=False,
    ):
        exp_id = self.setup_experiment(workspace_id, experiment)
        execution_url = self._get_execution_url(workspace_id, exp_id)
        resp = self._session.post(execution_url, json={"keepModel": keep_model})
        assert 200 == resp.status_code

        return exp_id

    def get_experiment_execution_status(self, execution_url):
        execution_status = self._session.get(execution_url)
        assert 200 == execution_status.status_code

        return execution_status

    def run_experiment_until_finish(self, workspace_id, experiment, keep_model=False):
        exp_id = self.start_experiment(workspace_id, experiment, keep_model=keep_model)
        execution_url = self._get_execution_url(workspace_id, exp_id)

        # Wait for execution to finished, then return
        wait_for_status("done", lambda: self._session.get(execution_url))
        return exp_id

    def assert_successful_experiment(self, workspace_id, exp_id, number_of_cases=1):
        workspace_url = self._get_workspace_url(workspace_id)
        # Get experiment run-info and check number of successful cases
        resp = self._session.get("{}/experiments/{}".format(workspace_url, exp_id))
        assert 200 == resp.status_code
        assert resp.json()["run_info"]["successful"] == number_of_cases

    def get_all_variables_results(self, workspace_id, exp_id):
        # Get values of all varible from the experiment results
        workspace_url = self._get_workspace_url(workspace_id)
        resp = self._session.get(
            "{}/experiments/{}/variables".format(workspace_url, exp_id)
        )
        assert 200 == resp.status_code
        return resp.json()

    def assert_experiment_result_contains_variable(
        self, workspace_id, exp_id, var_name
    ):
        # Get all variables in the experiment result
        workspace_url = self._get_workspace_url(workspace_id)
        resp = self._session.get(
            "{}/experiments/{}/variables".format(workspace_url, exp_id)
        )
        assert 200 == resp.status_code
        assert var_name in resp.json()

    def assert_fmu_meta_data(self, fmu_meta, expected):
        meta = fmu_meta.json()
        assert meta == expected

    def get_fmu_meta(self, workspace_id, fmu_id):
        workspace_url = self._get_workspace_url(workspace_id)
        fmu_meta = self._session.get(
            "{}/model-executables/{}/steady-state-metadata".format(
                workspace_url, fmu_id
            )
        )
        assert 200 == fmu_meta.status_code
        return fmu_meta

    def set_variables(self, workspace_id, fmu_id, var_name, var_value):
        workspace_url = self._get_workspace_url(workspace_id)
        resp = self._session.put(
            "{}/compilation/{}/variable/{}".format(workspace_url, fmu_id, var_name),
            json={"value": var_value},
        )
        assert 200 == resp.status_code

    def clear_variables(self, workspace_id, fmu_id):
        workspace_url = self._get_workspace_url(workspace_id)
        resp = self._session.delete(
            "{}/compilation/{}/variable".format(workspace_url, fmu_id)
        )
        assert 200 == resp.status_code

    def cancel_simulation(self, workspace_id, exp_id):
        termination_url = self._get_execution_url(workspace_id, exp_id)
        resp = self._session.delete(termination_url)
        assert 200 == resp.status_code

    def get_simulation_status(self, workspace_id, exp_id):
        status_url = self._get_execution_url(workspace_id, exp_id)
        status = self._session.get(status_url)
        return status

    def get_experiment_info(self, workspace_id):
        workspace_url = self._get_workspace_url(workspace_id)
        # Get all experiments information
        exp_info = self._session.get("{}/experiments".format(workspace_url))
        assert 200 == exp_info.status_code
        return exp_info

    def get_experiment_results(self, workspace_id, exp_id, var_names):
        # Get values of the specific varible from the experiment results
        workspace_url = self._get_workspace_url(workspace_id)
        request_body = {"variable_names": var_names}
        resp = self._session.post(
            "{}/experiments/{}/trajectories".format(workspace_url, exp_id),
            json=request_body,
        )
        assert 200 == resp.status_code
        return resp.json()

    def get_settable_parameters(self, workspace_id, fmu_id):
        workspace_url = self._get_workspace_url(workspace_id)
        # Get parameters that can be set on FMU
        settable_params = self._session.get(
            "{}/model-executables/{}/settable-parameters".format(workspace_url, fmu_id)
        )
        assert 200 == settable_params.status_code
        return settable_params.json()

    def delete_workspace(self, workspace_id):
        return self._session.delete(self._get_workspace_url(workspace_id))
