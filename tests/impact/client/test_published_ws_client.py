import unittest.mock as mock

import pytest

from modelon.impact.client.entities.workspace import PublishedWorkspaceUploadStatus
from modelon.impact.client.published_workspace_client import (
    PublishedWorkspaceAccessKind,
    PublishedWorkspacesClient,
)
from modelon.impact.client.sal.service import Service
from modelon.impact.client.sal.uri import URI
from tests.impact.client.helpers import ClientHelper, IDs


class TestPublishedWorkspace:
    def _publish_workspace(self, client_helper: ClientHelper):
        pub_ws_id = client_helper.workspace.export(publish=True).wait().id
        pwc = client_helper.client.get_published_workspaces_client()
        pw = pwc.get_by_id(pub_ws_id)
        assert pw
        return pw, pwc

    @pytest.mark.vcr()
    def test_get_publised_workspaces(self, client_helper: ClientHelper):
        pw, pwc = self._publish_workspace(client_helper)
        workspaces = pwc.find(
            name=IDs.WORKSPACE_ID_PRIMARY, owner_username=pw.definition.owner_username
        )
        assert workspaces
        assert len(workspaces) == 1
        assert workspaces[0].id == pw.id
        assert workspaces[0].name == IDs.WORKSPACE_ID_PRIMARY
        assert workspaces[0].definition.owner_username == pw.definition.owner_username
        assert workspaces[0].definition.tenant_id == IDs.TENANT_ID
        assert isinstance(workspaces[0].definition.size, int)
        assert workspaces[0].definition.status == PublishedWorkspaceUploadStatus.CREATED

        # Cleanup
        pw.delete()

    @pytest.mark.vcr()
    def test_get_publised_workspace(self, client_helper: ClientHelper):
        pw, _ = self._publish_workspace(client_helper)

        assert pw
        assert pw.id
        assert pw.name == IDs.WORKSPACE_ID_PRIMARY
        assert pw.definition.owner_username
        assert pw.definition.tenant_id
        assert isinstance(pw.definition.size, int)
        assert pw.definition.status == PublishedWorkspaceUploadStatus.CREATED

        # Cleanup
        pw.delete()

    @pytest.mark.experimental
    def test_get_publised_workspace_by_kind_shared_by_me(
        self, published_workspace_shared_by_me
    ):
        uri = URI(published_workspace_shared_by_me.url)
        service = Service(uri=uri, context=published_workspace_shared_by_me.context)
        client = PublishedWorkspacesClient(service)
        workspaces = client.get_by_access_kind(
            PublishedWorkspaceAccessKind.SHARED_BY_ME
        )
        assert len(workspaces) == 1
        workspace = workspaces[0]
        assert workspace.sharing_id == IDs.PUBLISHED_WORKSPACE_ID
        assert workspace.requested_id == IDs.USER_ID
        assert workspace.requested_username == IDs.USERNAME
        assert workspace.published_workspace
        assert workspace.published_workspace.id == IDs.PUBLISHED_WORKSPACE_ID
        assert workspace.published_workspace.name == IDs.WORKSPACE_ID_PRIMARY
        assert workspace.published_workspace.definition.owner_username == IDs.USERNAME
        assert workspace.published_workspace.definition.tenant_id == IDs.TENANT_ID
        assert workspace.published_workspace.definition.size == 10
        assert (
            workspace.published_workspace.definition.status
            == PublishedWorkspaceUploadStatus.CREATED
        )

    def test_request_published_workspace_access(self):
        service = mock.MagicMock()
        client = PublishedWorkspacesClient(service)
        client.get_by_id(IDs.PUBLISHED_WORKSPACE_ID, request_if_no_access=True)
        service.workspace.request_user_access.assert_called_with(
            IDs.PUBLISHED_WORKSPACE_ID
        )
