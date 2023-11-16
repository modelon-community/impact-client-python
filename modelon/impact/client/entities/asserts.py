from typing import List

from modelon.impact.client import exceptions


def assert_successful_operation(
    is_successful: bool, operation_name: str = "Operation"
) -> None:
    if not is_successful:
        raise exceptions.OperationFailureError(
            f"{operation_name} failed! See the log for more info!"
        )


def assert_variable_in_result(
    variables: List[str], result_variables: List[str]
) -> None:
    add = set(variables) - set(result_variables)
    if add:
        raise ValueError(
            f"Variable(s) '{', '.join(add)}' {'are' if len(add)>1 else 'is'} not"
            " present in the result"
        )
