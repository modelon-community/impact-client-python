from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

from modelon.impact.client.configuration import Experimental
from modelon.impact.client.entities.package import Package
from modelon.impact.client.exceptions import NoProjectFoundForClassError
from modelon.impact.client.sal.modeling import ModelingService
from modelon.impact.client.sal.service import Service
from modelon.impact.client.views import (
    ANALYSIS_KIND,
    PLOT_TYPES,
    AnalysisPlot,
    build_plot,
    new_analysis_view_definition,
    to_analysis_plot,
    updated_analysis_view_definition,
)

if TYPE_CHECKING:
    from modelon.impact.client.entities.model import Model


class ModelingSession:
    """Class containing ModelingService functionalities."""

    def __init__(
        self,
        session_id: str,
        workspace_id: str,
        project_id: str,
        modeling_sal: ModelingService,
        service: Service,
    ):
        self._session_id = session_id
        self._workspace_id = workspace_id
        self._project_id = project_id
        self._modeling_sal = modeling_sal
        self._sal = service

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, ModelingSession) and obj._session_id == self._session_id

    def __repr__(self) -> str:
        return f"Modeling session with ID '{self._session_id}'"

    def close(self) -> None:
        return self._modeling_sal.close_session()

    @Experimental
    def get_model(self, class_name: str) -> "Model":
        """Returns a Model class object backed by this modeling session.

        Example::

            with workspace.new_modeling_session() as session:
                model = session.get_model("LibA.Model")
                parameters = model.get_parameters()

        """
        from modelon.impact.client.entities.model import Model

        return Model(
            class_name,
            self._workspace_id,
            self._project_id,
            self._sal,
            modeling_sal_getter=lambda: self._modeling_sal,
        )

    def _project_id_for_class(self, class_path: str) -> str:
        """Returns the project the class's top-level package belongs to.

        A view is stored per project, so a write has to go to the project that owns the
        class rather than to whichever project happens to be first.

        """
        top_class = class_path.split(".")[0]
        for project_id, top_classes in self._modeling_sal.get_top_classes().items():
            if any(candidate["name"] == top_class for candidate in top_classes):
                return project_id
        raise NoProjectFoundForClassError(
            f"Could not find the project holding '{class_path}' in this workspace."
        )

    def _get_analysis_view(
        self, project_id: str, class_path: str
    ) -> Optional[Dict[str, Any]]:
        views = self._modeling_sal.get_views([project_id], class_path, [ANALYSIS_KIND])
        return views[0] if views else None

    @Experimental
    def add_analysis_plot(
        self,
        class_path: str,
        variables: Sequence[str],
        independent_variable: Optional[str] = None,
        plot_type: str = "line",
        title: Optional[str] = None,
    ) -> AnalysisPlot:
        """Adds a plot to a class's analysis dashboard, creating the dashboard if the
        class has none yet.

        The plot is placed where the dashboard would have placed it and left for the
        user to open; a session with that dashboard already open shows it without a
        reload.

        Args:
            class_path: Fully qualified path of the class the dashboard belongs to.
            variables: Result variables to draw, spelled as the result spells them.
                They all go on one plot; call again for a second plot.
            independent_variable: What goes on the x axis. Leave unset to let the
                dashboard choose, which is time for a dynamic result and the swept
                parameter for a steady-state one.
            plot_type: "line" (default), "scatter" or "histogram".
            title: A heading for the plot. Leave unset to let the dashboard number it.

        Returns:
            The plot that was added.

        Raises:
            ValueError: If no variables were given, or the plot type is not one the
                dashboard draws.
            NoProjectFoundForClassError: If no project in this workspace holds the
                class.

        Example::

            with workspace.new_modeling_session() as session:
                session.add_analysis_plot(
                    "LibA.Tank", ["tank.level"], title="Tank level"
                )

        """
        if not variables:
            raise ValueError("No variables were given to plot.")
        if plot_type not in PLOT_TYPES:
            raise ValueError(
                f"Unknown plot type '{plot_type}'. Use one of: "
                f"{', '.join(sorted(PLOT_TYPES))}."
            )

        project_id = self._project_id_for_class(class_path)
        view = self._get_analysis_view(project_id, class_path)
        existing_plots = (view or {}).get("plots") or []
        plot = build_plot(
            variables,
            existing_plots,
            independent_variable=independent_variable,
            plot_type=plot_type,
            title=title,
        )
        plots = [*existing_plots, plot]
        if view is None:
            self._modeling_sal.create_view(
                project_id, class_path, new_analysis_view_definition(plots)
            )
        else:
            self._modeling_sal.update_view(
                project_id,
                class_path,
                view["metadata"]["viewId"],
                updated_analysis_view_definition(view, plots),
            )
        return to_analysis_plot(plot)

    @Experimental
    def get_top_level_packages(self) -> List[Package]:
        libraries = self._modeling_sal.get_top_classes()
        packages = []
        for project_id, top_classes in libraries.items():
            for top_class in top_classes:
                packages.append(
                    Package(
                        top_class["name"],
                        self._workspace_id,
                        project_id,
                        self._sal,
                        self._modeling_sal,
                    )
                )
        return packages
