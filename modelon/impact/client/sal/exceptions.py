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
    pass


class ErrorBodyIsNotJSONError(ServiceAccessError):
    pass


class ErrorJSONInvalidFormatError(ServiceAccessError):
    pass


class NoResponseFetchVersionError(ServiceAccessError):
    pass
