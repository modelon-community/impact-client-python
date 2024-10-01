import os
import tempfile
import unittest.mock as mock

import pytest

import modelon.impact.client.sal.exceptions as sal_exceptions
from modelon.impact.client import (
    AccessSettings,
    Choices,
    SimpleFMUExperimentDefinition,
    SimpleModelicaExperimentDefinition,
)
from modelon.impact.client.entities.experiment import Experiment
from modelon.impact.client.entities.external_result import ExternalResult
from modelon.impact.client.entities.model import Model
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.exceptions import (
    NoAssociatedPublishedWorkspaceError,
    RemotePublishedWorkspaceLinkError,
)
from modelon.impact.client.experiment_definition.expansion import LatinHypercube, Sobol
from modelon.impact.client.experiment_definition.extension import (
    SimpleExperimentExtension,
)
from modelon.impact.client.experiment_definition.modifiers import Enumeration
from modelon.impact.client.experiment_definition.operators import Uniform
from modelon.impact.client.operations.workspace.exports import WorkspaceExportOperation
from tests.files.paths import get_archived_project_path
from tests.impact.client.helpers import (
    ClientHelper,
    IDs,
    create_published_workspace_entity,
    create_workspace_entity,
)


class TestPublishedWorkspace:
    def test_delete_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_ID_PRIMARY, service=service
        )
        workspace.delete()
        service.workspace.delete_published_workspace.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    @pytest.mark.experimental
    def test_revoke_user_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_ID_PRIMARY, service=service
        )
        workspace.revoke_user_access(IDs.USERNAME)
        service.workspace.revoke_user_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.USERNAME
        )

    @pytest.mark.experimental
    def test_grant_user_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_ID_PRIMARY, service=service
        )
        workspace.grant_user_access(IDs.USERNAME)
        service.workspace.grant_user_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.USERNAME
        )

    @pytest.mark.experimental
    def test_grant_community_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_ID_PRIMARY, service=service
        )
        workspace.grant_community_access()
        service.workspace.grant_community_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    @pytest.mark.experimental
    def test_revoke_community_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_ID_PRIMARY, service=service
        )
        workspace.revoke_community_access()
        service.workspace.revoke_community_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    @pytest.mark.experimental
    def test_grant_group_acess_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_ID_PRIMARY, service=service
        )
        workspace.grant_group_access()
        service.workspace.grant_group_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, None
        )
        workspace.grant_group_access(IDs.GROUP_NAME)
        service.workspace.grant_group_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.GROUP_NAME
        )

    @pytest.mark.experimental
    def test_revoke_group_access_for_published_workspace(self):
        service = mock.MagicMock()
        workspace = create_published_workspace_entity(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_ID_PRIMARY, service=service
        )
        workspace.revoke_group_access(IDs.GROUP_NAME)
        service.workspace.revoke_group_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.GROUP_NAME
        )

    @pytest.mark.experimental
    def test_get_modelica_resource_uri(self):
        service = mock.MagicMock()
        workspace = create_workspace_entity(IDs.WORKSPACE_ID_PRIMARY, service=service)
        uri = workspace.get_modelica_resource_uri(
            library="Modelica", resource_path=IDs.MODELICA_RESOURCE_PATH
        )
        assert str(uri) == IDs.MODELICA_RESOURCE_URI

    def test_rename_published_workspace(self, publish_workspace):
        workspace = publish_workspace.entity
        service = publish_workspace.service

        new_workspace_name = IDs.WORKSPACE_ID_SECONDARY
        assert workspace.name == IDs.WORKSPACE_ID_PRIMARY
        workspace.name = new_workspace_name

        service.workspace.rename_published_workspace.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID, new_workspace_name
        )
        service.workspace.get_published_workspace.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )

    def test_import_published_workspace(self, publish_workspace):
        workspace = publish_workspace.entity.import_to_userspace()
        assert workspace.id == IDs.WORKSPACE_ID_PRIMARY

    @pytest.mark.experimental
    def test_get_published_workspace_acl(self, publish_workspace):
        pub_ws_acl = publish_workspace.entity.get_access_control_list()
        assert len(pub_ws_acl.shared_with) == 1
        assert pub_ws_acl.shared_with[0].username == IDs.USERNAME
        assert pub_ws_acl.shared_with[0].id == IDs.USER_ID
        assert pub_ws_acl.requested_by == []
        assert pub_ws_acl.role_names == []
        assert len(pub_ws_acl.group_names) == 1
        assert pub_ws_acl.group_names[0] == IDs.GROUP_NAME


