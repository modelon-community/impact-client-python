import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from modelon.impact.client.experiment_definition.interfaces.expansion import (
    ExpansionAlgorithm,
)

logger = logging.getLogger(__name__)


@dataclass
class LatinHypercube(ExpansionAlgorithm):
    """LatinHypercube expansion class. Produces <samples> cases, picks a random value
    from each modifier expression for each case. The resulting cases are orthogonal,
    i.e., the values of a given modifier expression do not repeat. The exception are
    singular modifiers, e.g., experiment_definition.with_modifiers({'PI.k': 10}), these
    result in the same value for all cases. Singular modifiers do not affect the result
    (with respect to the seed) in the resulting experiment.

    Args:
        samples (int):
            Positive integer; number of cases the experiment will produce.
        seed (int) :
            Using the same seed will result in the same output for an experiment with
            the same modifiers. If not set or None: picks a random seed. Must be a
            non-negative integer. Default: None.

    Example::

        from modelon.impact.client import LatinHypercube, Beta, Normal

        model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
        experiment_definition = model.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': Beta(0.1, 0.9),
            'inertia2.J': Normal(0.1, 0.5)}).with_expansion(LatinHypercube(5,1))

    """

    samples: int
    seed: Optional[int] = None

    def __str__(self) -> str:
        return "LATINHYPERCUBE"

    def get_parameters_as_dict(self) -> Optional[Dict[str, Any]]:
        return asdict(self)


class FullFactorial(ExpansionAlgorithm):
    """Full-factorial expansion class. Creates experiment with all possible
    combinations of the input modifiers expressions. Supported Operator
    expressions are: Range and Choices. The size of an experiment with
    FullFactorial expansion is the product of the modifier operator length.
    This number can grow very rapidly if using a lot of modifiers.

    Example::

        from modelon.impact.client import FullFactorial, Range

        model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")

        experiment_definition = model.new_experiment_definition(custom_function)
        .with_modifiers({'inertia1.J': Range(0.1, 0.9, 2)})
        .with_expansion(FullFactorial())

        OR

        # Full-factorial is the default and does not need to be specified explicitly.
        experiment_definition = model.new_experiment_definition(custom_function)
        .with_modifiers({'inertia1.J': Range(0.1, 0.9, 2)})

    """

    def __str__(self) -> str:
        return "FULLFACTORIAL"

    def get_parameters_as_dict(self) -> Optional[Dict[str, Any]]:
        return None


@dataclass
class Sobol(ExpansionAlgorithm):
    """Expansion method based on the Sobol sequence. The Sobol sequence is a minimal
    discrepancy quasi-random sampling methods and suitable for achieving a good coverage
    of the design space. Singular Modifiers, e.g.,
    experiment_definition.with_modifiers({'PI.k': 10}), do not affect the result in the
    resulting experiment.

    Args:
        samples (int):
            Positive integer; number of cases the Experiment will produce.
            Expansions where the number of samples is a power of 2 yield
            additional balances properties.

    Example::

        from modelon.impact.client import Sobol, Beta, Normal

        model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
        experiment_definition = model.new_experiment_definition(
            custom_function).with_modifiers({'inertia1.J': Beta(0.1, 0.9),
            'inertia2.J': Normal(0.1, 0.5)}).with_expansion(Sobol(5))

    """

    samples: int

    def __str__(self) -> str:
        return "SOBOL"

    def get_parameters_as_dict(self) -> Optional[Dict[str, Any]]:
        return asdict(self)
