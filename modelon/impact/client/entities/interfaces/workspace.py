class BaseWorkspace:
    def __init__(self, workspace_id: str):
        self._workspace_id = workspace_id

    def __repr__(self) -> str:
        return f"Workspace with id '{self._workspace_id}'"

    @property
    def id(self) -> str:
        """Workspace id."""
        return self._workspace_id
