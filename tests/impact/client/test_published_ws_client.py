import unittest.mock as mock

import pytest

from modelon.impact.client.entities.workspace import PublishedWorkspaceUploadStatus
from modelon.impact.client.published_workspace_client import PublishedWorkspacesClient
from modelon.impact.client.sal.service import Service
from modelon.impact.client.sal.uri import URI
from tests.impact.client.helpers import IDs


@pytest.mark.experimental
def test_get_publised_workspaces(multiple_published_workspaces):
    uri = URI(multiple_published_workspaces.url)
    service = Service(uri=uri, context=multiple_published_workspaces.context)
    client = PublishedWorkspacesClient(service)
    workspaces = client.find()
    assert workspaces
    assert len(workspaces) == 1
    assert workspaces[0].id == IDs.PUBLISHED_WORKSPACE_ID
    assert workspaces[0].name == IDs.WORKSPACE_PRIMARY
    assert workspaces[0].definition.owner_username == IDs.USERNAME
    assert workspaces[0].definition.tenant == IDs.TENANT
    assert workspaces[0].definition.size == 10
    assert workspaces[0].definition.status == PublishedWorkspaceUploadStatus.CREATED


@pytest.mark.experimental
def test_get_publised_workspace(published_workspace):
    uri = URI(published_workspace.url)
    service = Service(uri=uri, context=published_workspace.context)
    client = PublishedWorkspacesClient(service)
    workspace = client.get_by_id(IDs.PUBLISHED_WORKSPACE_ID)
    assert workspace
    assert workspace.id == IDs.PUBLISHED_WORKSPACE_ID
    assert workspace.name == IDs.WORKSPACE_PRIMARY
    assert workspace.definition.owner_username == IDs.USERNAME
    assert workspace.definition.tenant == IDs.TENANT
    assert workspace.definition.size == 10
    assert workspace.definition.status == PublishedWorkspaceUploadStatus.CREATED


def test_request_published_workspace_access():
    service = mock.MagicMock()
    client = PublishedWorkspacesClient(service)
    client.get_by_id(IDs.PUBLISHED_WORKSPACE_ID, request_if_no_access=True)
    service.workspace.request_published_workspace_access.assert_called_with(
        IDs.PUBLISHED_WORKSPACE_ID
    )
