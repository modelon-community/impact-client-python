from modelon.impact.client import entities


def get_options(default_options, options):
    return (
        dict(default_options())
        if options is None
        else dict(options)
        if isinstance(options, entities.ExecutionOptions)
        else options
    )


def case_to_identifier_dict(case):
    return {
        "caseId": case.id,
        "experimentId": case.experiment_id,
    }
