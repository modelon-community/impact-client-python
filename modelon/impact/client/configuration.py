import os
import logging


logger = logging.getLogger(__name__)


def get_client_url() -> str:
    """Returns the default URL the client will use if unspecified.

    Can be overridden by the environment variable
    MODELON_IMPACT_CLIENT_URL.

    """
    url = os.environ.get("MODELON_IMPACT_CLIENT_URL")
    if url is None:
        url = "https://impact.modelon.cloud/"
        logger.warning("No URL for client was specified, will use: {}".format(url))
    return url


def get_client_interactive() -> bool:
    """Returns the default for if client will run interactive or not if
    unspecified.

    Can be overridden by the environment variable
    MODELON_IMPACT_CLIENT_INTERACTIVE.

    """
    interactive_env = os.environ.get("MODELON_IMPACT_CLIENT_INTERACTIVE", "false")
    return interactive_env.lower() in ("1", "true")
