"""Service access layer exceptions."""


class ServiceAccessError(Exception):
    pass


class CommunicationError(ServiceAccessError):
    pass


class SSLError(ServiceAccessError):
    pass


class InvalidContentTypeError(ServiceAccessError):
    pass


class UnauthorizedError(ServiceAccessError):
    pass


class HTTPError(ServiceAccessError):
    def __init__(self, message: str, status_code: int):
        self.status_code = status_code
        super().__init__(message)


class ErrorBodyIsNotJSONError(ServiceAccessError):
    pass


class ErrorJSONInvalidFormatError(ServiceAccessError):
    pass


class NoResponseFetchVersionError(ServiceAccessError):
    pass
