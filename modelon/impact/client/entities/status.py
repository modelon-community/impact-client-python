from enum import Enum


class CaseStatus(Enum):
    """Class representing an enumeration for the possible Case run info states."""

    SUCCESSFUL = "successful"
    """Status for case that has been executed successfully."""

    FAILED = "failed"
    """Status for case execution that has failed."""

    CANCELLED = "cancelled"
    """Status for experiment execution that has not yet started."""

    NOT_STARTED = "not_started"
    """Status for experiment execution that has not yet started."""

    STARTED = "started"
    """Status for case that has  started execution."""


class ExperimentStatus(Enum):
    """Class representing an enumeration for the possible experiment run info states."""

    NOTSTARTED = "not_started"
    """Status for experiment execution that has not yet started."""

    CANCELLED = "cancelled"
    """Status for a cancelled experiment execution."""

    DONE = "done"
    """Status for a completed experiment execution."""

    FAILED = "failed"
    """Status for a failed experiment execution."""


class ModelExecutableStatus(Enum):
    """Class representing an enumeration for the possible model-executable run info
    states."""

    NOTSTARTED = "not_started"
    """Status for compilation that has not yet started."""

    CANCELLED = "cancelled"
    """Status for a cancelled compilation."""

    SUCCESSFUL = "successful"
    """Status for a successful compilation."""

    FAILED = "failed"
    """Status for a failed compilation."""
