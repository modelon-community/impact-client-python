from __future__ import annotations
from typing import TYPE_CHECKING, Any
from modelon.impact.client.operations.external_result_import import (
    ExternalResultImportOperation,
)
from modelon.impact.client.sal.service import Service

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import BaseOperation


class _ExternalResultMetaData:
    """Class containing external result metadata."""

    def __init__(self, id: str, name: str, description: str, workspace_id: str):
        self._id = id
        self._name = name
        self._description = description
        self._workspace_id = workspace_id

    @property
    def id(self) -> str:
        """Result id."""
        return self._id

    @property
    def name(self) -> str:
        """Label for result."""
        return self._name

    @property
    def description(self) -> str:
        """Description of the result."""
        return self._description

    @property
    def workspace_id(self) -> str:
        """Name of workspace."""
        return self._workspace_id


class ExternalResult:
    """Class containing  external result."""

    def __init__(self, result_id: str, service: Service):
        self._result_id = result_id
        self._sal = service

    def __repr__(self) -> str:
        return f"Result id '{self._result_id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, ExternalResult) and obj._result_id == self._result_id

    @property
    def id(self) -> str:
        """Result id."""
        return self._result_id

    @property
    def metadata(self) -> _ExternalResultMetaData:
        """External result metadata."""
        upload_meta = self._sal.external_result.get_uploaded_result(self._result_id)[
            "data"
        ]
        id = upload_meta.get("id")
        name = upload_meta.get("name")
        description = upload_meta.get("description")
        workspace_id = upload_meta.get("workspaceId")
        return _ExternalResultMetaData(id, name, description, workspace_id)

    def delete(self) -> None:
        self._sal.external_result.delete_uploaded_result(self._result_id)

    @classmethod
    def from_operation(
        cls, operation: BaseOperation[ExternalResult], **kwargs: Any
    ) -> ExternalResult:
        assert isinstance(operation, ExternalResultImportOperation)
        return cls(**kwargs, service=operation._sal)
