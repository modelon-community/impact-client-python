from __future__ import annotations

import enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from modelon.impact.client.operations.content_import import ContentImportOperation
from modelon.impact.client.sal.service import Service

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import BaseOperation


@enum.unique
class ContentType(enum.Enum):
    """Supported content types in a project."""

    MODELICA = "MODELICA"
    VIEWS = "VIEWS"
    FAVORITES = "FAVORITES"
    CUSTOM_FUNCTIONS = "CUSTOM_FUNCTIONS"
    REFERENCE_RESULTS = "REFERENCE_RESULTS"
    EXPERIMENT_DEFINITIONS = "EXPERIMENT_DEFINITIONS"
    GENERIC = "GENERIC"


class ProjectContent:
    """Content entry in a project."""

    def __init__(self, content: Dict[str, str], project_id: str, service: Service):
        self._content = content
        self._project_id = project_id
        self._sal = service

    def __repr__(self) -> str:
        return f"Project content with id '{self.id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, ProjectContent) and obj.id == self.id

    @property
    def relpath(self) -> Path:
        """Relative path in the project.

        Can be file (e.g., SomeLib.mo) or folder

        """
        return Path(self._content["relpath"])

    @property
    def content_type(self) -> ContentType:
        """Type of content."""
        return ContentType(self._content["contentType"])

    @property
    def id(self) -> str:
        """Content ID."""
        return self._content["id"]

    @property
    def name(self) -> Optional[str]:
        """Modelica library name."""
        return self._content.get("name")

    @property
    def default_disabled(self) -> str:
        return self._content["defaultDisabled"]

    def delete(self) -> None:
        """Deletes a project content.

        Example::

            content.delete()

        """
        self._sal.project.project_content_delete(self._project_id, self.id)

    @classmethod
    def from_operation(
        cls, operation: BaseOperation[ProjectContent], **kwargs: Any
    ) -> ProjectContent:
        assert isinstance(operation, ContentImportOperation)
        return cls(**kwargs, service=operation._sal)
