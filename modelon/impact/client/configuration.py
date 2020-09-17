import logging


logger = logging.getLogger(__name__)


def get_client_url():
    """ Returns the default URL the client will use if unspecified """
    url = "http://localhost:8080/"
    logger.warning("No URL for client was specified, will use: {}".format(url))
    return url


def get_client_interactive():
    """ Returns the default for if client will run interactive or not if unspecified """
    return False
