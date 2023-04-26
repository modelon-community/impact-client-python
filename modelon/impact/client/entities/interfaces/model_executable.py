class BaseModelExecutable:
    def __init__(self, fmu_id: str):
        self._fmu_id = fmu_id

    def __repr__(self) -> str:
        return f"FMU with id '{self._fmu_id}'"

    @property
    def id(self) -> str:
        """FMU id."""
        return self._fmu_id
