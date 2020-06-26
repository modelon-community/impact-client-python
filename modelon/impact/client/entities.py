class Workspace:
    def __init__(self, workspace_id):
        self._workspace_id = workspace_id

    def __repr__(self):
        return f"Workspace with id '{self._workspace_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Workspace) and obj._workspace_id == self._workspace_id
