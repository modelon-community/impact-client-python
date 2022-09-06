#
# Copyright (c) 2022 Modelon AB
#
import enum
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from modelon.impact.client.options import (
    CompilerOptions,
    RuntimeOptions,
    SimulationOptions,
    SolverOptions,
)
from modelon.impact.client.entities.model import Model
from modelon.impact.client.sal.project import ProjectService
from modelon.impact.client.sal.workspace import WorkspaceService
from modelon.impact.client.sal.model_executable import ModelExecutableService

logger = logging.getLogger(__name__)
RepoURL = Union['GitRepoURL', 'SvnRepoURL']


@enum.unique
class ContentType(enum.Enum):
    """Supported content types in a project."""

    MODELICA = 'MODELICA'
    VIEWS = 'VIEWS'
    FAVOURITES = 'FAVOURITES'
    CUSTOM_FUNCTIONS = 'CUSTOM_FUNCTIONS'
    REFERENCE_RESULTS = 'REFERENCE_RESULTS'
    GENERIC = 'GENERIC'


@enum.unique
class ProjectType(enum.Enum):
    """Type of project."""

    LOCAL = 'LOCAL'
    RELEASED = 'RELEASED'
    SYSTEM = 'SYSTEM'


@dataclass
class GitRepoURL:
    """GitRepoURL represents a project referenced in a git repo
    String representation is url[@[refname][:sha1]]
    """

    url: str
    """ URL without protocol part, e.g., gitlab.modelon.com/group/project/repo """

    refname: str = ""
    """ Reference name (branch, tag or similar) """

    sha1: str = ""
    """ Commit hash """

    def __str__(self):
        repo_url = self.url
        if self.refname or self.sha1:
            repo_url += '@'
        if self.refname:
            repo_url += self.refname
        if self.sha1:
            repo_url += ':' + self.sha1
        return repo_url

    @classmethod
    def from_dict(cls, data):
        return cls(
            url=data.get("url"), refname=data.get("refname"), sha1=data.get("sha1"),
        )


@dataclass
class SvnRepoURL:
    """SvnRepoURL represents a project referenced in a Subversion repo
    String representation is url/trunk/subdir[@[rev]]
    """

    root_url: str
    """ URL without protocol part up to branch part, e.g., svn.modelon.com/PNNN/ """

    branch: str = ""
    """ Non-empty if it's standard layout and can be either
        trunk or branches/name or tags/name """

    url_from_root: str = ""
    """ URL segment after branch (could be saved in subdir as well) """

    rev: str = ""
    """ Revision number or empty (means HEAD) """

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
            return 'HEAD'
        return rev

    def __str__(self):
        segments = [self.root_url]
        if self.branch:
            segments.append(self.branch)
        if self.url_from_root:
            segments.append(self.url_from_root)
        repo_url = '/'.join(segments)
        if self.rev:
            repo_url += '@' + self.rev
        return repo_url

    @classmethod
    def from_dict(cls, data):
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

    def __str__(self):
        uri = f"{self.service_kind.lower()}+{self.protocol}://{self.repourl}"
        subdir = self.subdir
        if subdir not in ["", "."]:
            uri = uri + "#" + subdir
        return uri

    @classmethod
    def from_dict(cls, data):
        repo_url = data.get("repoUrl")
        service_kind = data.get("serviceKind")
        return cls(
            service_kind=service_kind,
            service_url=data.get("serviceUrl"),
            repourl=GitRepoURL.from_dict(repo_url)
            if service_kind.lower() == 'git'
            else SvnRepoURL.from_dict(repo_url),
            protocol=data.get("protocol"),
            subdir=data.get("subdir"),
        )


