import logging
import os
from typing import Optional, Tuple
from modelon.impact.client.credential_manager import CredentialManager
from modelon.impact.client.jupyterhub import exceptions
from modelon.impact.client.jupyterhub import sal
from modelon.impact.client.sal.context import Context
from modelon.impact.client.sal.uri import URI

logger = logging.getLogger(__name__)


def _get_jupyter_token(credential_manager: CredentialManager, interactive: bool) -> str:
    jupyter_token = credential_manager.get_key(interactive=interactive)
    if not jupyter_token:
        raise exceptions.NoJupyterHubTokenError("No JupyterHub API token is given")

    return jupyter_token


def _running_in_jupyterhub_environment() -> bool:
    return os.environ.get("JUPYTERHUB_SERVICE_PREFIX") is not None


def authorize(
    uri: URI,
    interactive: bool,
    context: Optional[Context] = None,
    credential_manager: Optional[CredentialManager] = None,
    service: Optional[sal.JupyterHubService] = None,
) -> Tuple[URI, sal.JupyterContext]:

    jupyter_context = sal.JupyterContext(base=context)
    service = service or sal.JupyterHubService()

    if _running_in_jupyterhub_environment():
        jupyter_context.token = os.environ.get('JUPYTERHUB_API_TOKEN', '')
        server = os.environ.get('JUPYTERHUB_SERVICE_PREFIX')
        user = service.get_user_data(uri, jupyter_context, server)
        return user.impact_server_uri(uri), jupyter_context

    help_text = f"Enter JupyterHub API token (can be generated at {uri / 'token'}):"
    credential_manager = credential_manager or CredentialManager(
        file_id="jupyterhub-api.key",
        env_names=[
            "JUPYTERHUB_API_TOKEN",
            "MODELON_IMPACT_JUPYTERHUB_CLIENT_API_TOKEN",
        ],
        interactive_help_text=help_text,
    )

    try:
        jupyter_context.token = _get_jupyter_token(credential_manager, interactive)
        user = service.get_user_data(uri, jupyter_context)
    except exceptions.JupyterHubAuthrizationError:
        if interactive:
            logger.warning(
                "Could not authorize with the provided JupyterHub API token, "
                "please enter a new token"
            )
            jupyter_context.token = credential_manager.get_key_from_prompt()
            user = service.get_user_data(uri, jupyter_context)
        else:
            raise

    jupyter_token = jupyter_context.token
    if interactive and jupyter_token:
        credential_manager.write_key_to_file(jupyter_token)

    if not user.server_running():
        uri_to_start_server = uri / 'hub/home'
        raise exceptions.NoJupyterHubServerRunningError(
            "The user does not have a server running. "
            f"Go to {uri_to_start_server} and start a server."
        )

    return user.impact_server_uri(uri), jupyter_context
