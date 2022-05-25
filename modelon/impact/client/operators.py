"""This module contains operators for parametrizing batch runs."""

from abc import abstractmethod
from dataclasses import dataclass


class Operator:
    """
    Base class for an Operator.
    """

    @abstractmethod
    def __str__(self):
        "Returns a string representation of the operator"


@dataclass
class Range(Operator):
    """
    Range operator class for parameterizing batch runs.

    Parameters:

        start_value --
            The start value for the sweep parameter.

        end_value --
            The end value for the sweep parameter.

        no_of_steps --
            The number of steps to intermediate steps to take between start_value
            and end_value.

    Examples::

        from modelon.impact.client import Range

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Range(0.1, 0.5, 3)})
    """

    start_value: float
    end_value: float
    no_of_steps: int

    def __str__(self):
        return f"range({self.start_value},{self.end_value},{self.no_of_steps})"


class Choices(Operator):
    """
    Choices operator class for parameterizing batch runs.

    Parameters:

        values --
            Variable number of numerical arguments to sweep.

    Examples::

        from modelon.impact.client import Choices

        fmu = model.compile().wait()
        experiment_definition = fmu.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': 2,
            'inertia2.J': Choices(0.1, 0.5)})
    """

    def __init__(self, *values):
        self.values = values

    def __str__(self):
        return f"choices({', '.join(map(str, self.values))})"