class ProjectContent:
    """Content entry in a project."""

    def __init__(
        self,
        content: Dict[str, str],
        project_id: str,
        project_service: ProjectService,
        workspace_service: WorkspaceService,
        model_executable_service: ModelExecutableService,
    ):
        self._content = content
        self._project_id = project_id
        self._project_sal = project_service
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_executable_service

    def __repr__(self):
        return f"Project content with id '{self.id}'"

    def __eq__(self, obj):
        return isinstance(obj, ProjectContent) and obj.id == self.id

    @property
    def relpath(self):
        """
        Relative path in the project. Can be file (e.g., SomeLib.mo) or folder
        """
        return self._content.get('relpath')

    @property
    def content_type(self) -> ContentType:
        """Type of content"""
        return ContentType(self._content.get('contentType'))

    @property
    def id(self):
        """Content ID."""
        return self._content['id']

    @property
    def name(self):
        """Modelica library name"""
        return self._content.get('name')

    @property
    def default_disabled(self):
        return self._content.get('defaultDisabled')

    def delete(self):
        """Deletes a project content.

        Example::

            content.delete()
        """
        self._project_sal.project_content_delete(self._project_id, self.id)

    def upload_fmu(
        self,
        workspace,
        fmu_path: str,
        library_path: str,
        class_name: Optional[str] = None,
        overwrite: bool = False,
        include_patterns: Optional[Union[str, List[str]]] = None,
        exclude_patterns: Optional[Union[str, List[str]]] = None,
        top_level_inputs: Optional[Union[str, List[str]]] = None,
        step_size: float = 0.0,
    ) -> Model:
        """Uploads a FMU to the workspace.

        Parameters:

            fmu_path --
                The path for the FMU to be imported.

            library_path --
                The library identifier, '{name} {version}' or '{name}' if version is
                missing.

            class_name --
                Qualified name of generated class. By default, 'class_name' is
                set to the name of the library followed by a name based
                on the filename of the imported FMU.

            overwrite --
                Determines if any already existing files should be overwritten.
                Default: False.

            include_patterns, exclude_patterns --
                Specifies what variables from the FMU to include and/or exclude in the
                wrapper model. These two arguments are patterns or lists of patterns as
                the same kind as the argument 'filter' for the function
                'get_model_variables' in PyFMI. If both 'include_patterns' and
                'exclude_patterns' are given, then all variables that matches
                'include_patterns' but does not match 'exclude_patterns' are included.
                Derivatives and variables with a leading underscore in the name are
                always excluded.
                Default value: None (which means to include all the variables).

            top_level_inputs --
                Specify what inputs that should be kept as inputs, i.e. with or without
                the input keyword. The argument is a pattern similar to the arguments
                include_patterns and exclude_patterns. Example: If
                top_level_inputs = 'my_inputs*', then all input variables matching the
                pattern 'my_inputs*' will be generated as inputs, and all other inputs
                not matching the pattern as model variables. If top_level_inputs = '',
                then no input is imported as an input.
                Default value: None (which means all inputs are kept as inputs)
                Type: str or a list of strings

            step_size --
                Specify what value to set for the parameter for step size in the
                generated model. By default the parameter is set to zero, which
                inturn means that the step size will be set during simulation based
                on simulation properties such as the time interval.
                This can also be manually set to any real non-negative number.
                The value of the step size parameter can also be set via the function
                set_step_size, which must be invoked before importing the model.
                Default value: 0.0 (which during simulation is set according to the
                description above).
                Type: number

        Example::
            workspace = client.get_workspace("test")
            content.upload_fmu(workspace, 'C:/A.fmu',"Test")
            content.upload_fmu(workspace, 'C:/B.fmu',"Test",class_name="Test.Model")
        """
        resp = self._project_sal.fmu_upload(
            workspace.id,
            self._project_id,
            self.id,
            fmu_path,
            library_path,
            class_name,
            overwrite,
            include_patterns,
            exclude_patterns,
            top_level_inputs,
            step_size=step_size,
        )

        if resp["importWarnings"]:
            logger.warning(f"Import Warnings: {'. '.join(resp['importWarnings'])}")

        return Model(
            resp['fmuClassPath'],
            workspace.id,
            self._workspace_sal,
            self._model_exe_sal,
        )


class ProjectDependency:
    """Dependency entry for a project"""

    def __init__(self, data):
        self._data = data

    @property
    def name(self):
        """The name of the project dependency"""
        return self._data.get('name')

    @property
    def version_specifier(self):
        """Version specifier"""
        return self._data.get('versionSpecifier')


