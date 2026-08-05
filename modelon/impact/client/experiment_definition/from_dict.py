from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from modelon.impact.client.entities._initialize_from import (
    _resolve_extension_initialize_from,
    _resolve_initialize_from,
)
from modelon.impact.client.entities.model_executable import ModelExecutable
from modelon.impact.client.experiment_definition.expansion import expansion_from_dict
from modelon.impact.client.experiment_definition.extension import (
    SimpleExperimentExtension,
)
from modelon.impact.client.experiment_definition.fmu_based import (
    SimpleFMUExperimentDefinition,
)
from modelon.impact.client.experiment_definition.model_based import (
    SimpleModelicaExperimentDefinition,
)
from modelon.impact.client.experiment_definition.operators import get_operator_from_dict

if TYPE_CHECKING:
    from modelon.impact.client.entities.custom_function import CustomFunction
    from modelon.impact.client.entities.model import Model
    from modelon.impact.client.sal.service import Service

logger = logging.getLogger(__name__)

ValidExperimentDefinitions = Union[
    SimpleModelicaExperimentDefinition,
    SimpleFMUExperimentDefinition,
]


def _create_model(class_name: str, workspace_id: str, sal: Service) -> Model:
    # Imported here as the model entity module imports this module.
    from modelon.impact.client.entities.model import Model

    return Model(class_name, workspace_id=workspace_id, project_id="", service=sal)


def _get_variable_modifiers(modifiers: Dict[str, Any]) -> Dict[str, Any]:
    return {
        mod["name"]: get_operator_from_dict(mod)
        for mod in modifiers.get("variables", [])
    }


def _build_extensions(
    extensions: List[Dict[str, Any]],
    workspace_id: str,
    sal: Service,
) -> List[SimpleExperimentExtension]:
    # Imported here as the model entity module imports this module.
    from modelon.impact.client.entities.model import to_domain_parameter_value

    sim_exts = []
    for extension in extensions:
        analysis = extension.get("analysis", {})
        modifiers = extension.get("modifiers", {})
        sim_ext = SimpleExperimentExtension(
            parameter_modifiers={
                param["name"]: param["value"]
                for param in analysis.get("parameters", [])
            },
            solver_options=analysis.get("solverOptions"),
            simulation_options=analysis.get("simulationOptions"),
            simulation_log_level=analysis.get("simulationLogLevel"),
            initialize_from=_resolve_extension_initialize_from(
                workspace_id, sal, modifiers
            ),
        ).with_modifiers(
            modifiers={
                mod["name"]: to_domain_parameter_value(mod)
                for mod in modifiers.get("variables", [])
            }
        )
        case_labels = [data.get("label") for data in extension.get("caseData", [])]
        if case_labels:
            sim_ext = sim_ext.with_case_label(case_labels[0])
        sim_exts.append(sim_ext)
    return sim_exts


def _build_modelica_definition(
    base: Dict[str, Any],
    custom_function: CustomFunction,
    workspace_id: str,
    sal: Service,
    model: Optional[Model] = None,
) -> SimpleModelicaExperimentDefinition:
    modelica = base["model"]["modelica"]
    analysis = base["analysis"]
    return (
        SimpleModelicaExperimentDefinition(
            model=model or _create_model(modelica["className"], workspace_id, sal),
            custom_function=custom_function,
            compiler_options=modelica.get("compilerOptions", {}),
            fmi_target=modelica.get("fmiTarget", "me"),
            fmi_version=modelica.get("fmiVersion", "2.0"),
            platform=modelica.get("platform", "auto"),
            compiler_log_level=modelica.get("compilerLogLevel", "warning"),
            runtime_options=modelica.get("runtimeOptions", {}),
            solver_options=analysis.get("solverOptions", {}),
            simulation_options=analysis.get("simulationOptions", {}),
            simulation_log_level=analysis.get("simulationLogLevel", "WARNING"),
            initialize_from=_resolve_initialize_from(
                workspace_id, sal, base.get("modifiers", {})
            ),
        )
        .with_modifiers(_get_variable_modifiers(base.get("modifiers", {})))
        .with_expansion(expansion_from_dict(base.get("expansion", {})))
    )


def _build_fmu_definition(
    base: Dict[str, Any],
    custom_function: CustomFunction,
    workspace_id: str,
    sal: Service,
) -> SimpleFMUExperimentDefinition:
    # Note: The FMU based experiment definition has no expansion support,
    # so any expansion data in 'base' is not carried over here.
    analysis = base["analysis"]
    modifiers = base.get("modifiers", {})
    return SimpleFMUExperimentDefinition(
        fmu=ModelExecutable(workspace_id, base["model"]["fmu"]["id"], sal),
        custom_function=custom_function,
        solver_options=analysis.get("solverOptions", {}),
        simulation_options=analysis.get("simulationOptions", {}),
        simulation_log_level=analysis.get("simulationLogLevel", "WARNING"),
        initialize_from=_resolve_initialize_from(workspace_id, sal, modifiers),
    ).with_modifiers(modifiers=_get_variable_modifiers(modifiers))


def _build_experiment_definition(
    info: Dict[str, Any],
    custom_function: CustomFunction,
    workspace_id: str,
    sal: Service,
    model: Optional[Model] = None,
) -> ValidExperimentDefinitions:
    """Build an experiment definition entity from an experiment dictionary.

    Args:
        info: The 'experiment' part of an experiment dictionary, holding the
            'base' definition and any 'extensions'.
        custom_function: The custom function to use for the definition.
        workspace_id: The workspace identifier.
        sal: The service class.
        model: The Model class object to use for class based experiments. If not
            given, a Model is created from the class name in the dictionary.

    Returns:
        An instance of SimpleModelicaExperimentDefinition for class based
        experiments and SimpleFMUExperimentDefinition for FMU based experiments.

    """
    base = info["base"]
    definition: ValidExperimentDefinitions = (
        _build_modelica_definition(base, custom_function, workspace_id, sal, model)
        if base["model"].get("modelica")
        else _build_fmu_definition(base, custom_function, workspace_id, sal)
    )
    extensions = info.get("extensions", [])
    if extensions:
        definition = definition.with_extensions(
            _build_extensions(extensions, workspace_id, sal)
        )
    return definition
