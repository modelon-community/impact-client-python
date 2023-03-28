from __future__ import annotations
from typing import Any


class Error(Exception):
    pass


class UnsupportedSemanticVersionError(Error):
    pass


class NoAssignedLicenseError(Error):
    pass


class OperationTimeOutError(Error):
    pass


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


class ExternalResultUploadError(Error):
    pass


class NoSuchCustomArtifactError(Error):
    pass
