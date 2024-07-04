import abc
import enum
from typing import Any, Union

Scalar = Union[bool, int, float, str]


class DataType(enum.Enum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    REAL = "REAL"
    STRING = "STRING"
    ENUMERATION = "ENUMERATION"


class Modifier(abc.ABC):
    @abc.abstractmethod
    def to_dict(self, name: str) -> dict[str, Any]:
        """Returns a dict representation of the modifier."""

    @abc.abstractmethod
    def to_value(self) -> Scalar:
        """Returns a single scalar representing the modifier, operators are serialized
        as strings."""


class ValueModifier(Modifier):
    def __init__(self, value: Scalar, data_type: DataType) -> None:
        self.value = value
        self.data_type = data_type

    def to_dict(self, name: str) -> dict[str, Any]:
        return {
            "kind": "value",
            "name": name,
            "value": self.value,
            "dataType": self.data_type.value,
        }

    def to_value(self) -> Scalar:
        return self.value


class Enumeration(ValueModifier):
    def __init__(self, value: str) -> None:
        super().__init__(value, DataType.ENUMERATION)


def data_type_from_value(value: Scalar) -> DataType:
    if isinstance(value, bool):
        return DataType.BOOLEAN
    elif isinstance(value, int):
        return DataType.INTEGER
    elif isinstance(value, float):
        return DataType.REAL
    elif isinstance(value, str):
        return DataType.STRING

    raise ValueError(f"Unsupported type for modifier value {value}")


def ensure_as_modifier(value: Union[Scalar, Modifier]) -> Modifier:
    if isinstance(value, Modifier):
        return value

    return ValueModifier(value, data_type_from_value(value))


def modifiers_to_dict(variable_modifiers: dict[str, Modifier]) -> Any:
    return [m.to_dict(name) for name, m in variable_modifiers.items()]
