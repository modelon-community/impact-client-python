import unittest.mock as mock

import pytest

from modelon.impact.client.entities.workspace import PublishedWorkspaceUploadStatus
from modelon.impact.client.published_workspace_client import (
    PublishedWorkspaceAccessKind,
    PublishedWorkspacesClient,
)
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
    assert workspaces[0].definition.tenant_id == IDs.TENANT_ID
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
    assert workspace.definition.tenant_id == IDs.TENANT_ID
    assert workspace.definition.size == 10
    assert workspace.definition.status == PublishedWorkspaceUploadStatus.CREATED


@pytest.mark.experimental
def test_get_publised_workspace_by_kind_shared_by_me(published_workspace_shared_by_me):
    uri = URI(published_workspace_shared_by_me.url)
    service = Service(uri=uri, context=published_workspace_shared_by_me.context)
    client = PublishedWorkspacesClient(service)
    workspaces = client.get_by_access_kind(PublishedWorkspaceAccessKind.SHARED_BY_ME)
    assert len(workspaces) == 1
    workspace = workspaces[0]
    assert workspace.sharing_id == IDs.PUBLISHED_WORKSPACE_ID
    assert workspace.requested_id == IDs.USER_ID
    assert workspace.requested_username == IDs.USERNAME
    assert workspace.published_workspace
    assert workspace.published_workspace.id == IDs.PUBLISHED_WORKSPACE_ID
    assert workspace.published_workspace.name == IDs.WORKSPACE_PRIMARY
    assert workspace.published_workspace.definition.owner_username == IDs.USERNAME
    assert workspace.published_workspace.definition.tenant_id == IDs.TENANT_ID
    assert workspace.published_workspace.definition.size == 10
    assert (
        workspace.published_workspace.definition.status
        == PublishedWorkspaceUploadStatus.CREATED
    )


def test_request_published_workspace_access():
    service = mock.MagicMock()
    client = PublishedWorkspacesClient(service)
    client.get_by_id(IDs.PUBLISHED_WORKSPACE_ID, request_if_no_access=True)
    service.workspace.request_published_workspace_access.assert_called_with(
        IDs.PUBLISHED_WORKSPACE_ID
    )