class TestWorkspace:
    @pytest.mark.vcr()
    def test_get_workspace_size(self, client_helper: ClientHelper):
        assert client_helper.workspace.id == IDs.WORKSPACE_ID_PRIMARY
        assert isinstance(client_helper.workspace.size, int)

    @pytest.mark.vcr()
    def test_rename_workspace(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        assert workspace.name == IDs.WORKSPACE_ID_PRIMARY
        workspace.rename(IDs.WORKSPACE_ID_SECONDARY)
        workspace = client_helper.client.get_workspace(IDs.WORKSPACE_ID_PRIMARY)
        assert workspace.name == IDs.WORKSPACE_ID_SECONDARY

    @pytest.mark.vcr()
    def test_get_custom_function(self, client_helper: ClientHelper):
        custom_function = client_helper.workspace.get_custom_function(IDs.DYNAMIC_CF)
        assert IDs.DYNAMIC_CF == custom_function.name

    @pytest.mark.vcr()
    def test_get_custom_functions(self, client_helper: ClientHelper):
        custom_function_list = [
            custom_function.name
            for custom_function in client_helper.workspace.get_custom_functions()
        ]
        assert IDs.DYNAMIC_CF in custom_function_list

    @pytest.mark.vcr()
    def test_delete(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        workspace.delete()
        with pytest.raises(sal_exceptions.HTTPError) as err:
            client_helper.client.get_workspace(workspace.id)
        assert str(err.value) == f"The workspace '{workspace.id}' does not exist"

    @pytest.mark.vcr()
    def test_upload_result(self, tmpdir, client_helper: ClientHelper):
        exp = client_helper.create_and_execute_experiment(modifiers={})
        assert isinstance(exp, Experiment)
        case = exp.get_case(IDs.CASE_ID_PRIMARY)
        result, file_name = case.get_result()
        result_path = os.path.join(tmpdir, file_name)
        with open(result_path, "wb") as f:
            f.write(result)

        external_result_label = "Cruise result"
        external_result_description = "An external_result"
        external_result = client_helper.workspace.upload_result(
            result_path, external_result_label, external_result_description
        ).wait()
        assert isinstance(external_result, ExternalResult)
        assert external_result.id
        assert external_result.metadata.description == external_result_description
        assert external_result.metadata.name == external_result_label

        external_result.delete()

    @pytest.mark.vcr()
    def test_download_workspace(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        temp_dir = tempfile.gettempdir()
        resp = workspace.download(temp_dir)
        download_path = os.path.join(temp_dir, workspace.id + ".zip")
        assert resp == download_path

    @pytest.mark.vcr()
    def test_export_workspace(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        ops = workspace.export()
        assert isinstance(ops, WorkspaceExportOperation)
        temp_dir = tempfile.gettempdir()
        download_path = os.path.join(temp_dir, workspace.id + ".zip")
        path = ops.wait().download_as(download_path)
        assert path == download_path

    def test_publish_workspace_without_group_share(self, workspace):
        workspace_entity = workspace.entity
        service = workspace.service
        workspace_service = service.workspace
        workspace_entity.export(
            publish=True, access=AccessSettings(share_with_own_tenant=False)
        )
        access_settings = {"shareWithOwnTenant": False}
        workspace_service.workspace_export_setup.assert_has_calls(
            [mock.call(IDs.WORKSPACE_ID_PRIMARY, True, None, access_settings)]
        )

    @pytest.mark.vcr()
    def test_publish_workspace(self, client_helper: ClientHelper):
        pwc = client_helper.client.get_published_workspaces_client()
        pub_ws_id = client_helper.workspace.export(publish=True).wait().id
        pw = pwc.get_by_id(pub_ws_id)
        assert pw
        assert pw.name == client_helper.workspace.name
        pw.delete()

    @pytest.mark.vcr()
    def test_get_remote_workspace_corresponding_to_workspace(
        self, client_helper: ClientHelper
    ):
        pw = client_helper.workspace.export(publish=True).wait()
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pw.id)
        assert pw
        workspace = pw.import_to_userspace()
        pub_ws = workspace.received_from.get_workspace()
        assert pub_ws
        pw.delete()

    @pytest.mark.vcr()
    def test_get_remote_workspace_fails_if_remote_deleted(
        self, client_helper: ClientHelper
    ):
        pw = client_helper.workspace.export(publish=True).wait()
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pw.id)
        assert pw
        workspace = pw.import_to_userspace()

        pub_ws = workspace.received_from.get_workspace()
        assert pub_ws

        # Delete published workspace, local workspace still has a link to it
        pw.delete()

        pub_ws = workspace.received_from.get_workspace()
        assert pub_ws is None

    @pytest.mark.vcr()
    def test_get_remote_workspace_fails_for_local_workspace(
        self, client_helper: ClientHelper
    ):
        with pytest.raises(NoAssociatedPublishedWorkspaceError):
            client_helper.workspace.received_from.get_workspace()

    @pytest.mark.vcr()
    def test_has_remote_update_fails_for_local_workspace(
        self, client_helper: ClientHelper
    ):
        with pytest.raises(NoAssociatedPublishedWorkspaceError):
            client_helper.workspace.received_from.has_updates()

    @pytest.mark.vcr()
    def test_has_remote_update_returns_None_if_no_published_workspace_found(
        self, client_helper: ClientHelper
    ):
        pw = client_helper.workspace.export(publish=True).wait()
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pw.id)
        assert pw
        workspace = pw.import_to_userspace()

        has_remote_updates = workspace.received_from.has_updates()
        assert has_remote_updates is False

        # Delete published workspace, local workspace still has a link to it
        pw.delete()

        has_remote_updates = workspace.received_from.has_updates()
        assert has_remote_updates is None

    @pytest.mark.vcr()
    def test_workspace_has_remote_updates(self, client_helper: ClientHelper):
        pw = client_helper.workspace.export(publish=True).wait()
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pw.id)
        assert pw
        workspace = pw.import_to_userspace()
        assert not workspace.received_from.has_updates()

        # Republish workspace
        client_helper.workspace.export(publish=True).wait()

        assert workspace.received_from.has_updates()
        pw.delete()

    @pytest.mark.vcr()
    def test_update_from_remote(self, client_helper: ClientHelper):
        pw = client_helper.workspace.export(publish=True).wait()
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pw.id)
        assert pw
        workspace = pw.import_to_userspace()
        assert not workspace.received_from.has_updates()

        # Republish workspace
        client_helper.workspace.export(publish=True).wait()
        assert workspace.received_from.has_updates()

        # Update from remote
        workspace = workspace.received_from.update_userspace()

        assert not workspace.received_from.has_updates()

        pw.delete()

    @pytest.mark.vcr()
    def test_get_published_workspace_corresponding_to_workspace(
        self, client_helper: ClientHelper
    ):
        pub_ws = client_helper.workspace.get_published_workspace()
        assert not pub_ws
        pw_id = client_helper.workspace.export(publish=True).wait().id

        pub_ws = client_helper.workspace.get_published_workspace()
        assert pub_ws
        assert pub_ws.id == pw_id

        # Cleanup
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pw_id)
        assert pw
        pw.delete()

    @pytest.mark.vcr()
    def test_get_published_app_mode_workspace_corresponding_to_workspace(
        self, client_helper: ClientHelper
    ):
        # Assert workspace not linked to any archieve or app mode published workspaces
        pub_ws = client_helper.workspace.get_published_workspace()
        assert not pub_ws

        pub_ws = client_helper.workspace.get_published_workspace(
            model_name=IDs.PID_MODELICA_CLASS_PATH
        )
        assert not pub_ws

        pub_ws = client_helper.workspace.get_published_workspace(
            model_name=IDs.FILTER_MODELICA_CLASS_PATH
        )
        assert not pub_ws

        # Publish app mode workspace with PID controller
        pw_id_pid = (
            client_helper.workspace.export(
                publish=True, class_path=IDs.PID_MODELICA_CLASS_PATH
            )
            .wait()
            .id
        )
        # Publish app mode workspace with Filter
        pw_id_filter = (
            client_helper.workspace.export(
                publish=True, class_path=IDs.FILTER_MODELICA_CLASS_PATH
            )
            .wait()
            .id
        )

        # Fetch linked PID app mode workspace
        pub_ws_pid = client_helper.workspace.get_published_workspace(
            model_name=IDs.PID_MODELICA_CLASS_PATH
        )
        assert pub_ws_pid
        assert pub_ws_pid.id == pw_id_pid
        assert pub_ws_pid.definition.app_mode
        assert pub_ws_pid.definition.app_mode.model == IDs.PID_MODELICA_CLASS_PATH

        # Fetch linked Filter app mode workspace
        pub_ws_filter = client_helper.workspace.get_published_workspace(
            model_name=IDs.FILTER_MODELICA_CLASS_PATH
        )
        assert pub_ws_filter
        assert pub_ws_filter.id == pw_id_filter
        assert pub_ws_filter.definition.app_mode
        assert pub_ws_filter.definition.app_mode.model == IDs.FILTER_MODELICA_CLASS_PATH

        # Fetch linked archive workspace
        pub_ws = client_helper.workspace.get_published_workspace()
        assert not pub_ws

        # Cleanup
        pwc = client_helper.client.get_published_workspaces_client()
        for id in [pw_id_pid, pw_id_filter]:
            pw = pwc.get_by_id(id)
            assert pw
            pw.delete()

    @pytest.mark.vcr()
    def test_get_published_workspace_fails_for_remote_imported_workspace(
        self, client_helper: ClientHelper
    ):
        pw_id = client_helper.workspace.export(publish=True).wait().id
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pw_id)
        assert pw
        workspace = pw.import_to_userspace()

        with pytest.raises(RemotePublishedWorkspaceLinkError):
            workspace.get_published_workspace()

        # Cleanup
        pw.delete()

    @pytest.mark.vcr()
    def test_get_model(self, client_helper: ClientHelper):
        model_name = IDs.PID_MODELICA_CLASS_PATH
        model = client_helper.workspace.get_model(model_name)
        assert isinstance(model, Model)
        assert model.name == model_name

    @pytest.mark.vcr()
    def test_model_repr(self, client_helper: ClientHelper):
        model_name = IDs.PID_MODELICA_CLASS_PATH
        model = client_helper.workspace.get_model(model_name)
        assert f"Class name '{model_name}'" == model.__repr__()

    @pytest.mark.vcr()
    def test_get_fmus(self, client_helper: ClientHelper):
        client_helper.create_and_execute_experiment()
        fmus = client_helper.workspace.get_fmus()
        assert len(fmus) == 2

    @pytest.mark.vcr()
    def test_get_fmu(self, client_helper: ClientHelper):
        client_helper.create_and_execute_experiment(modifiers={})
        fmus = client_helper.workspace.get_fmus()
        assert len(fmus) == 1
        fmu = client_helper.workspace.get_fmu(fmus[0].id)
        assert isinstance(fmu, ModelExecutable)

    @pytest.mark.vcr()
    def test_get_experiment(self, client_helper: ClientHelper):
        exp = client_helper.create_experiment(modifiers={})
        exp = client_helper.workspace.get_experiment(exp.id)
        assert isinstance(exp, Experiment)

    @pytest.mark.vcr()
    def test_get_experiments(self, client_helper: ClientHelper):
        client_helper.create_experiment(modifiers={})
        client_helper.create_experiment(modifiers={})
        exps = client_helper.workspace.get_experiments()
        assert len(exps) == 2

    @pytest.mark.vcr()
    def test_create_experiment(self, client_helper: ClientHelper):
        exp = client_helper.create_experiment(modifiers={})
        assert isinstance(exp, Experiment)
        assert exp.id

    @pytest.mark.vcr()
    def test_create_experiment_with_user_data(self, client_helper: ClientHelper):
        expected_user_data = {"customWsGetKey": "customWsGetValue"}
        exp = client_helper.create_experiment(user_data=expected_user_data)
        user_data = exp.metadata.user_data
        assert user_data == expected_user_data

    @pytest.mark.vcr()
    def test_experiment_def_as_dict(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        dynamic = workspace.get_custom_function("dynamic")
        model = workspace.get_model(IDs.PID_MODELICA_CLASS_PATH)
        experiment_definition = SimpleModelicaExperimentDefinition(
            model, dynamic
        ).to_dict()
        exp = workspace.execute(experiment_definition).wait()
        assert isinstance(exp, Experiment)

    @pytest.mark.vcr()
    def test_get_default_project(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        project = workspace.get_default_project()
        assert project.name == IDs.DEFAULT_PROJECT_NAME

    @pytest.mark.vcr()
    def test_get_projects(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        workspace.create_project(IDs.PROJECT_NAME_PRIMARY)
        projects = workspace.get_projects()
        assert len(projects) == 2

    @pytest.mark.vcr()
    def test_get_all_dependencies(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        dependencies = workspace.get_dependencies()
        assert len(dependencies) == 1
        assert dependencies[0].name == "Modelica"

    @pytest.mark.vcr()
    def test_create_project(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        project = workspace.create_project(IDs.PROJECT_NAME_PRIMARY)
        assert project.name == IDs.PROJECT_NAME_PRIMARY

    @pytest.mark.vcr()
    def test_import_dependency_from_zip(self, tmpdir, client_helper: ClientHelper):
        archieve_prj_path = get_archived_project_path(tmpdir)
        imported_dependency = client_helper.workspace.import_dependency_from_zip(
            archieve_prj_path
        ).wait()
        assert imported_dependency.name == IDs.PROJECT_NAME_PRIMARY
        ws_prjs = client_helper.workspace.get_dependencies()
        assert len(ws_prjs) == 2
        assert ws_prjs[1].name == IDs.PROJECT_NAME_PRIMARY

    @pytest.mark.vcr()
    def test_import_project_from_zip(self, tmpdir, client_helper: ClientHelper):
        archieve_prj_path = get_archived_project_path(tmpdir)
        imported_project = client_helper.workspace.import_project_from_zip(
            archieve_prj_path
        ).wait()
        assert imported_project.name == IDs.PROJECT_NAME_PRIMARY
        ws_prjs = client_helper.workspace.get_projects()
        assert len(ws_prjs) == 2
        assert ws_prjs[1].name == IDs.PROJECT_NAME_PRIMARY

    @pytest.mark.vcr()
    def test_get_model_experiments(self, client_helper: ClientHelper):
        workspace = client_helper.workspace
        client_helper.create_experiment()
        experiments = workspace.get_experiments(IDs.PID_MODELICA_CLASS_PATH)
        assert len(experiments) == 1

    @pytest.mark.vcr()
    def test_create_class_based_experiment_definition_from_experiment_result(
        self, client_helper: ClientHelper
    ):
        workspace = client_helper.workspace
        dynamic = workspace.get_custom_function("dynamic").with_parameters(
            start_time=0.0, final_time=2.5
        )
        model = workspace.get_model(IDs.PID_MODELICA_CLASS_PATH)
        base_experiment_definition = SimpleModelicaExperimentDefinition(model, dynamic)
        _exp_for_init = workspace.create_experiment(base_experiment_definition)
        exp_for_init = _exp_for_init.execute().wait()
        case_for_init = exp_for_init.get_case("case_1")

        # Setup extensions
        simulation_options = dynamic.get_simulation_options().with_values(ncp=500)
        solver_options = {"atol": 1e-8}
        # Extension initialized from case
        simulate_ext_1 = (
            SimpleExperimentExtension()
            .with_case_label("Cruise condition 1")
            .with_initialize_from(case_for_init)
        )
        # Extension initialized from experiment
        simulate_ext_2 = (
            SimpleExperimentExtension(
                {"start_time": 0.0, "final_time": 4.0},
                solver_options,
                simulation_options,
            )
            .with_case_label("Cruise condition 2")
            .with_initialize_from(exp_for_init)
        )
        extensions = [simulate_ext_1, simulate_ext_2]

        # Initializing with experiment and expanding with Sobol
        experiment_definition = (
            base_experiment_definition.with_modifiers(
                {
                    "PI.k": Uniform(100.0, 200.0),
                    "PI.Ti": 0.2,
                    "PI.homotopyType": Enumeration(
                        "Modelica.Blocks.Types.LimiterHomotopy.NoHomotopy"
                    ),
                }
            )
            .with_expansion(Sobol(5))
            .with_extensions(extensions)
            .with_cases([{"inertia1.J": 3}])
            .with_initialize_from(exp_for_init)
        )
        experiment = workspace.create_experiment(experiment_definition)
        definition = workspace.get_experiment(experiment.id).get_definition()
        definition_dict = definition.to_dict()
        expected_definition_dict = experiment_definition.to_dict()
        assert definition_dict == expected_definition_dict
        assert isinstance(definition, SimpleModelicaExperimentDefinition)
        assert len(definition.modifiers) == 3 and all(
            mod in definition.modifiers for mod in ("PI.k", "PI.Ti", "PI.homotopyType")
        )
        assert definition.model.name == IDs.PID_MODELICA_CLASS_PATH
        assert definition.fmi_target == "me"
        assert definition.fmi_version == "2.0"
        assert definition.platform == "auto"
        assert definition.compiler_log_level == "warning"
        assert definition.simulation_log_level == "WARNING"
        assert definition.simulation_options == {
            "dynamic_diagnostics": False,
            "ncp": 500,
        }
        assert definition.solver_options == {}
        assert definition.runtime_options == {}
        assert definition.compiler_options == {
            "c_compiler": "gcc",
            "generate_html_diagnostics": False,
            "include_protected_variables": False,
        }
        assert definition.custom_function.name == "dynamic"
        assert definition.expansion == Sobol(samples=5)
        expected_extensions = extensions + [
            SimpleExperimentExtension().with_modifiers({"inertia1.J": 3})
        ]
        expected_extensions_as_list_dict = [
            extension.to_dict() for extension in expected_extensions
        ]
        assert [
            extension.to_dict() for extension in definition.extensions
        ] == expected_extensions_as_list_dict

        # Initializing with case and expanding with Latinhypercube
        experiment_definition = (
            base_experiment_definition.with_modifiers({"PI.k": Uniform(100.0, 200.0)})
            .with_expansion(LatinHypercube(5, 2))
            .with_extensions([simulate_ext_1, simulate_ext_2])
            .with_cases([{"inertia1.J": 3}])
            .with_initialize_from(case_for_init)
        )
        experiment = workspace.create_experiment(experiment_definition)
        definition_dict = (
            workspace.get_experiment(experiment.id).get_definition().to_dict()
        )
        expected_definition_dict = experiment_definition.to_dict()
        assert definition_dict == expected_definition_dict

    @pytest.mark.vcr()
    def test_create_fmu_based_experiment_definition_from_experiment_result(
        self, client_helper: ClientHelper
    ):
        workspace = client_helper.workspace
        dynamic = workspace.get_custom_function("dynamic").with_parameters(
            start_time=0.0, final_time=2.5
        )
        model = workspace.get_model(IDs.PID_MODELICA_CLASS_PATH)
        compiler_options = dynamic.get_compiler_options().with_values(c_compiler="gcc")
        fmu = model.compile(compiler_options).wait()
        base_experiment_definition = SimpleFMUExperimentDefinition(fmu, dynamic)
        _exp_for_init = workspace.create_experiment(base_experiment_definition)
        exp_for_init = _exp_for_init.execute().wait()
        case_for_init = exp_for_init.get_case("case_1")

        # Setup extensions
        simulation_options = dynamic.get_simulation_options().with_values(ncp=500)
        solver_options = {"atol": 1e-8}
        # Extension initialized from case
        simulate_ext_1 = (
            SimpleExperimentExtension()
            .with_case_label("Cruise condition 1")
            .with_initialize_from(case_for_init)
        )
        # Extension initialized from experiment
        simulate_ext_2 = (
            SimpleExperimentExtension(
                {"start_time": 0.0, "final_time": 4.0},
                solver_options,
                simulation_options,
            )
            .with_case_label("Cruise condition 2")
            .with_initialize_from(exp_for_init)
        )
        extensions = [simulate_ext_1, simulate_ext_2]

        # Initializing with experiment
        experiment_definition = (
            base_experiment_definition.with_modifiers({"PI.k": Uniform(100.0, 200.0)})
            .with_extensions(extensions)
            .with_cases([{"inertia1.J": 3}])
            .with_initialize_from(exp_for_init)
        )
        experiment = workspace.create_experiment(experiment_definition)

        definition_dict = (
            workspace.get_experiment(experiment.id).get_definition().to_dict()
        )
        expected_definition_dict = experiment_definition.to_dict()
        assert definition_dict == expected_definition_dict

        # Initializing with case
        experiment_definition = (
            base_experiment_definition.with_modifiers(
                {
                    "PI.k": Uniform(100.0, 200.0),
                    "PI.Ti": 0.2,
                    "PI.homotopyType": Enumeration(
                        "Modelica.Blocks.Types.LimiterHomotopy.NoHomotopy"
                    ),
                }
            )
            .with_extensions(extensions)
            .with_cases([{"inertia1.J": 3}])
            .with_initialize_from(case_for_init)
        )
        experiment = workspace.create_experiment(experiment_definition)
        definition = workspace.get_experiment(experiment.id).get_definition()
        definition_dict = definition.to_dict()
        expected_definition_dict = experiment_definition.to_dict()
        assert definition_dict == expected_definition_dict

        assert isinstance(definition, SimpleFMUExperimentDefinition)
        assert len(definition.modifiers) == 3 and all(
            mod in definition.modifiers for mod in ("PI.k", "PI.Ti", "PI.homotopyType")
        )
        assert definition.fmu.id
        assert definition.simulation_log_level == "WARNING"
        assert definition.simulation_options == {
            "dynamic_diagnostics": False,
            "ncp": 500,
        }
        assert definition.solver_options == {}
        assert definition.custom_function.name == "dynamic"
        expected_extensions = extensions + [
            SimpleExperimentExtension().with_modifiers({"inertia1.J": 3})
        ]
        expected_extensions_as_list_dict = [
            extension.to_dict() for extension in expected_extensions
        ]
        assert [
            extension.to_dict() for extension in definition.extensions
        ] == expected_extensions_as_list_dict

    @pytest.mark.vcr()
    def test_create_class_based_experiment_definition_from_case_result(
        self, client_helper: ClientHelper
    ):
        workspace = client_helper.workspace
        dynamic = workspace.get_custom_function("dynamic").with_parameters(
            start_time=0.0, final_time=2.5
        )
        model = workspace.get_model(IDs.PID_MODELICA_CLASS_PATH)
        base_experiment_definition = SimpleModelicaExperimentDefinition(model, dynamic)
        exp_for_init = workspace.execute(base_experiment_definition).wait()
        case_for_init = exp_for_init.get_case(IDs.CASE_ID_PRIMARY)

        experiment_definition = base_experiment_definition.with_modifiers(
            {
                "PI.yMax": Choices(100, 200),
                "PI.homotopyType": Enumeration(
                    "Modelica.Blocks.Types.LimiterHomotopy.NoHomotopy"
                ),
                "PI.Ti": 0.2,
            }
        ).with_initialize_from(case_for_init)
        experiment = workspace.execute(experiment_definition).wait()
        case = experiment.get_case(IDs.CASE_ID_PRIMARY)

        definition = (
            workspace.get_experiment(experiment.id).get_case(case.id).get_definition()
        )
        definition_dict = definition.to_dict()

        expected_definition_dict = experiment_definition.to_dict()
        variables = expected_definition_dict["experiment"]["base"]["modifiers"][
            "variables"
        ]
        index = next(
            (index for (index, var) in enumerate(variables) if var["name"] == "PI.yMax")
        )
        variables[index]["kind"] = "value"
        del variables[index]["values"]
        variables[index]["value"] = 100
        assert definition_dict == expected_definition_dict

    @pytest.mark.vcr()
    def test_get_experiment_definition_for_exp_with_choices_operator(
        self, client_helper: ClientHelper
    ):
        workspace = client_helper.workspace
        dynamic = workspace.get_custom_function("dynamic").with_parameters(
            start_time=0.0, final_time=2.5
        )
        model = workspace.get_model(IDs.PID_MODELICA_CLASS_PATH)
        base_experiment_definition = SimpleModelicaExperimentDefinition(model, dynamic)
        experiment_definition = base_experiment_definition.with_modifiers(
            {
                "PI.yMax": Choices(100, 200),
            }
        )
        experiment = workspace.execute(experiment_definition).wait()
        definition_dict = experiment.get_definition().to_dict()
        expected_definition_dict = experiment_definition.to_dict()
        assert definition_dict == expected_definition_dict