class ProjectExecutionOptions:
    def __init__(self, data):
        self._data = data

    @property
    def custom_function(self):
        return self._data.get('customFunction')

    @property
    def compiler_options(self):
        return CompilerOptions(self._data.get("compiler"), self.custom_function)

    @property
    def runtime_options(self):
        return RuntimeOptions(self._data.get("runtime"), self.custom_function)

    @property
    def simulation_options(self):
        return SimulationOptions(self._data.get("simulation"), self.custom_function)

    @property
    def solver_options(self):
        return SolverOptions(self._data.get("solver"), self.custom_function)


class ProjectDefinition:
    """
    Impact project definition.
    """

    def __init__(self, data):
        self._data = data

    @property
    def name(self):
        return self._data.get("name")

    @property
    def version(self):
        return self._data.get("version")

    @property
    def format(self):
        return self._data.get("format")

    @property
    def dependencies(self):
        dependencies = self._data.get('dependencies', [])
        return [ProjectDependency(dependency) for dependency in dependencies]

    @property
    def content(self):
        return self._data.get('content', [])

    @property
    def execution_options(self):
        execution_options = self._data.get('executionOptions', [])
        return [
            ProjectExecutionOptions(execution_option)
            for execution_option in execution_options
        ]


class Project:
    """
    Class containing Project functionalities.
    """

    def __init__(
        self,
        project_id: str,
        project_definition: ProjectDefinition,
        project_type: ProjectType,
        vcs_uri: Optional[VcsUri],
        project_service: ProjectService,
        workspace_service: WorkspaceService,
        model_executable_service: ModelExecutableService,
    ):
        self._project_id = project_id
        self._project_definition = project_definition
        self._vcs_uri = vcs_uri or None
        self._project_type = project_type
        self._project_sal = project_service
        self._workspace_sal = workspace_service
        self._model_exe_sal = model_executable_service

    def __repr__(self):
        return f"Project with id '{self._project_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Project) and obj._project_id == self._project_id

    @property
    def id(self) -> str:
        """Project id"""
        return self._project_id

    @property
    def definition(self):
        return self._project_definition

    @property
    def vcs_uri(self) -> Optional[VcsUri]:
        """Project vcs uri"""
        return self._vcs_uri

    def delete(self):
        """Deletes a project.

        Example::

            project.delete()
        """
        self._project_sal.project_delete(self._project_id)

    def _get_project_content(self, content):
        return ProjectContent(
            content,
            self._project_id,
            self._project_sal,
            self._workspace_sal,
            self._model_exe_sal,
        )

    def get_contents(self) -> List[ProjectContent]:
        """Get project contents.

        Example::

            project.get_contents()
        """
        return [
            self._get_project_content(content)
            for content in self._project_definition.content
        ]

    def get_content_by_name(self, name: str) -> Optional[ProjectContent]:
        """Gets the first matching project content with the given name.

        Example::

            project.get_content_by_name(name)
        """
        contents = self.get_contents()
        for content in contents:
            if content.name == name:
                return content
        return None

    def upload_content(
        self, path_to_content: str, content_type: ContentType
    ) -> ProjectContent:
        """Upload content to a project.

        Parameters:

            path_to_content --
                The path for the content to be imported.

            content_type --
                The type of the imported content.

        Example::
            from modelon.impact.client import ContentType

            project.upload_content('/home/test.mo', ContentType.MODELICA)
        """
        resp = self._project_sal.project_content_upload(
            path_to_content, self._project_id, content_type.value
        )
        return self._get_project_content(resp)

    def upload_modelica_library(self, path_to_lib: str):
        """Uploads/adds a non-encrypted modelica library or a modelica model to the project.

        Parameters:

            path_to_lib --
                The path for the library to be imported. Only '.mo' or '.zip' file
                extension are supported for upload.

        Example::

            project.upload_model_library('C:/A.mo')
            project.upload_model_library('C:/B.zip')
        """
        if Path(path_to_lib).suffix.lower() not in ['.mo', '.zip']:
            raise ValueError(
                "Only '.mo' or '.zip' file extension are supported for uploading "
                "Modelica content into project."
            )
        return self.upload_content(path_to_lib, ContentType.MODELICA)
