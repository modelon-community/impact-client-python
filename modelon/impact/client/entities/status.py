from enum import Enum


class CaseStatus(Enum):
    """
    Class representing an enumeration for the possible
    Case run info states.
    """

    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NOT_STARTED = "not_started"
    STARTED = 'started'


class ExperimentStatus(Enum):
    """
    Class representing an enumeration for the possible
    experiment run info states.
    """

    NOTSTARTED = "not_started"
    CANCELLED = "cancelled"
    DONE = "done"
    FAILED = "failed"


class ModelExecutableStatus(Enum):
    """
    Class representing an enumeration for the possible
    model-executable run info states.
    """

    NOTSTARTED = "not_started"
    CANCELLED = "cancelled"
    SUCCESSFUL = "successful"
    FAILED = "failed"
