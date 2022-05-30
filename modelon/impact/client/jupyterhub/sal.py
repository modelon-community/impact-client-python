import json.decoder

import requests

from modelon.impact.client.jupyterhub import exceptions
from modelon.impact.client.sal.context import Context


class JupyterContext:
    def __init__(self, base=None):
        self._base = base if base else Context()
        self._token = None

    @property
    def session(self):
        return self._base.session

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        self.session.headers.update({'Authorization': 'token %s' % token})


class JupyterUser:
    def __init__(self, user_id, server):
        self.id = user_id
        self._server = server

    def server_running(self):
        return self._server is not None

    def impact_server_uri(self, jupyterhub_uri):
        return jupyterhub_uri / f'user/{self.id}/impact'


class JupyterHubService:
    @classmethod
    def get_user_data(cls, uri, context):
        auth_token_url = (
            uri / f'hub/api/authorizations/token/{context.token}'
        ).resolve()

        try:
            user_respons = context.session.get(auth_token_url)
        except requests.exceptions.RequestException as e:
            raise exceptions.NotAJupyterHubUrl(
                f"Did not get a response from {uri}, is the URL correct?"
            ) from e

        if not user_respons.ok:
            if user_respons.status_code == 403:
                raise exceptions.JupyterHubAuthrizationError(
                    "Could not authorize against JupyterHub, is the token correct?"
                )
            elif user_respons.status_code == 404:
                raise exceptions.NotAJupyterHubUrl(
                    f"Missing resource '{auth_token_url}'. Possible errors are "
                    f"that the URL '{uri}' don't points to a JupyterHub or "
                    "that the user of the API key as been deleted."
                )
            else:
                raise exceptions.UnknownJupyterHubError(
                    "Something went wrong calling JupyterHub. Got the response "
                    f"'{user_respons}' with content '{user_respons.content}'"
                )

        try:
            user_data = user_respons.json()
            return JupyterUser(user_data['name'], user_data['server'])
        except (KeyError, json.decoder.JSONDecodeError) as e:
            raise exceptions.NotAJupyterHubUrl(
                "User response data is not correct, "
                f"is the URL '{uri}' for a JupyterHub?"
            ) from e
