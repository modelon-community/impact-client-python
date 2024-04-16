import os
import shutil

# Setup of general paths:
_SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

_TEST_LIBRARIES_PATH = os.path.join(_SCRIPT_PATH, "test_libraries")
_TEST_WORKSPACE_PATH = os.path.join(_SCRIPT_PATH, "test_workspaces")

# Paths for library files
SINGLE_FILE_LIBRARY_PATH = os.path.join(_TEST_LIBRARIES_PATH, "Single.mo")
TEST_WORKSPACE_PATH = os.path.join(_TEST_WORKSPACE_PATH, "Test.zip")


def get_archived_modelica_lib_path(base_path: str):
    return shutil.make_archive(
        os.path.join(base_path, "Dynamic"), "zip", _TEST_LIBRARIES_PATH, "Dynamic"
    )
