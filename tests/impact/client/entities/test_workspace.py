import os
import tempfile
import unittest.mock as mock

from tests.impact.client.helpers import (
    create_model_entity,
    create_model_exe_entity,
    create_workspace_entity,
    create_experiment_operation,
    create_project_entity,
    IDs,
)


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
        service = mock.MagicMock()
        workspace = create_workspace_entity(IDs.WORKSPACE_PRIMARY, service=service)
        workspace.delete()
        service.workspace.workspace_delete.assert_called_with(IDs.WORKSPACE_PRIMARY)

    def test_upload_result(self, workspace_sal_upload_base):
        workspace_service = workspace_sal_upload_base.workspace
        workspace = create_workspace_entity(
            IDs.WORKSPACE_PRIMARY, service=workspace_sal_upload_base
        )
        upload_op = workspace.upload_result("test.mat", "Workspace")
        workspace_service.result_upload.assert_called_with(
            IDs.WORKSPACE_PRIMARY, 'test.mat', description=None, label='Workspace'
        )
        assert upload_op.id == "2f036b9fab6f45c788cc466da327cc78workspace"

    def test_download_workspace(self, workspace):
        t = os.path.join(tempfile.gettempdir(), workspace.entity.id + '.zip')
        resp = workspace.entity.download({}, tempfile.gettempdir())
        assert resp == t

    # TODO: Cloning workspace is not implemented on feature branch
    # def test_clone(self, workspace):
    #     clone = workspace.entity.clone()
    #     assert clone == create_workspace_entity('MyClonedWorkspace')

    # TODO: Cloning workspace is not implemented on feature branch
    # def test_get_custom_function_from_clone(self, workspace):
    #     clone = workspace.entity.clone()
    #     custom_function = clone.get_custom_function('dynamic')
    #     assert 'dynamic' == custom_function.name

    def test_get_model(self, workspace):
        model = workspace.entity.get_model("Modelica.Blocks.PID")
        assert model == create_model_entity(
            "Modelica.Blocks.PID", workspace.entity.id, IDs.PROJECT_PRIMARY,
        )

    def test_model_repr(self, workspace):
        model = create_model_entity(
            "Modelica.Blocks.PID", workspace.entity.id, IDs.PROJECT_PRIMARY,
        )
        assert "Class name 'Modelica.Blocks.PID'" == model.__repr__()

    def test_get_fmus(self, workspace):
        fmus = workspace.entity.get_fmus()
        assert len(fmus) == 2
        assert fmus[0].id == IDs.FMU_PRIMARY
        assert fmus[1].id == IDs.FMU_SECONDARY

    def test_get_fmu(self, workspace):
        fmu = workspace.entity.get_fmu(IDs.FMU_PRIMARY)
        assert fmu == create_model_exe_entity(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)

    def test_get_experiment(self, workspace):
        exp = workspace.entity.get_experiment(IDs.EXPERIMENT_PRIMARY)
        assert exp.id == IDs.EXPERIMENT_PRIMARY

    def test_get_experiments(self, workspace):
        exps = workspace.entity.get_experiments()
        assert len(exps) == 2
        assert exps[0].id == IDs.EXPERIMENT_PRIMARY
        assert exps[1].id == IDs.EXPERIMENT_SECONDARY

    def test_create_experiment(self, workspace):
        exp = workspace.entity.create_experiment({})
        assert exp.id == IDs.EXPERIMENT_PRIMARY

    def test_create_experiment_with_user_data(self, workspace):
        workspace_entity = workspace.entity
        service = workspace.service
        workspace_service = service.workspace
        user_data = {"customWsGetKey": "customWsGetValue"}
        workspace_entity.create_experiment({}, user_data)

        workspace_service.experiment_create.assert_has_calls(
            [mock.call(IDs.WORKSPACE_PRIMARY, {}, user_data)]
        )

    def test_execute_options_dict(self, workspace):
        exp = workspace.entity.execute({})
        assert exp == create_experiment_operation(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )

    def test_get_default_project(self, workspace):
        project = workspace.entity.get_default_project()
        assert project.id == IDs.PROJECT_PRIMARY

    def test_get_projects(self, workspace):
        projects = workspace.entity.get_projects()
        assert projects == [
            create_project_entity(
                project_id=IDs.PROJECT_PRIMARY, project_name="NewProject",
            )
        ]

    def test_get_all_dependencies(self, workspace):
        dependencies = workspace.entity.get_dependencies()
        assert len(dependencies) == 2
        assert dependencies[0].id == IDs.MSL_300_PROJECT_ID
        assert dependencies[1].id == IDs.MSL_400_PROJECT_ID

    def test_create_project(self, workspace):
        project = workspace.entity.create_project("my_project")
        assert project.id == IDs.PROJECT_PRIMARY
