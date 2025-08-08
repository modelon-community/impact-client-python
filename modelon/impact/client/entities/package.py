from typing import Any, Dict, List

from modelon.impact.client.entities.interfaces.package import PackageInterface
from modelon.impact.client.entities.model import Model
from modelon.impact.client.sal.modeling import ModelingService
from modelon.impact.client.sal.service import Service


class Package(PackageInterface):
    """Class containing Package functionalities."""

    def __init__(
        self,
        class_path: str,
        workspace_id: str,
        project_id: str,
        service: Service,
        modeling_sal: ModelingService,
    ):
        self._class_path = class_path
        self._workspace_id = workspace_id
        self._project_id = project_id
        self._sal = service
        self._modeling_sal = modeling_sal

    def __repr__(self) -> str:
        return f"Package name '{self._class_path}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Package) and obj._class_path == self._class_path

    @property
    def name(self) -> str:
        """Package name."""
        return self._class_path

    @property
    def project_id(self) -> str:
        """Project ID."""
        return self._project_id

    def _info(self) -> Dict[str, Any]:
        return self._modeling_sal.get_top_class_info(self._class_path)

    @property
    def is_editable(self) -> bool:
        """Returns True if the package is editable."""
        return self._info()["editable"]

    @property
    def is_structured(self) -> bool:
        """Returns True if the package is structured."""
        return self._info()["structured"]

    @property
    def is_enabled(self) -> bool:
        """Returns True if the package is enabled."""
        return self._info()["enabled"]

    def get_uses(self) -> Dict[str, str]:
        """Returns the libraries the package has dependencies on."""
        return self._info()["uses"]

    def get_sub_models(self) -> List[Model]:
        return [
            Model(class_path, self._workspace_id, self._project_id, self._sal)
            for class_path in self._modeling_sal.get_sub_models(self._class_path)
        ]

    def get_sub_packages(self) -> List["Package"]:
        return [
            Package(
                class_path,
                self._workspace_id,
                self._project_id,
                self._sal,
                self._modeling_sal,
            )
            for class_path in self._modeling_sal.get_sub_packages(self._class_path)
        ]

    def get_all_sub_models(self) -> List[Model]:
        return [
            Model(class_path, self._workspace_id, self._project_id, self._sal)
            for class_path in self._modeling_sal.get_all_sub_models(self._class_path)
        ]
