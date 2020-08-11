class Error(Exception):
    pass


class UnsupportedSemanticVersionError(Error):
    pass


class OperationTimeOutError(Error):
    pass


class OperationFailureError(Error):
    pass


class OperationNotCompleteError(Error):
    pass


class EmptyLogError(Error):
    pass
