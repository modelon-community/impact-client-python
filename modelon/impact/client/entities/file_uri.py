from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union
from urllib.parse import urlparse

from typing_extensions import assert_never


@enum.unique
class URISchema(enum.Enum):
    """Supported Version Control System services."""

    MODELICA = "MODELICA"
    IMPACT_ARTIFACT = "IMPACT-ARTIFACT"

    @classmethod
    def from_str(cls, value: str) -> URISchema:
        for member in cls:
            if member.value == value.upper():
                return member
        raise ValueError(f"Incorrect schema in URI: {value!r}")


@dataclass
class URI:
    schema: URISchema
    netloc: str
    path: str

    @classmethod
    def from_str(cls, uri_str: str) -> URI:
        """Parse URI str into this class instance.

        Args:
            uri_str (str): <scheme>://<netloc>/<path>

        Returns:
            URI: This class instance.

        """
        parsed_url = urlparse(uri_str)
        netloc = parsed_url.netloc
        scheme = parsed_url.scheme
        path = parsed_url.path.lstrip("/")
        uri_schema = URISchema.from_str(scheme)
        return cls(uri_schema, netloc, path)

    def __str__(self) -> str:
        return f"{self.schema.value.lower()}://{self.netloc}/{self.path}"


class FileURI(ABC):
    def __str__(self) -> str:
        return str(self.uri)

    @property
    @abstractmethod
    def uri(self) -> URI:
        """URI class."""
        raise NotImplementedError


class ModelicaResourceURI(FileURI):
    def __init__(self, library: str, resource_path: str) -> None:
        self._library = library
        self._resource_path = resource_path

    @property
    def uri(self) -> URI:
        return URI.from_str(f"modelica://{self._library}/{self._resource_path}")

    @classmethod
    def from_uri(cls, uri: URI) -> ModelicaResourceURI:
        return cls(uri.netloc, uri.path)


class CustomArtifactURI(FileURI):
    def __init__(self, experiment_id: str, case_id: str, artifact_id: str) -> None:
        self._experiment_id = experiment_id
        self._case_id = case_id
        self._artifact_id = artifact_id

    @property
    def uri(self) -> URI:
        return URI.from_str(
            f"impact-artifact://workspace/{self._experiment_id}/{self._case_id}/"
            f"{self._artifact_id}"
        )

    @classmethod
    def from_uri(cls, uri: URI) -> CustomArtifactURI:
        experiment_id, case_id, artifact_id = uri.path.split("/")
        return cls(experiment_id, case_id, artifact_id)


def get_resource_URI_from_str(
    uri_str: str,
) -> Union[ModelicaResourceURI, CustomArtifactURI]:
    file_uri = URI.from_str(uri_str)
    if file_uri.schema == URISchema.MODELICA:
        return ModelicaResourceURI.from_uri(file_uri)
    elif file_uri.schema == URISchema.IMPACT_ARTIFACT:
        return CustomArtifactURI.from_uri(file_uri)
    else:
        assert_never(file_uri.schema)
