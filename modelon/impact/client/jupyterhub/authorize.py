import logging

from modelon.impact.client.credential_manager import CredentialManager
from modelon.impact.client.jupyterhub import exceptions
from modelon.impact.client.jupyterhub import sal


logger = logging.getLogger(__name__)


def _get_jupyter_token(credential_manager, interactive, context=None):
    jupyter_token = credential_manager.get_key(interactive=interactive)
    if not jupyter_token:
        raise exceptions.NoJupyterHubTokenError("No JupyterHub API token is given")

    return jupyter_token


def authorize(uri, interactive, context=None, credential_manager=None, service=None):
    credential_manager = credential_manager or CredentialManager(
        file_id="jupyterhub-api.key",
        env_name="MODELON_IMPACT_JUPYTERHUB_CLIENT_API_TOKEN",
        interactive_help_text="Enter JupyterHub API token:",
    )
    context = sal.JupyterContext(base=context)
    service = service or sal.JupyterHubService()

    try:
        context.token = _get_jupyter_token(credential_manager, interactive)
        user = service.get_user_data(uri, context)
    except exceptions.JupyterHubAuthrizationError:
        if interactive:
            logger.warning(
                "Could not authorize with the provided JupyterHub API token, "
                "please enter a new token"
            )
            context.token = credential_manager.get_key_from_prompt()
            user = service.get_user_data(uri, context)
        else:
            raise

    if interactive:
        credential_manager.write_key_to_file(context.token)

    if not user.server_running():
        uri_to_start_server = uri / 'hub/home'
        raise exceptions.NoJupyterHubServerRunningError(
            "The user does not have a server running. "
            f"Go to {uri_to_start_server} and start a server."
        )

    return user.impact_server_uri(uri), context
