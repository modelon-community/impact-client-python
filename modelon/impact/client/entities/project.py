from __future__ import annotations

import enum
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Union

from modelon.impact.client.entities.content import ContentType, ProjectContent
from modelon.impact.client.entities.custom_function import CustomFunction
from modelon.impact.client.operations.content_import import ContentImportOperation
from modelon.impact.client.operations.project_import import ProjectImportOperation
from modelon.impact.client.options import ProjectExecutionOptions
from modelon.impact.client.sal.service import Service

if TYPE_CHECKING:
    from modelon.impact.client.operations.base import BaseOperation

logger = logging.getLogger(__name__)
RepoURL = Union["GitRepoURL", "SvnRepoURL"]


@enum.unique
class ProjectType(enum.Enum):
    """Type of project."""

    LOCAL = "LOCAL"
    RELEASED = "RELEASED"
    SYSTEM = "SYSTEM"


@enum.unique
class StorageLocation(enum.Enum):
    """The storage location of the project."""

    APPMODE = "APPMODE"
    USERSPACE = "USERSPACE"
    SYSTEM = "SYSTEM"


@dataclass
class GitRepoURL:
    """GitRepoURL represents a project referenced in a git repository String
    representation is url[@[refname][:sha1]]"""

    url: str
    """URL without protocol part, e.g., gitlab.modelon.com/group/project/repository."""

    refname: str = ""
    """Reference name (branch, tag or similar)"""

    sha1: str = ""
    """Commit hash."""

    def __str__(self) -> str:
        repo_url = self.url
        if self.refname or self.sha1:
            repo_url += "@"
        if self.refname:
            repo_url += self.refname
        if self.sha1:
            repo_url += ":" + self.sha1
        return repo_url

    @classmethod
    def from_dict(cls, data: Any) -> GitRepoURL:
        return cls(
            url=data.get("url"), refname=data.get("refname"), sha1=data.get("sha1")
        )


@dataclass
class SvnRepoURL:
    """SvnRepoURL represents a project referenced in a Subversion repository String
    representation is url/trunk/subdir[@[rev]]"""

    root_url: str
    """URL without protocol part up to branch part, e.g., svn.modelon.com/PNNN/"""

    branch: str = ""
    """Non-empty if it's standard layout and can be either trunk or branches/name or
    tags/name."""

    url_from_root: str = ""
    """URL segment after branch (could be saved in subdir as well)"""

    rev: str = ""
    """Revision number or empty (means HEAD)"""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SvnRepoURL):
            return False
        return (
            self.get_rev() == other.get_rev()
            and self.root_url == other.root_url
            and self.branch == other.branch
            and self.url_from_root == other.url_from_root
        )

    def get_rev(self) -> str:
        rev = self.rev
        if rev == "":
            return "HEAD"
        return rev

    def __str__(self) -> str:
        segments = [self.root_url]
        if self.branch:
            segments.append(self.branch)
        if self.url_from_root:
            segments.append(self.url_from_root)
        repo_url = "/".join(segments)
        if self.rev:
            repo_url += "@" + self.rev
        return repo_url

    @classmethod
    def from_dict(cls, data: Any) -> SvnRepoURL:
        return cls(
            root_url=data.get("rootUrl"),
            branch=data.get("branch"),
            url_from_root=data.get("urlFromRoot"),
            rev=data.get("rev"),
        )


@dataclass
class VcsUri:
    service_kind: str
    service_url: str
    repourl: RepoURL
    protocol: str
    subdir: str

    def __str__(self) -> str:
        uri = f"{self.service_kind.lower()}+{self.protocol}://{self.repourl}"
        subdir = self.subdir
        if subdir not in ["", "."]:
            uri = uri + "#" + subdir
        return uri

    @classmethod
    def from_dict(cls, data: Any) -> VcsUri:
        repo_url = data.get("repoUrl")
        service_kind = data.get("serviceKind")
        return cls(
            service_kind=service_kind,
            service_url=data.get("serviceUrl"),
            repourl=GitRepoURL.from_dict(repo_url)
            if service_kind.lower() == "git"
            else SvnRepoURL.from_dict(repo_url),
            protocol=data.get("protocol"),
            subdir=data.get("subdir"),
        )


class ProjectDependency:
    """Dependency entry for a project."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def name(self) -> Optional[str]:
        """The name of the project dependency."""
        return self._data.get("name")

    @property
    def version_specifier(self) -> Optional[str]:
        """Version specifier."""
        return self._data.get("versionSpecifier")


class ProjectDefinition:
    """Impact project definition."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def version(self) -> Optional[str]:
        return self._data.get("version")

    @property
    def format(self) -> str:
        return self._data["format"]

    @property
    def dependencies(self) -> List[ProjectDependency]:
        dependencies = self._data.get("dependencies", [])
        return [ProjectDependency(dependency) for dependency in dependencies]

    @property
    def content(self) -> list:
        return self._data.get("content", [])

    @property
    def execution_options(self) -> List[ProjectExecutionOptions]:
        execution_options = self._data.get("executionOptions", [])
        return [
            ProjectExecutionOptions(
                execution_option, execution_option["customFunction"]
            )
            for execution_option in execution_options
        ]

    def to_dict(self) -> Dict[str, Any]:
        return self._data


