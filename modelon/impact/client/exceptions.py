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
    def for_operation(cls, operation_name: str):
        return cls(
            f"{operation_name} was cancelled before completion! "
            f"Log file generated for cancelled {operation_name} is empty!"
        )


class OperationNotCompleteError(Error):
    @classmethod
    def for_operation(cls, operation_name: str, status):
        return cls(
            f"{operation_name} is still in progress! Status : {status}."
            f" Please call the wait() method on the {operation_name} operation"
            " to wait until completion!"
        )


class OperationCompleteError(Error):
    pass


class IllegalWorkspaceImport(Error):
    pass
