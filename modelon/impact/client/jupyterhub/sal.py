import json.decoder
from typing import Optional
import requests

from modelon.impact.client.jupyterhub import exceptions
from modelon.impact.client.sal.context import Context
from modelon.impact.client.sal.uri import URI


class JupyterContext:
    __slots__ = ['_base', '_token']

    def __init__(self, base: Optional[Context] = None):
        self._base = base if base else Context()
        self._token: Optional[str] = None

    @property
    def session(self) -> requests.Session:
        return self._base.session

    @property
    def token(self) -> Optional[str]:
        return self._token

    @token.setter
    def token(self, token: str) -> None:
        self._token = token
        self.session.headers.update({'Authorization': 'token %s' % token})


class JupyterUser:
    def __init__(self, user_id: str, server: Optional[str]):
        self.id = user_id
        self._server = server

    def server_running(self) -> bool:
        return self._server is not None

    def impact_server_uri(self, jupyterhub_uri: URI) -> URI:
        return jupyterhub_uri / f'user/{self.id}/impact'


class JupyterHubService:
    @classmethod
    def get_user_data(
        cls, uri: URI, context: JupyterContext, server: Optional[str] = None
    ) -> JupyterUser:
        auth_token_url = (
            uri / f'hub/api/authorizations/token/{context.token}'
        ).resolve()

        try:
            user_response = context.session.get(auth_token_url)
        except requests.exceptions.RequestException as e:
            raise exceptions.NotAJupyterHubUrl(
                f"Did not get a response from {uri}, is the URL correct?"
            ) from e

        if not user_response.ok:
            if user_response.status_code == 403:
                raise exceptions.JupyterHubAuthrizationError(
                    "Could not authorize against JupyterHub, is the token correct?"
                )
            elif user_response.status_code == 404:
                raise exceptions.NotAJupyterHubUrl(
                    f"Missing resource '{auth_token_url}'. Possible errors are "
                    f"that the URL '{uri}' don't points to a JupyterHub or "
                    "that the user of the API key as been deleted."
                )
            else:
                raise exceptions.UnknownJupyterHubError(
                    "Something went wrong calling JupyterHub. Got the response "
                    f"'{user_response}' with content '{str(user_response.content)}'"
                )

        try:
            user_data = user_response.json()
            return JupyterUser(user_data['name'], user_data.get('server', server))
        except (KeyError, json.decoder.JSONDecodeError) as e:
            raise exceptions.NotAJupyterHubUrl(
                "User response data is not correct, "
                f"is the URL '{uri}' for a JupyterHub?"
            ) from e