class Project:
    """Class containing Project functionalities."""

    def __init__(
        self,
        project_id: str,
        project_type: Union[ProjectType, str],
        storage_location: Union[StorageLocation, str],
        vcs_uri: Optional[VcsUri],
        service: Service,
    ):
        self._project_id = project_id
        self._vcs_uri = vcs_uri or None
        self._project_type = (
            ProjectType(project_type) if isinstance(project_type, str) else project_type
        )
        self._storage_location = (
            StorageLocation(storage_location)
            if isinstance(storage_location, str)
            else storage_location
        )
        self._sal = service

    def __repr__(self) -> str:
        return f"Project with id '{self._project_id}'"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, Project) and obj._project_id == self._project_id

    @property
    def id(self) -> str:
        """Project id."""
        return self._project_id

    @property
    def name(self) -> str:
        """Project name."""
        return self.definition.name

    @property
    def size(self) -> float:
        """Project size in bytes."""
        return self._sal.project.project_get(self.id, vcs_info=False, size_info=True)[
            "size"
        ]

    @property
    def definition(self) -> ProjectDefinition:
        """Project definition."""
        definition = self._sal.project.project_get(
            project_id=self.id, size_info=False, vcs_info=False
        )["definition"]
        return ProjectDefinition(definition)

    @property
    def vcs_uri(self) -> Optional[VcsUri]:
        """Project vcs uri."""
        return self._vcs_uri

    @property
    def project_type(self) -> ProjectType:
        return self._project_type

    @property
    def storage_location(self) -> StorageLocation:
        return self._storage_location

    def rename(self, new_name: str) -> None:
        """Renames a project.

        Args:
            name: The new name for the project.

        Example::

            project.rename('renamed project')

        """
        prj_data = self._sal.project.project_get(
            project_id=self.id, vcs_info=False, size_info=False
        )
        prj_data["definition"]["name"] = new_name
        self._sal.project.project_put(self.id, prj_data)

    def delete(self) -> None:
        """Deletes a project.

        Example::

            project.delete()

        """
        self._sal.project.project_delete(self._project_id)

    def _get_project_content(self, content: Dict[str, str]) -> ProjectContent:
        return ProjectContent(content, self._project_id, self._sal)

    def get_contents(self) -> Iterable[ProjectContent]:
        """Get project contents.

        Example::

            project.get_contents()

        """
        return [
            self._get_project_content(content) for content in self.definition.content
        ]

    def get_content(self, content_id: str) -> ProjectContent:
        """Gets the project content with the given ID.

        Args:
            content_id: The ID of the workspace.

        Example::

            project.get_content("79sd8-3n2a4-e3t24")

        """
        resp = self._sal.project.project_content_get(self.id, content_id)
        return ProjectContent(resp, self.id, self._sal)

    def get_content_by_name(
        self, name: str, content_type: Optional[ContentType] = None
    ) -> Optional[ProjectContent]:
        """Gets the first matching project content with the given name.

        Args:
            name: The name of the content.

            content_type: The type of the project content.

        Example::

            from modelon.impact.client import ContentType
            project.get_content_by_name(name, ContentType.MODELICA)

        """
        contents = self.get_contents()
        if content_type:
            contents = (c for c in contents if c.content_type == content_type)
        try:
            return next(c for c in contents if c.name == name)
        except StopIteration:
            return None

    def get_modelica_library_by_name(self, name: str) -> Optional[ProjectContent]:
        """Gets the first matching Modelica library with the given name.

        Args:

            name: The Modelica library name.

        Example::

            project.get_content_by_name(name)

        """
        return self.get_content_by_name(name, ContentType.MODELICA)

    def import_content(
        self, path_to_content: str, content_type: ContentType
    ) -> ContentImportOperation:
        """Upload content to a project.

        Args:

            path_to_content: The path for the content to be imported.

            content_type: The type of the imported content.

        Example::

            from modelon.impact.client import ContentType

            project.import_content('/home/test.mo', ContentType.MODELICA).wait()

        """
        resp = self._sal.project.project_content_upload(
            path_to_content, self._project_id, content_type.value
        )
        return ContentImportOperation[ProjectContent](
            resp["data"]["location"], self._sal, ProjectContent.from_operation
        )

    def import_modelica_library(self, path_to_lib: str) -> ContentImportOperation:
        """Uploads/adds a non-encrypted Modelica library or a Modelica model to the
        project.

        Args:
            path_to_lib:
                The path for the library to be imported. Only '.mo' or '.zip' file
                extension are supported for upload.

        Example::

            content  = project.import_modelica_library('A.mo').wait()
            content  = project.import_modelica_library('B.zip').wait()

        """
        if Path(path_to_lib).suffix.lower() not in [".mo", ".zip"]:
            raise ValueError(
                "Only '.mo' or '.zip' file extension are supported for uploading "
                "Modelica content into project."
            )
        return self.import_content(path_to_lib, ContentType.MODELICA)

    def get_options(
        self, custom_function: CustomFunction, use_defaults: Optional[bool] = False
    ) -> ProjectExecutionOptions:
        """Get project execution option.

        Args:
            custom_function: The CustomFunction class object.
            use_defaults: If true, default options are used.

        Example::

            dynamic = workspace.get_custom_function('dynamic')
            project.get_options(dynamic)

        """
        if use_defaults:
            options = self._sal.project.project_default_options_get(
                custom_function._workspace_id, custom_function.name
            )
        else:
            options = self._sal.project.project_options_get(
                self._project_id, custom_function._workspace_id, custom_function.name
            )
        return ProjectExecutionOptions(options, custom_function.name)

    @classmethod
    def from_operation(
        cls, operation: BaseOperation[Project], **kwargs: Any
    ) -> Project:
        assert isinstance(operation, ProjectImportOperation)
        return cls(**kwargs, vcs_uri=None, service=operation._sal)
