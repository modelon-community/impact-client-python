from __future__ import annotations

from typing import Any, Optional


class Error(Exception):
    pass


class UnsupportedSemanticVersionError(Error):
    pass


class NoAssignedLicenseError(Error):
    pass


class OperationTimeOutError(Error):
    def __init__(
        self,
        current_status_name: str,
        expected_status_names: Optional[list[str]] = None,
        timeout: Optional[float] = None,
    ) -> None:
        timeout_msg = f"Time exceeded the set timeout - {timeout}s. " if timeout else ""
        status_msg = f"Present status of operation is {current_status_name}. "
        expected_status_names_msg = (
            f"Expected statuses: {', '.join(expected_status_names)}."
            if expected_status_names
            else ""
        )
        super().__init__(timeout_msg + status_msg + expected_status_names_msg)


class OperationFailureError(Error):
    @classmethod
    def for_operation(cls, operation_name: str) -> OperationFailureError:
        return cls(
            f"{operation_name} was cancelled before completion! "
            f"Log file generated for cancelled {operation_name} is empty!"
        )


class OperationNotCompleteError(Error):
    @classmethod
    def for_operation(
        cls, operation_name: str, status: Any
    ) -> OperationNotCompleteError:
        return cls(
            f"{operation_name} is still in progress! Status : {status}."
            f" Please call the wait() method on the {operation_name} operation"
            " to wait until completion!"
        )


class OperationCompleteError(Error):
    pass


class FailedOrphanCleanup(Error):
    pass


class IllegalProjectImport(Error):
    pass


class IllegalWorkspaceImport(Error):
    pass


class IllegalWorkspaceExport(Error):
    pass


class IllegalWorkspaceConversion(Error):
    pass


class IllegalContentImport(Error):
    pass


class IllegalCustomArtifactImport(Error):
    pass


class IllegalCaseResultImport(Error):
    pass


class IllegalFMUImport(Error):
    pass


class ExternalResultUploadError(Error):
    pass


class NoSuchCustomArtifactError(Error):
    pass


class NoAssociatedPublishedWorkspaceError(Error):
    pass


class RemotePublishedWorkspaceLinkError(Error):
    pass


class AuthenticationError(Error):
    pass
