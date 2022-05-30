from dataclasses import dataclass, asdict
from abc import abstractmethod, ABC
from typing import Optional
import logging


logger = logging.getLogger(__name__)


class ExpansionAlgorithm(ABC):
    """
    Base class for an expansion algorithm.
    """

    @abstractmethod
    def __str__(self):
        "Returns a string representation of the expansion algorithm"

    @abstractmethod
    def get_parameters_as_dict(self):
        "Returns parameters as a dictionary"


@dataclass
class LatinHypercube(ExpansionAlgorithm):
    """LatinHypercube expansion class.

    Args:
        samples (int) --
            Positive integer; number of cases the Experiment will produce.
        seed (int)  --
            Using the same seed will result in the same output for an Experiment with
            the same modifiers. If not set or None: picks a random seed. Must be a
            non-negative integer. Default: None.

        Produces <samples> cases, picks a random value from each Modifier expression
        for each case. The resulting cases are ortogonal, i.e., the values of a given
        Modifier expression do not repeat. The exception are singular Modifiers, e.g.,
        Modifier('name', 1), these result in the same value for all cases. Singular
        Modifiers do not affect the result (with respect to the seed) in the resulting
        Experiment.

    """

    samples: int
    seed: Optional[int] = None

    def __str__(self):
        return "LATINHYPERCUBE"

    def get_parameters_as_dict(self):
        return asdict(self)


class FullFactorial(ExpansionAlgorithm):
    """Full-factorial expansion class.
    Creates experiment with all possible combinations of the input Modifiers
    expressions.

    Supported Modifier expressions:
        Range
        Choices
        Singular Modifiers, e.g., Modifier('name', 1), Modifier('name', 'a')

    Will return a single empty case if no Modifiers provided in Experiment.

    Observe that the size of an Experiment with FullFactorial expansion is the product
    of the Modifier lenghts. This number can grow very rapidly if using a lot of
    Modifiers.
    """

    def __str__(self):
        return "FULLFACTORIAL"

    def get_parameters_as_dict(self):
        return None


@dataclass
class Sobol(ExpansionAlgorithm):
    """Expansion method based on the Sobol sequence.
    The Sobol sequence is a minimal discrepancy quasi-random
    sampling methods and suitable for achieving a good coverage of the design space.

    Args:
        samples (int) --
            Positive integer; number of cases the Experiment will produce.
            Expansions where the number of samples is a power of 2 yield
            additional balances properties.

        Produces <samples> cases, based on the Sobol sequence.
        The points of the Sobol sequence are "extendible".
        I.e., given two Experiments with Expansions of different sample size, the larger
        Experiment contains all cases of the smaller one.

        Singular Modifiers, e.g., Modifier('name', 1), do not affect the result in the
        resulting Experiment.
    """

    samples: int

    def __str__(self):
        return "SOBOL"

    def get_parameters_as_dict(self):
        return asdict(self)
