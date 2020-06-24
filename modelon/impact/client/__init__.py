import logging
import modelon.impact.client.entities
import modelon.impact.client.sal.service


logger = logging.getLogger(__name__)


class Client:
    def __init__(self, url=None, context=None):
        if url is None:
            url = "http://localhost:8080/"
            logger.warning("No URL for client was specified, will use: {}".format(url))

        self._sal = modelon.impact.client.sal.service.Service(url, context)
        # TODO: check that the API is of a version that client can use!

    def get_workspace(self, workspace_id):
        # TODO: should have an endpoint for getting a single workspace
        return modelon.impact.client.entities.Workspace(workspace_id)

    def get_workspaces(self):
        resp = self._sal.get("api/workspaces")
        return [
            modelon.impact.client.entities.Workspace(item['id'])
            for item in resp.data['data']['items']
        ]

    def create_workspace(self, name):
        resp = self._sal.post("api/workspaces", {"new": {"name": name}})
        return modelon.impact.client.entities.Workspace(resp.data['workspaceId'])
