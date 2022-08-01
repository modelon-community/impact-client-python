#
# Copyright (c) 2022 Modelon AB
#
import enum
from pathlib import Path
from typing import List, Dict
from modelon.impact.client.options import (
    CompilerOptions,
    RuntimeOptions,
    SimulationOptions,
    SolverOptions,
)
from modelon.impact.client.sal.project import ProjectService


@enum.unique
class ContentType(enum.Enum):
    """Supported content types in a project."""

    MODELICA = 'MODELICA'
    VIEWS = 'VIEWS'
    FAVOURITES = 'FAVOURITES'
    CUSTOM_FUNCTIONS = 'CUSTOM_FUNCTIONS'
    REFERENCE_RESULTS = 'REFERENCE_RESULTS'
    GENERIC = 'GENERIC'


class ProjectContent:
    """Content entry in a project."""

    def __init__(
        self, content: Dict[str, str], project_id: str, project_sal: ProjectService
    ):
        self._content = content
        self._project_id = project_id
        self._project_sal = project_sal

    def __repr__(self):
        return f"Project content with id '{self.id}'"

    def delete(self):
        """Deletes a project content.

        Example::

            content.delete()
        """
        self._project_sal.project_content_delete(self._project_id, self.id)

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
        return self._content.get('id')

    @property
    def name(self):
        """Modelica library name"""
        return self._content.get('name')

    @property
    def default_disabled(self):
        return self._content.get('defaultDisabled')


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
        project_service: ProjectService,
    ):
        self._project_id = project_id
        self._project_definition = project_definition
        self._project_sal = project_service

    def __repr__(self):
        return f"Project with id '{self._project_id}'"

    def __eq__(self, obj):
        return isinstance(obj, Project) and obj._project_id == self._project_id

    @property
    def id(self) -> str:
        """Project id"""
        return self._project_id

    def delete(self):
        """Deletes a project.

        Example::

            project.delete()
        """
        self._project_sal.project_delete(self._project_id)

    def _get_project_content(self, content):
        return ProjectContent(content, self._project_id, self._project_sal)

    def get_contents(self) -> List[ProjectContent]:
        """Get project contents.

        Example::

            project.get_contents()
        """
        return [
            self._get_project_content(content)
            for content in self._project_definition.content
        ]

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
