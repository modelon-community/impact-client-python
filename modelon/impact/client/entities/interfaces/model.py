class BaseModel:
    def __init__(self, class_name: str):
        self._class_name = class_name

    def __repr__(self) -> str:
        return f"Class name '{self._class_name}'"

    @property
    def name(self) -> str:
        """Class name."""
        return self._class_name
