class Error(Exception):
    pass


class JupyterHubAuthrizationError(Error):
    pass


class NotAJupyterHubUrl(Error):
    pass


class NoJupyterHubServerRunningError(Error):
    pass


class UnknownJupyterHubError(Error):
    pass


class NoJupyterHubTokenError(Error):
    pass
