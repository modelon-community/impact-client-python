import os
import shutil

from tests.impact.client.helpers import IDs

# Setup of general paths:
_SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

_TEST_LIBRARIES_PATH = os.path.join(_SCRIPT_PATH, "test_libraries")
_TEST_WORKSPACES_PATH = os.path.join(_SCRIPT_PATH, "test_workspaces")
_TEST_PROJECTS_PATH = os.path.join(_SCRIPT_PATH, "test_projects")

# Paths for library files
SINGLE_FILE_LIBRARY_PATH = os.path.join(_TEST_LIBRARIES_PATH, "Single.mo")
TEST_WORKSPACE_PATH = os.path.join(_TEST_WORKSPACES_PATH, "Test.zip")


def get_archived_modelica_lib_path(base_path: str):
    return shutil.make_archive(
        os.path.join(base_path, "Dynamic"), "zip", _TEST_LIBRARIES_PATH, "Dynamic"
    )


def get_archived_workspace_path(base_path: str):
    return shutil.make_archive(
        os.path.join(base_path, IDs.WORKSPACE_ID_SECONDARY),
        "zip",
        os.path.join(_TEST_WORKSPACES_PATH, IDs.WORKSPACE_ID_SECONDARY),
    )


def get_archived_project_path(base_path: str):
    return shutil.make_archive(
        os.path.join(base_path, IDs.PROJECT_NAME_PRIMARY),
        "zip",
        os.path.join(_TEST_PROJECTS_PATH, IDs.PROJECT_NAME_PRIMARY),
    )
