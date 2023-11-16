import logging
import os
from typing import Any, Callable

logger = logging.getLogger(__name__)


def get_client_url() -> str:
    """Returns the default URL the client will use if unspecified.

    Can be overridden by the environment variable MODELON_IMPACT_CLIENT_URL.

    """
    url = os.environ.get("MODELON_IMPACT_CLIENT_URL")
    if url is None:
        url = "https://impact.modelon.cloud/"
        logger.warning("No URL for client was specified, will use: {}".format(url))
    return url


def get_client_interactive() -> bool:
    """Returns the default for if client will run interactive or not if unspecified.

    Can be overridden by the environment variable MODELON_IMPACT_CLIENT_INTERACTIVE.

    """
    interactive_env = os.environ.get("MODELON_IMPACT_CLIENT_INTERACTIVE", "false")
    return interactive_env.lower() in ("1", "true")


def get_client_experimental() -> bool:
    """Returns the default for if experimental client methods should be enabled or not.

    Can be overridden by the environment variable IMPACT_PYTHON_CLIENT_EXPERIMENTAL.

    """
    experimental_env = os.environ.get("IMPACT_PYTHON_CLIENT_EXPERIMENTAL", "false")
    return experimental_env.lower() in ("1", "true")


class Experimental:
    def __init__(self, fn: Callable):
        self.fn = fn

    def __set_name__(self, owner: str, name: str) -> None:
        if get_client_experimental():
            setattr(owner, name, self.fn)
        else:
            delattr(owner, name)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.fn(*args, **kwargs)
