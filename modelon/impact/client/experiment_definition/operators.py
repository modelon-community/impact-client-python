"""This module contains operators for parametrizing batch runs."""
from typing import Any
from abc import abstractmethod
from dataclasses import dataclass


class Operator:
    """Base class for an Operator."""

    @abstractmethod
    def __str__(self) -> str:
        "Returns a string representation of the operator"


@dataclass
class Range(Operator):
    """Range operator class for parametrizing batch runs. Range(a, b, c)
    represents c linearly spaced values in the (real) interval [a, b]; b >= a.
    The functionality is analogous to numpy.linspace.

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


class Choices(Operator):
    """Choices operator class for parametrizing batch runs. Choices defines a
    list of specified values a Modifier expression can take.

    Args:
        values: Variable number of numerical arguments to sweep.

    Example::

        from modelon.impact.client import Choices

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Choices(0.1, 0.5)})

    """

    def __init__(self, *values: Any):
        self.values = values

    def __str__(self) -> str:
        return f"choices({', '.join(map(str, self.values))})"


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
        return f"beta({self.alpha},{self.alpha})"


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
    start: float = float('-inf')
    end: float = float('inf')

    def __str__(self) -> str:
        return f"normal({self.mean},{self.variance},{self.start},{self.end})"
