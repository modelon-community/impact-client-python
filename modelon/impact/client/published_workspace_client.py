from __future__ import annotations

import enum
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from modelon.impact.client.configuration import Experimental
from modelon.impact.client.entities.workspace import (
    PublishedWorkspace,
    PublishedWorkspaceDefinition,
    PublishedWorkspaceType,
)

if TYPE_CHECKING:
    from modelon.impact.client.sal.service import Service

logger = logging.getLogger(__name__)


@enum.unique
class PublishedWorkspaceAccessKind(enum.Enum):
    SHARED_BY_ME = "sharedByMe"
    SHARED_WITH_ME = "sharedWithMe"
    REQUESTED_BY_ME = "requestedByMe"
    REQUESTED_FROM_ME = "requestedFromMe"


@dataclass
class PublishedWorkspaceAccess:
    sharing_id: str
    requested_id: str
    requested_username: str
    published_workspace: Optional[PublishedWorkspace] = None


class PublishedWorkspacesClient:
    def __init__(self, service: Service):
        self._sal = service

    def find(
        self,
        *,
        name: str = "",
        first: int = 0,
        maximum: int = 20,
        has_data: bool = True,
        owner_username: str = "",
        type: Optional[PublishedWorkspaceType] = None,
        group_name: Optional[str] = None,
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
            group_name: Group name to query published workspaces for. Only
                a user with impact-sys-admin role can query published workspaces
                shared with a group other than his own.

        Returns:
            A list of published workspace class objects.

        Example::

            pw_client = client.get_published_workspaces_client()
            pw_client.find()

        """
        data = self._sal.workspace.get_published_workspaces(
            name,
            first,
            maximum,
            has_data,
            owner_username,
            type.value if type else None,
            group_name,
        )["data"]["items"]
        return [
            PublishedWorkspace(
                item["id"],
                definition=PublishedWorkspaceDefinition.from_dict(item),
                service=self._sal,
            )
            for item in data
        ]

    def get_by_id(
        self, sharing_id: str, request_if_no_access: bool = False
    ) -> Optional[PublishedWorkspace]:
        """Returns the published workspace class object with the given ID.

        Args:
            sharing_id: ID of the published workspace.
            request_if_no_access: Request access if user doesn't have access.

        Returns:
            The published workspace class object.

        Example::

            pw_client = client.get_published_workspaces_client()
            pw_client.get("2h98hciwsniucwincj")

        """
        if request_if_no_access:
            self._sal.workspace.request_user_access(sharing_id)
            logger.info(
                "Access request sent for published workspaces with ID '%s'.", sharing_id
            )
            return None
        data = self._sal.workspace.get_published_workspace(sharing_id)
        definition = PublishedWorkspaceDefinition.from_dict(data)
        return PublishedWorkspace(data["id"], definition=definition, service=self._sal)

    @Experimental
    def get_by_access_kind(
        self,
        access_kind: PublishedWorkspaceAccessKind = PublishedWorkspaceAccessKind.SHARED_BY_ME,  # noqa
        first: int = 0,
        maximum: int = 20,
    ) -> List[PublishedWorkspaceAccess]:
        """Returns a list of PublishedWorkspaceAccess class objects. The snapshots could
        be filtered based on the key-worded arguments.

        Args:
            access_kind: Access kind for the published workspace.
            first: Index of first matching published workspace to return.
            maximum: Maximum number of published workspaces to return.

        Returns:
            A list of PublishedWorkspaceAccess class objects.

        Example::

            from modelon.impact.client.published_workspace_client import
                PublishedWorkspaceAccessKind

            pw_client = client.get_published_workspaces_client()
            pw_client.get_by_access_kind(PublishedWorkspaceAccessKind.REQUESTED_BY_ME)

        """
        data = self._sal.workspace.get_published_workspaces_by_kind(
            access_kind.value, first, maximum
        )["data"]["items"]
        return [
            PublishedWorkspaceAccess(
                item["sharingId"],
                item["requesterId"],
                item["requesterUsername"],
                PublishedWorkspace(
                    item["publishedWorkspace"]["id"],
                    definition=PublishedWorkspaceDefinition.from_dict(
                        item["publishedWorkspace"]
                    ),
                    service=self._sal,
                )
                if "publishedWorkspace" in item
                else None,
            )
            for item in data
        ]
