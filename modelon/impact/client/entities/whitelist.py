from typing import List

from modelon.impact.client.sal.whitelist import WhitelistService


class Whitelist:
    def __init__(self, service: WhitelistService):
        self._sal = service

    def remove_user(self, username: str) -> None:
        """Remove a user from whitelisted users.

        Args:
            username: Username of the user to remove from whitelist.

        Example::

            whitelist = client.get_whitelist()
            whitelist.remove_user("naruto")

        """
        self._sal.whitelist_remove_user(username)

    def remove_group(self, group_name: str) -> None:
        """Remove a group from whitelisted groups.

        Args:
            group_name: Group name to remove from whitelist.

        Example::

            whitelist = client.get_whitelist()
            whitelist.remove_group("impact-tenant-konoha")

        """
        self._sal.whitelist_remove_group(group_name)

    def add_user(self, user_name: str) -> None:
        """Add a user to whitelisted users.

        Args:
            username: Username of the user to add to whitelisted users.

        Example::

            whitelist = client.get_whitelist()
            whitelist.add_user("naruto")

        """
        self._sal.whitelist_append(users=[user_name], groups=[])

    def add_group(self, group_name: str) -> None:
        """Add a group to whitelisted groups.

        Args:
            group_name: Group name to add to whitelisted groups.

        Example::

            whitelist = client.get_whitelist()
            whitelist.add_group("impact-tenant-konoha")

        """
        self._sal.whitelist_append(users=[], groups=[group_name])

    @property
    def users(self) -> List[str]:
        """List of whitelisted users."""
        data = self._sal.whitelist_get()
        return data["users"]

    @property
    def groups(self) -> List[str]:
        """List of whitelisted groups."""
        data = self._sal.whitelist_get()
        return data["groups"]
