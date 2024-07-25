from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from modelon.impact.client import exceptions
from modelon.impact.client.operations.base import AsyncOperationStatus
from modelon.impact.client.sal.service import Service

logger = logging.getLogger(__name__)


class OrphanPublishedWorkspaceOperation:
    """An operation class for the published workspace orphan cleanup."""

    def __init__(self, location: str, service: Service, operation_name: str):
        self._location = location
        self._sal = service
        self._name = operation_name

    def __repr__(self) -> str:
        return f"Orphan operations with id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return (
            isinstance(obj, OrphanPublishedWorkspaceOperation)
            and obj._location == self._location
        )

    @property
    def id(self) -> str:
        """Orphan operation id."""
        return self._location.split("/")[-1]

    @property
    def name(self) -> str:
        """Return the name of operation."""
        return self._name

    def _info(self) -> Dict[str, Any]:
        return self._sal.imports.get_import_status(self._location)["data"]

    def data(self) -> List[str]:
        """Returns a list of orphaned published workspace IDs.

        Returns:
            A a list of orphaned published workspace IDs.

        """
        info = self._info()
        if info["status"] == AsyncOperationStatus.ERROR.value:
            raise exceptions.FailedOrphanCleanup(
                f"Orphan cleanup failed! Cause: {info['error'].get('message')}"
            )
        return info["data"]["orphans"]

    @property
    def status(self) -> AsyncOperationStatus:
        """Returns the operation status as an enumeration.

        Returns:
            The AsyncOperationStatus enum. The status can have the enum values
            AsyncOperationStatus.READY, AsyncOperationStatus.RUNNING or
            AsyncOperationStatus.ERROR

        Example::

            pw_client = client.get_published_workspaces_client()
            status = pw_client.wipe_orphans().status

        """
        return AsyncOperationStatus(self._info()["status"])

    def wait(self, timeout: Optional[float] = None) -> List[str]:
        """Waits until the operation completes. Returns the operation class instance if
        operation completes.

        Args:
            timeout: Time to wait in seconds for achieving the status. By default
                the timeout is set to 'None', which signifies an infinite time
                to wait until the status is achieved.

        Raises:
            OperationTimeOutError if time exceeds set timeout.

        Example::

            pw_client = client.get_published_workspaces_client()
            status = pw_client.wipe_orphans().wait()

        """
        start_t = time.time()
        while True:
            logger.info(f"{self.name} in progress! Status : {self.status.name}")
            if self.status.done():
                logger.info(f"{self.name} completed! Status : {self.status.name}")
                return self.data()

            current_t = time.time()
            if timeout and current_t - start_t > timeout:
                raise exceptions.OperationTimeOutError(
                    f"Time exceeded the set timeout - {timeout}s! "
                    f"Present status of operation is {self.status.name}!"
                )

            time.sleep(0.5)
