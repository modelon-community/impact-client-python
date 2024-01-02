import modelon.impact.client.sal.service
from modelon.impact.client.sal.uri import URI
from tests.files.paths import TEST_WORKSPACE_PATH
from tests.impact.client.helpers import (
    VERSIONED_PROJECT_BRANCH,
    VERSIONED_PROJECT_TRUNK,
    IDs,
    get_test_published_workspace_definition,
    get_test_workspace_definition,
)


class TestWorkspaceService:
    def test_create_workspace(self, create_workspace):
        uri = URI(create_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_workspace.context
        )
        data = service.workspace.workspace_create(IDs.WORKSPACE_PRIMARY)
        assert data == {
            'definition': get_test_workspace_definition(),
            'id': IDs.WORKSPACE_PRIMARY,
        }

    def test_rename_workspace(self, update_workspace):
        uri = URI(update_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=update_workspace.context
        )
        workspace_update_data = {
            'definition': get_test_workspace_definition(IDs.WORKSPACE_SECONDARY),
            'id': IDs.WORKSPACE_PRIMARY,
        }
        data = service.workspace.update_workspace(
            IDs.WORKSPACE_PRIMARY,
            {
                'definition': get_test_workspace_definition(IDs.WORKSPACE_SECONDARY),
                'id': IDs.WORKSPACE_PRIMARY,
            },
        )
        assert update_workspace.adapter.called
        rename_call = update_workspace.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}'
            == rename_call.url
        )
        assert 'PUT' == rename_call.method
        assert data == workspace_update_data

    def test_delete_workspace(self, delete_workspace):
        uri = URI(delete_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_workspace.context
        )
        service.workspace.workspace_delete(IDs.WORKSPACE_PRIMARY)
        assert delete_workspace.adapter.called
        delete_call = delete_workspace.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}'
            == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_get_workspace(self, single_workspace):
        uri = URI(single_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_workspace.context
        )
        data = service.workspace.workspace_get(IDs.WORKSPACE_PRIMARY, False)
        assert data == {
            "definition": get_test_workspace_definition(),
            "id": IDs.WORKSPACE_PRIMARY,
        }

    def test_get_workspace_with_size(self, single_workspace_with_size):
        uri = URI(single_workspace_with_size.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=single_workspace_with_size.context
        )
        data = service.workspace.workspace_get(IDs.WORKSPACE_PRIMARY, True)
        assert data == {
            "definition": get_test_workspace_definition(),
            "id": IDs.WORKSPACE_PRIMARY,
            "sizeInfo": {"total": 7014},
        }

    def test_get_workspaces(self, multiple_workspace):
        uri = URI(multiple_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_workspace.context
        )
        data = service.workspace.workspaces_get()
        workspace_1_def = get_test_workspace_definition(IDs.WORKSPACE_PRIMARY)
        workspace_2_def = get_test_workspace_definition(IDs.WORKSPACE_SECONDARY)
        assert data == {
            'data': {
                'items': [
                    {'id': IDs.WORKSPACE_PRIMARY, 'definition': workspace_1_def},
                    {'id': IDs.WORKSPACE_SECONDARY, 'definition': workspace_2_def},
                ]
            }
        }

    def test_workspace_export_setup(self, setup_export_workspace):
        uri = URI(setup_export_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=setup_export_workspace.context
        )
        data = service.workspace.workspace_export_setup(IDs.WORKSPACE_PRIMARY, False)
        request_data = setup_export_workspace.adapter.request_history[0].json()
        assert request_data == {'publish': False, 'workspaceId': IDs.WORKSPACE_PRIMARY}
        assert data == {"data": {"location": f"api/workspace-exports/{IDs.EXPORT}"}}

    def test_app_mode_workspace_export_setup(self, setup_export_workspace):
        uri = URI(setup_export_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=setup_export_workspace.context
        )
        data = service.workspace.workspace_export_setup(
            IDs.WORKSPACE_PRIMARY, False, IDs.MODELICA_CLASS_PATH
        )
        request_data = setup_export_workspace.adapter.request_history[0].json()
        assert request_data == {
            'publish': False,
            'workspaceId': IDs.WORKSPACE_PRIMARY,
            'appMode': {'model': IDs.MODELICA_CLASS_PATH},
        }
        assert data == {"data": {"location": f"api/workspace-exports/{IDs.EXPORT}"}}

    def test_workspace_export_status(self, get_export_workspace_status):
        uri = URI(get_export_workspace_status.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_export_workspace_status.context
        )
        data = service.exports.get_export_status(f"api/workspace-exports/{IDs.EXPORT}")
        assert data["data"]["status"] == "ready"

    def test_workspace_conversion_setup(self, setup_workspace_conversion):
        uri = URI(setup_workspace_conversion.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=setup_workspace_conversion.context
        )
        data = service.workspace.workspace_conversion_setup(
            IDs.WORKSPACE_PRIMARY, 'backup'
        )
        assert data == {
            "data": {"location": f"api/workspace-conversions/{IDs.CONVERSION}"}
        }

    def test_workspace_conversion_status(self, get_workspace_conversion_status):
        uri = URI(get_workspace_conversion_status.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_workspace_conversion_status.context
        )
        data = service.workspace.get_workspace_conversion_status(
            f"api/workspace-conversions/{IDs.CONVERSION}"
        )
        assert data["data"]["status"] == "ready"

    def test_get_fmu(self, get_fmu):
        uri = URI(get_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_fmu.context
        )
        data = service.workspace.fmu_get(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
        assert data == {'id': IDs.FMU_PRIMARY}

    def test_get_fmus(self, get_all_fmu):
        uri = URI(get_all_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_fmu.context
        )
        data = service.workspace.fmus_get(IDs.WORKSPACE_PRIMARY)
        assert data == {
            'data': {'items': [{'id': IDs.FMU_PRIMARY}, {'id': IDs.FMU_SECONDARY}]}
        }

    def test_fmu_download(self, download_fmu):
        uri = URI(download_fmu.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=download_fmu.context
        )
        data = service.workspace.fmu_download(IDs.WORKSPACE_PRIMARY, IDs.FMU_PRIMARY)
        assert data == b'\x00\x00\x00\x00'

    def test_get_experiment(self, get_experiment):
        uri = URI(get_experiment.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_experiment.context
        )
        data = service.workspace.experiment_get(
            IDs.WORKSPACE_PRIMARY, IDs.EXPERIMENT_PRIMARY
        )
        assert data == {'id': IDs.EXPERIMENT_PRIMARY}

    def test_get_experiments(self, get_all_experiments):
        uri = URI(get_all_experiments.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_experiments.context
        )
        data = service.workspace.experiments_get(IDs.WORKSPACE_PRIMARY)
        assert data == {
            'data': {
                'items': [
                    {'id': IDs.EXPERIMENT_PRIMARY},
                    {'id': IDs.EXPERIMENT_SECONDARY},
                ]
            }
        }
        assert get_all_experiments.adapter.called
        get_exps_call = get_all_experiments.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments'
            == get_exps_call.url
        )

    def test_get_experiments_for_class(self, get_all_experiments_for_class):
        uri = URI(get_all_experiments_for_class.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_all_experiments_for_class.context
        )
        data = service.workspace.experiments_get(
            IDs.WORKSPACE_PRIMARY, IDs.MODELICA_CLASS_PATH
        )
        assert data == {
            'data': {
                'items': [
                    {'id': IDs.EXPERIMENT_PRIMARY},
                    {'id': IDs.EXPERIMENT_SECONDARY},
                ]
            }
        }
        assert get_all_experiments_for_class.adapter.called
        get_exps_call = get_all_experiments_for_class.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/workspaces/{IDs.WORKSPACE_PRIMARY}/experiments'
            f'?classPath={IDs.MODELICA_CLASS_PATH}' == get_exps_call.url
        )

    def test_create_experiment(self, experiment_create):
        uri = URI(experiment_create.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=experiment_create.context
        )
        data = service.workspace.experiment_create(IDs.WORKSPACE_PRIMARY, {})
        assert experiment_create.adapter.called
        assert data == {"experiment_id": IDs.EXPERIMENT_PRIMARY}

        user_data = {"value": 42}
        data = service.workspace.experiment_create(IDs.WORKSPACE_PRIMARY, {}, user_data)
        request_data = experiment_create.adapter.request_history[1].json()
        assert request_data == {'userData': user_data}

    def test_get_projects(self, get_projects):
        uri = URI(get_projects.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_projects.context
        )
        data = service.workspace.projects_get(
            IDs.WORKSPACE_PRIMARY, include_disabled=False, vcs_info=False
        )
        assert data == {
            "data": {
                "items": [
                    {
                        "id": IDs.PROJECT_PRIMARY,
                        "definition": {},
                        "projectType": "LOCAL",
                    }
                ]
            }
        }

    def test_create_project(self, create_project):
        uri = URI(create_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=create_project.context
        )
        data = service.workspace.project_create(IDs.WORKSPACE_PRIMARY, "my_project")
        assert data == {
            "id": IDs.PROJECT_PRIMARY,
            "definition": {
                "name": "my_project",
                "format": "1.0",
                "dependencies": [],
                "content": [],
                "executionOptions": [],
            },
            "projectType": "LOCAL",
        }

    def test_get_dependencies(self, get_dependencies):
        uri = URI(get_dependencies.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_dependencies.context
        )
        data = service.workspace.dependencies_get(
            IDs.WORKSPACE_PRIMARY, vcs_info=False, include_disabled=False
        )
        assert data == {
            "data": {
                "items": [
                    {
                        "id": IDs.MSL_300_PROJECT_ID,
                        "definition": {},
                        "projectType": "SYSTEM",
                    },
                ]
            }
        }

    def test_get_shared_definition(self, shared_definition_get):
        uri = URI(shared_definition_get.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=shared_definition_get.context
        )
        data = service.workspace.shared_definition_get(IDs.WORKSPACE_PRIMARY, True)
        assert shared_definition_get.adapter.called
        git_url = "https://github.com/project/test"
        vcs_uri = f"git+{git_url}.git@main:da6abb188a089527df1b54b27ace84274b819e4a"
        assert data == {
            "definition": {
                "name": "test",
                "projects": [
                    {
                        "reference": {
                            "id": IDs.VERSIONED_PROJECT_REFERENCE,
                            "vcsUri": vcs_uri,
                        },
                        "disabled": True,
                        "disabledContent": [],
                    }
                ],
                "dependencies": [],
            }
        }

    def test_get_workspace_upload_status(self, get_workspace_upload_status):
        uri = URI(get_workspace_upload_status.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_workspace_upload_status.context
        )
        data = service.imports.get_import_status(f"api/workspace-imports/{IDs.IMPORT}")
        assert get_workspace_upload_status.adapter.called
        assert data == {
            "data": {
                'id': IDs.IMPORT,
                'status': 'ready',
                'data': {
                    'resourceUri': f'api/workspaces/{IDs.WORKSPACE_PRIMARY}',
                    'workspaceId': IDs.WORKSPACE_PRIMARY,
                },
            }
        }

    def test_workspace_import_from_zip(self, import_workspace):
        uri = URI(import_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_workspace.context
        )
        data = service.workspace.import_from_zip(TEST_WORKSPACE_PATH)
        assert data == {"data": {"location": f"api/workspace-imports/{IDs.IMPORT}"}}

    def test_import_from_shared_definition(self, import_workspace):
        uri = URI(import_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_workspace.context
        )
        data = service.workspace.import_from_shared_definition(
            {"definition": {"name": "test", "projects": []}}
        )
        assert data == {"data": {"location": f"api/workspace-imports/{IDs.IMPORT}"}}

    def test_get_vcs_matchings(self, get_project_matchings):
        uri = URI(get_project_matchings.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=get_project_matchings.context
        )
        data = service.workspace.get_project_matchings(
            {"definition": {"name": "test", "projects": []}}
        )
        assert data == {
            "data": {
                "vcs": [
                    {
                        "entryId": IDs.VERSIONED_PROJECT_REFERENCE,
                        "uri": {
                            "serviceKind": "git",
                            "serviceUrl": "https://github.com",
                            "repoUrl": {
                                "url": "github.com/project/test.git",
                                "refname": "main",
                                "sha1": "da6abb188a089527df1b54b27ace84274b819e4a",
                            },
                            "protocol": "https",
                            "subdir": ".",
                        },
                        "projects": [VERSIONED_PROJECT_TRUNK, VERSIONED_PROJECT_BRANCH],
                    },
                ]
            }
        }

    def test_project_import_from_zip(self, import_workspace_project):
        uri = URI(import_workspace_project.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_workspace_project.context
        )
        data = service.workspace.import_project_from_zip(
            IDs.WORKSPACE_PRIMARY, TEST_WORKSPACE_PATH
        )
        assert data == {
            "data": {
                "location": f"api/workspaces/{IDs.WORKSPACE_PRIMARY}/project-imports/{IDs.IMPORT}"
            }
        }

    def test_dependency_import_from_zip(self, import_workspace_dependency):
        uri = URI(import_workspace_dependency.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=import_workspace_dependency.context
        )
        data = service.workspace.import_dependency_from_zip(
            IDs.WORKSPACE_PRIMARY, TEST_WORKSPACE_PATH
        )
        assert data == {
            "data": {
                "location": f"api/workspaces/{IDs.WORKSPACE_PRIMARY}/dependency-imports/{IDs.IMPORT}"
            }
        }

    def test_get_published_workspace(self, published_workspace):
        uri = URI(published_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=published_workspace.context
        )
        data = service.workspace.get_published_workspace(IDs.PUBLISHED_WORKSPACE_ID)
        definition = get_test_published_workspace_definition()
        assert data == {"id": IDs.PUBLISHED_WORKSPACE_ID, **definition}

    def test_get_published_workspaces_with_filter(self, multiple_published_workspaces):
        uri = URI(multiple_published_workspaces.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=multiple_published_workspaces.context
        )
        data = service.workspace.get_published_workspaces(
            name="new_name",
            first=0,
            maximum=10,
            has_data=True,
            owner_username="alice",
            type="APP_MODE",
        )['data']['items']
        assert len(data) == 1
        definition = get_test_published_workspace_definition()
        assert data[0] == {"id": IDs.PUBLISHED_WORKSPACE_ID, **definition}
        assert multiple_published_workspaces.adapter.called
        get_published_workspaces_call = (
            multiple_published_workspaces.adapter.request_history[0]
        )
        assert (
            'http://mock-impact.com/api/published-workspaces?workspaceName=new_name'
            '&hasData=True&max=10&ownerUsername=alice&type=APP_MODE'
            == get_published_workspaces_call.url
        )

    def test_get_published_workspaces_with_kind_shared_by_me(
        self, published_workspace_shared_by_me
    ):
        uri = URI(published_workspace_shared_by_me.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=published_workspace_shared_by_me.context
        )
        data = service.workspace.get_published_workspaces_by_kind(
            kind="sharedByMe",
            first=0,
            maximum=10,
        )['data']['items']
        assert len(data) == 1
        definition = get_test_published_workspace_definition()
        assert data[0] == {
            "sharingId": IDs.PUBLISHED_WORKSPACE_ID,
            "requesterId": IDs.USER_ID,
            "requesterUsername": IDs.USERNAME,
            "publishedWorkspace": {"id": IDs.PUBLISHED_WORKSPACE_ID, **definition},
        }
        assert published_workspace_shared_by_me.adapter.called
        get_published_workspaces_call = (
            published_workspace_shared_by_me.adapter.request_history[0]
        )
        assert (
            'http://mock-impact.com/api/published-workspaces/access/users?kind='
            'sharedByMe&max=10' == get_published_workspaces_call.url
        )

    def test_delete_published_workspace(self, delete_published_workspace):
        uri = URI(delete_published_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=delete_published_workspace.context
        )
        service.workspace.delete_published_workspace(IDs.PUBLISHED_WORKSPACE_ID)
        assert delete_published_workspace.adapter.called
        delete_call = delete_published_workspace.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/published-workspaces/{IDs.PUBLISHED_WORKSPACE_ID}'
            == delete_call.url
        )
        assert 'DELETE' == delete_call.method

    def test_rename_published_workspace(self, rename_published_workspace):
        uri = URI(rename_published_workspace.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=rename_published_workspace.context
        )
        service.workspace.rename_published_workspace(
            IDs.PUBLISHED_WORKSPACE_ID, IDs.WORKSPACE_SECONDARY
        )
        assert rename_published_workspace.adapter.called
        rename_call = rename_published_workspace.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/published-workspaces/{IDs.PUBLISHED_WORKSPACE_ID}'
            == rename_call.url
        )
        assert 'PATCH' == rename_call.method

    def test_request_published_workspace_access(
        self, request_published_workspace_access
    ):
        uri = URI(request_published_workspace_access.url)
        service = modelon.impact.client.sal.service.Service(
            uri=uri, context=request_published_workspace_access.context
        )
        service.workspace.request_published_workspace_access(IDs.PUBLISHED_WORKSPACE_ID)
        assert request_published_workspace_access.adapter.called
        access_call = request_published_workspace_access.adapter.request_history[0]
        assert (
            f'http://mock-impact.com/api/published-workspaces/{IDs.PUBLISHED_WORKSPACE_ID}/access/users'
            == access_call.url
        )
        assert 'PATCH' == access_call.method
