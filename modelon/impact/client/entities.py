class Workspace:
    def __init__(self, workspace_id):
        self._workspace_id = workspace_id

    def __repr__(self):
        return self._workspace_id.__repr__()

    def __eq__(self, obj):
        return isinstance(obj, Workspace) and obj._workspace_id == self._workspace_id
