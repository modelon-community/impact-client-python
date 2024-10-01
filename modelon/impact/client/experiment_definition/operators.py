"""This module contains operators for parametrizing batch runs."""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union

from modelon.impact.client.experiment_definition.modifiers import (
    DataType,
    Enumeration,
    Modifier,
    Scalar,
    data_type_from_value,
)


class Operator(Modifier):
    """Base class for an Operator."""

    @abstractmethod
    def __str__(self) -> str:
        "Returns a string representation of the operator"

    def to_value(self) -> str:
        return str(self)


@dataclass
class Range(Operator):
    """Range operator class for parametrizing batch runs. Range(a, b, c) represents c
    linearly spaced values in the (real) interval [a, b]; b >= a. The functionality is
    analogous to numpy.linspace.

    Args:
        start_value: The start value for the sweep parameter.
        end_value: The end value for the sweep parameter.
        no_of_steps: The number of steps to intermediate steps
        to take between start_value and end_value.

    Example::

        from modelon.impact.client import Range

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Range(0.1, 0.5, 3)})

    """

    start_value: float
    end_value: float
    no_of_steps: int

    def __str__(self) -> str:
        return f"range({self.start_value},{self.end_value},{self.no_of_steps})"

    def to_dict(self, name: str) -> dict[str, Any]:
        return {
            "kind": "range",
            "name": name,
            "start": self.start_value,
            "end": self.end_value,
            "steps": self.no_of_steps,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Range":
        return Range(
            start_value=data["start"], end_value=data["end"], no_of_steps=data["steps"]
        )


class Choices(Operator):
    """Choices operator class for parametrizing batch runs. Choices defines a list of
    specified values a Modifier expression can take.

    Args:
        values: Variable number of numerical arguments to sweep.

    Example::

        from modelon.impact.client import Choices

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Choices(0.1, 0.5)})

    """

    def __init__(self, *values: Scalar, data_type: Optional[DataType] = None):
        self.values = values
        self.data_type = self._resolve_data_type(values, data_type)

    @classmethod
    def _resolve_data_type(
        cls, values: tuple[Scalar, ...], given_data_type: Optional[DataType]
    ) -> DataType:
        used_data_type = given_data_type
        for value in values:
            value_type = data_type_from_value(value)

            if not used_data_type:
                used_data_type = value_type

            if cls._widen_from_int_to_real(given_data_type, used_data_type, value_type):
                used_data_type = DataType.REAL

            if used_data_type == DataType.REAL and value_type == DataType.INTEGER:
                pass  # Integer can be assigned to real, do nothing
            elif used_data_type != value_type:
                if given_data_type:
                    raise ValueError(
                        f"Choices value '{value}', not compatible "
                        f"with specified data type '{given_data_type}'"
                    )
                else:
                    raise ValueError(
                        f"Choices values are resolving to '{used_data_type}', "
                        f"which is not compatible with the value '{value}'"
                    )

        return used_data_type or DataType.REAL

    @classmethod
    def _widen_from_int_to_real(
        cls,
        given_data_type: Optional[DataType],
        used_data_type: DataType,
        value_type: DataType,
    ) -> bool:
        # If no given data type and current used is integer but there
        # is a value with type real then we say we can widen the type
        # to use real.
        return (
            given_data_type is None
            and used_data_type == DataType.INTEGER
            and value_type == DataType.REAL
        )

    def __str__(self) -> str:
        return f"choices({', '.join(map(str, self.values))})"

    def to_dict(self, name: str) -> dict[str, Any]:
        return {
            "kind": "choices",
            "name": name,
            "values": list(self.values),
            "dataType": self.data_type.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Choices:
        return Choices(*data["values"], data_type=DataType(data["dataType"]))


@dataclass
class Uniform(Operator):
    """Uniform distribution class for parametrizing batch runs.For mathematical
    background, see e.g.,
    https://en.wikipedia.org/wiki/Continuous_uniform_distribution.

    Args:
        start (float): Starting value of the interval.
        end (float): End value of the interval. Requires start <= end.

    Example::

        from modelon.impact.client import Uniform

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Uniform(0.1, 0.5)})

    """

    start: float
    end: float

    def __str__(self) -> str:
        return f"uniform({self.start},{self.end})"

    def to_dict(self, name: str) -> dict[str, Any]:
        return {
            "kind": "uniform",
            "name": name,
            "start": self.start,
            "end": self.end,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Uniform:
        return Uniform(start=data["start"], end=data["end"])


@dataclass
class Beta(Operator):
    """Beta distribution class for parametrizing batch runs. For mathematical
    background, see e.g., https://en.wikipedia.org/wiki/Beta_distribution.

    Args:
        alpha (float): 'alpha' resp. 'a' parameter of beta distribution, requires
            alpha > 0
        beta (float): 'beta' resp. 'b' parameter of beta distribution, requires
            beta > 0

    Example::

        from modelon.impact.client import Beta

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Beta(0.1, 0.5, 3)})

    """

    alpha: float
    beta: float

    def __str__(self) -> str:
        return f"beta({self.alpha},{self.beta})"

    def to_dict(self, name: str) -> dict[str, Any]:
        return {
            "kind": "beta",
            "name": name,
            "alpha": self.alpha,
            "beta": self.beta,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Beta:
        return Beta(alpha=data["alpha"], beta=data["beta"])


@dataclass
class Normal(Operator):
    """Normal distribution class for parametrizing batch runs.For mathematical
    background, see e.g., https://en.wikipedia.org/wiki/Normal_distribution
    https://en.wikipedia.org/wiki/Truncated_normal_distribution Supports both
    the standard and truncated Normal distribution. The standard Normal
    distribution is the default, add additional start & end parameters for
    truncation.

    Args:
        mean (float): Mean resp. location of the distribution.
        variance (float): Variance of the normal distribution. Requires var > 0.
        start (float): Lower bound. Default: -inf
        end (float): Upper bound, requires end > start. Default: inf

    Example::

        from modelon.impact.client import Normal

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Normal(0.1, 0.5)})

    """

    mean: float
    variance: float
    start: Optional[float] = None
    end: Optional[float] = None

    def __str__(self) -> str:
        start = self.start or float("-inf")
        end = self.end or float("inf")
        return f"normal({self.mean},{self.variance},{start},{end})"

    def to_dict(self, name: str) -> dict[str, Any]:
        return {
            "kind": "normal",
            "name": name,
            "mean": self.mean,
            "variable": self.variance,
            "start": self.start,
            "end": self.end,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Normal:
        return Normal(
            mean=data["mean"],
            variance=data["variance"],
            start=data["start"],
            end=data["end"],
        )


def get_operator_from_dict(
    data: dict[str, Any]
) -> Union[Range, Choices, Uniform, Beta, Normal, Enumeration, int, float, bool, str]:
    kind = data["kind"]
    if kind == "range":
        return Range.from_dict(data)
    elif kind == "choices":
        return Choices.from_dict(data)
    elif kind == "uniform":
        return Uniform.from_dict(data)
    elif kind == "beta":
        return Beta.from_dict(data)
    elif kind == "normal":
        return Normal.from_dict(data)
    elif kind == "value":
        data_type = DataType(data["dataType"])
        if data_type == DataType.ENUMERATION:
            return Enumeration(data["value"])
        else:
            return data["value"]
    raise ValueError(f"Unsupported operator kind: {kind}!")
