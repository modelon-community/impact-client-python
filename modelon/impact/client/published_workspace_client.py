from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional

from modelon.impact.client.entities.workspace import (
    PublishedWorkspace,
    PublishedWorkspaceDefinition,
    PublishedWorkspaceType,
)

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service

logger = logging.getLogger(__name__)


class PublishedWorkspacesClient:
    def __init__(self, service: Service):
        self._sal = service

    def find(
        self,
        *,
        name: str = "",
        first: int = 0,
        maximum: int = 20,
        has_data: bool = False,
        owner_username: str = "",
        type: Optional[PublishedWorkspaceType] = None,
    ) -> List[PublishedWorkspace]:
        """Returns a list of published workspaces. The snapshots could be filtered based
        on the key-worded arguments.

        Args:
            name: Name of the workspace.
            first: Index of first matching resource to return.
            maximum: Maximum number of resources to return.
            has_data: If true, filters with
            status==PublishedWorkspaceUploadStatus.CREATED. If false
            returns everything.
            owner_username: If true, only workspaces published by the specified
            user are listed.
            type: Filter so only published workspace of a specified type are
                returned. If not given all published workspace types are
                returned.

        Returns:
            A list of published workspace class objects.

        Example::

            pw_client = client.get_published_workspaces_client()
            pw_client.find()

        """
        data = self._sal.workspace.get_published_workspaces(
            name, first, maximum, has_data, owner_username, type.value if type else None
        )["data"]["items"]
        return [
            PublishedWorkspace(
                item['id'],
                definition=PublishedWorkspaceDefinition.from_dict(item),
                service=self._sal,
            )
            for item in data
        ]

    def get(self, sharing_id: str) -> PublishedWorkspace:
        """Returns the published workspace class object with the given ID.

        Args:
            sharing_id: ID of the published workspace.

        Returns:
            The published workspace class object.

        Example::

            pw_client = client.get_published_workspaces_client()
            pw_client.get("2h98hciwsniucwincj")

        """
        data = self._sal.workspace.get_published_workspace(sharing_id)
        definition = PublishedWorkspaceDefinition.from_dict(data)
        return PublishedWorkspace(data['id'], definition=definition, service=self._sal)
