import enum
from typing import Union

Scalar = Union[bool, int, float, str]


class DataType(enum.Enum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    REAL = "REAL"
    STRING = "STRING"


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
