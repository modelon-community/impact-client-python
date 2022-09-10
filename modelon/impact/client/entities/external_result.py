from modelon.impact.client.sal.service import Service


class _ExternalResultMetaData:
    """
    Class containing external result metadata.
    """

    def __init__(self, id: str, name: str, description: str, workspace_id: str):
        self._id = id
        self._name = name
        self._description = description
        self._workspace_id = workspace_id

    @property
    def id(self) -> str:
        """Result id"""
        return self._id

    @property
    def name(self) -> str:
        """Label for result"""
        return self._name

    @property
    def description(self) -> str:
        """Description of the result"""
        return self._description

    @property
    def workspace_id(self) -> str:
        """Name of workspace"""
        return self._workspace_id


class ExternalResult:
    """
    Class containing  external result.
    """

    def __init__(self, result_id: str, service: Service):
        self._result_id = result_id
        self._sal = service

    def __repr__(self):
        return f"Result id '{self._result_id}'"

    def __eq__(self, obj):
        return isinstance(obj, ExternalResult) and obj._result_id == self._result_id

    @property
    def id(self) -> str:
        """Result id"""
        return self._result_id

    @property
    def metadata(self) -> _ExternalResultMetaData:
        """External result metadata."""
        upload_meta = self._sal.workspace.get_uploaded_result_meta(self._result_id)[
            "data"
        ]
        id = upload_meta.get("id")
        name = upload_meta.get("name")
        description = upload_meta.get("description")
        workspace_id = upload_meta.get("workspaceId")
        return _ExternalResultMetaData(id, name, description, workspace_id)

    def delete(self):
        self._sal.workspace.delete_uploaded_result(self._result_id)
