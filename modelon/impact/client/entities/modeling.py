from __future__ import annotations

from typing import TYPE_CHECKING, List

from modelon.impact.client.configuration import Experimental
from modelon.impact.client.entities.package import Package
from modelon.impact.client.sal.modeling import ModelingService
from modelon.impact.client.sal.service import Service

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
