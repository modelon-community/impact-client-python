from modelon.impact.client.options import BaseExecutionOptions


def get_options(default_options, options):
    return (
        dict(default_options())
        if options is None
        else dict(options)
        if isinstance(options, BaseExecutionOptions)
        else options
    )


def case_to_identifier_dict(case):
    return {
        "caseId": case.id,
        "experimentId": case.experiment_id,
    }
