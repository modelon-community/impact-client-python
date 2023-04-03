from __future__ import annotations
import enum
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Union, TYPE_CHECKING, Any

from modelon.impact.client.entities.model import Model
from modelon.impact.client.sal.service import Service
from modelon.impact.client.operations.content_import import ContentImportOperation

if TYPE_CHECKING:
    from modelon.impact.client.entities.workspace import Workspace
    from modelon.impact.client.operations.base import BaseOperation


logger = logging.getLogger(__name__)


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
        return Path(self._content['relpath'])

    @property
    def content_type(self) -> ContentType:
        """Type of content."""
        return ContentType(self._content['contentType'])

    @property
    def id(self) -> str:
        """Content ID."""
        return self._content['id']

    @property
    def name(self) -> Optional[str]:
        """Modelica library name."""
        return self._content.get('name')

    @property
    def default_disabled(self) -> str:
        return self._content['defaultDisabled']

    def delete(self) -> None:
        """Deletes a project content.

        Example::

            content.delete()

        """
        self._sal.project.project_content_delete(self._project_id, self.id)

    def upload_fmu(
        self,
        workspace: Workspace,
        fmu_path: str,
        class_name: Optional[str] = None,
        overwrite: bool = False,
        include_patterns: Optional[Union[str, List[str]]] = None,
        exclude_patterns: Optional[Union[str, List[str]]] = None,
        top_level_inputs: Optional[Union[str, List[str]]] = None,
        step_size: float = 0.0,
    ) -> Model:
        """Uploads a FMU to the workspace.

        Args:

            workspace:
                Workspace class object

            fmu_path:
                The path for the FMU to be imported.

            class_name:
                Qualified name of generated class. By default, 'class_name' is
                set to the name of the library followed by a name based
                on the filename of the imported FMU.

            overwrite:
                Determines if any already existing files should be overwritten.
                Default: False.

            include_patterns, exclude_patterns:
                Specifies what variables from the FMU to include and/or exclude in the
                wrapper model. These two arguments are patterns or lists of patterns as
                the same kind as the argument 'filter' for the function
                'get_model_variables' in PyFMI. If both 'include_patterns' and
                'exclude_patterns' are given, then all variables that matches
                'include_patterns' but does not match 'exclude_patterns' are included.
                Derivatives and variables with a leading underscore in the name are
                always excluded.
                Default value: None (which means to include all the variables).

            top_level_inputs:
                Specify what inputs that should be kept as inputs, i.e. with or without
                the input keyword. The argument is a pattern similar to the arguments
                include_patterns and exclude_patterns. Example: If
                top_level_inputs = 'my_inputs*', then all input variables matching the
                pattern 'my_inputs*' will be generated as inputs, and all other inputs
                not matching the pattern as model variables. If top_level_inputs = '',
                then no input is imported as an input.
                Default value: None (which means all inputs are kept as inputs)
                Type: str or a list of strings

            step_size:
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
        class_name = class_name or ".".join(
            [self.relpath.stem.split(' ')[0], os.path.split(fmu_path)[-1].strip('.fmu')]
        )
        resp = self._sal.project.fmu_upload(
            workspace.id,
            self._project_id,
            self.id,
            fmu_path,
            class_name,
            overwrite,
            include_patterns,
            exclude_patterns,
            top_level_inputs,
            step_size=step_size,
        )

        if resp["importWarnings"]:
            logger.warning(f"Import Warnings: {'. '.join(resp['importWarnings'])}")
        return Model(resp['fmuClassPath'], workspace.id, self._project_id, self._sal)

    @classmethod
    def from_operation(
        cls, operation: BaseOperation[ProjectContent], **kwargs: Any
    ) -> ProjectContent:
        assert isinstance(operation, ContentImportOperation)
        return cls(**kwargs, service=operation._sal)
